from fastapi import APIRouter, Depends, HTTPException
from langchain.chat_models import init_chat_model
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from sqlalchemy import text
from sqlalchemy.orm import Session
import json

from app.utils import schemas
from app.config.database import get_db
from app.config.vector_store import vector_store
from app.utils.redis_utils import get_chat_history, append_to_chat_history

model = init_chat_model("gpt-4.1", model_provider="openai")

# Redis: mock user id for now
user_id = "12334245"

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def get_chat():
    chat_history = get_chat_history(user_id)
    return chat_history

@router.post("/")
def chat_response(user_input: schemas.ChatQuery, db: Session = Depends(get_db)):
    results = vector_store.search_schema(user_input.query, n_results=4)
    if not results:
        return {
            "response": {
                "type": "need_more_info",
                "text": "Sorry, I couldn't find any relevant schema information.",
            }
        }

    schema_context = "\n".join([f"{r['metadata']['schema']}, Description: {r['document']}" for r in results])

    prompt = f"""
You are 'Lark AI', an intelligent chatbot assistant integrated into an organization's dashboard.
Users will ask questions in **natural language**, and possibly ask **follow-up questions** based on earlier parts of the conversation.

Task:
- If it is a **generic question**, reply with a helpful message and set "type" as "generic".
- If it is a **question about organizational data**, analyze it and generate a valid SQL query and respond with "type" as "sql".
- If the query is **out of scope**, set "type": "out_of_scope" and reply appropriately.
- If you need **more information** to proceed, respond with "type": "need_more_info" and ask the user what you need.
- If you can **fully answer** the question based on the context, respond with "type": "generic" and provide a natural language response.

SQL Guidelines:
- Only generate valid SELECT SQL queries.
- Format dates in "DD-MM-YYYY" format.
- Select only relevant columns.
- Translate vague time expressions (e.g., "this quarter" → actual dates)
- Join tables when necessary.
- SQL should be compatible with Python SQLAlchemy and Postgres and ready to run via: db.execute(text(sql_query)) 

Error Handling & Accuracy Requirements:
1. **Spelling Flexibility**:
   - Tolerate minor spelling mistakes (e.g., "Softwear Engineer" → "Software Engineer")
   - Correct common abbreviations (e.g., "PM" → "Product Manager", "SE" → "Software Engineer")
   - For ambiguous terms, ask the user for clarification.

2. **Data Validation**:
   - Validate values such as known roles, departments, companies, or regions.
   - Reject impossible queries (e.g., "users from Mars").
   - Translate vague time expressions accurately (e.g., "this quarter", "last month").

3. **Edge Case Handling**:
   - Empty results are valid as long as the SQL is correct.
   - Warn the user if a query could return a very large result set.
   - Handle special characters in names and emails correctly.

Scope Constraints:
You must not respond to vague or out-of-scope queries like:
- "Show me *"
- "Find all things related to *"
- "What's trending now?"

Instead, respond with:
- "I'm sorry, I need more specific information to assist you."
- "This query appears to be outside the current scope of supported questions."

Schemas:
{schema_context}

Respond in JSON:
{{
    "type": "sql" | "generic" | "out_of_scope" | "need_more_info",
    "component": "table" | "text" | "number" | "pie_chart" | "bar_chart",
    "text": "Natural language explanation or response for UI display",
    "sql": "SELECT ..."
}}
"""


    messages = [SystemMessage(content=prompt)]
    chat_histoy = get_chat_history(user_id)
    
    # Add chat history to messages
    for message in chat_histoy:
        if message["role"] == "user":
            messages.append(HumanMessage(content=message["content"]))
        elif message["role"] == "assistant":
            messages.append(AIMessage(content= json.dumps(message["content"])))

    messages.append(HumanMessage(content=user_input.query))
    response = model(messages).content
    # print(response)

    try:
        data = json.loads(response)
        
        if data['type'] == 'sql':
            result = db.execute(text(data['sql']))
            rows = result.fetchall()
            columns = result.keys()
            result_data = [dict(zip(columns, row)) for row in rows]
            data["result"] = result_data

        # Store the chat history in Redis
        append_to_chat_history(user_id, {"role": "user", "content": user_input.query})
        append_to_chat_history(user_id, {"role": "assistant", "content": data})
        
        return {"response": data}

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Model response could not be parsed as JSON")


@router.get("/vectors/schemas")
def get_schemas(id: str = None):
    return vector_store.schema_collection.get(ids = id or None)

 
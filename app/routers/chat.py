from fastapi import APIRouter, Depends, HTTPException, Query
from langchain.chat_models import init_chat_model
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from sqlalchemy import text
from sqlalchemy.orm import Session
import json

from app.utils import schemas
from app.config.database import get_db
from app.config.vector_store import vector_store
from app.utils.prompt_utils import get_prompt, get_final_rag_prompt
from app.utils.redis_utils import get_chat_history, append_to_chat_history, clear_chat_history

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
def chat_response(
    user_input: schemas.ChatQuery,
    rag: bool = Query(False, description="Use RAG-based response"),
    db: Session = Depends(get_db)
):
    results = vector_store.search_schema(user_input.query, n_results=4)
    if not results:
        return {
            "response": [{"component": "text", "content": "Sorry, I couldn't find any relevant schema information."}]
        }

    schema_context = "\n".join([f"{r['metadata']['schema']}, Description: {r['document']}" for r in results])

    prompt = get_prompt(schema_context)

    messages = [SystemMessage(content=prompt)]
    chat_histoy = get_chat_history(user_id)
    
    # Add chat history to messages
    for message in chat_histoy:
        if message["role"] == "user":
            messages.append(HumanMessage(content=message["content"]))
        elif message["role"] == "assistant":
            messages.append(AIMessage(content= json.dumps(message["content"])))

    messages.append(HumanMessage(content=user_input.query))
    response = model.predict_messages(messages).content
    # print(response)

    try:
        data = json.loads(response)
        
        if data['type'] == 'sql':
            result = db.execute(text(data['sql']))
            rows = result.fetchall()
            columns = result.keys()
            result_data = [dict(zip(columns, row)) for row in rows]
            data = [
                {"component": "text", "content": data["text"] if len(result_data) else "Sorry, I couldn't find any relevant information."},
                {"component": data["component"], "content": result_data}
            ]
            
            if rag:
                rag_prompt = get_final_rag_prompt(user_input.query, data)
                # print(rag_prompt
                response = model.predict(text=rag_prompt)
                data = json.loads(response)
        else:
            data = [{"component": "text", "content": data["text"]}]

        # Store the chat history in Redis
        append_to_chat_history(user_id, {"role": "user", "content": user_input.query})
        append_to_chat_history(user_id, {"role": "assistant", "content": data})
        
        return {"response": data}

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Model response could not be parsed as JSON")

@router.post("/clear")
async def clear_chat():
    clear_chat_history(user_id)
    return {"message": "Chat history cleared"}

@router.get("/vectors/schemas")
def get_schemas(id: str = None):
    return vector_store.schema_collection.get(ids = id or None)

 
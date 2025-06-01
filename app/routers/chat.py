from fastapi import APIRouter, Depends, HTTPException
from langchain.chat_models import init_chat_model
from langchain.schema import SystemMessage, HumanMessage
from sqlalchemy import text
from sqlalchemy.orm import Session
import json

from app.config import schemas
from app.config.database import get_db
from app.config.vector_store import vector_store

model = init_chat_model("gpt-4.1-mini", model_provider="openai")

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def get_chat():
    return {"message": "Hello, How can I help you today?"}

@router.post("/")
def chat_response(user_input: schemas.ChatQuery, db: Session = Depends(get_db)):
    results = vector_store.search_schema(user_input.query, n_results=3)

    if not results:
        return {
            "response": {
                "type": "need_more_info",
                "component": "text",
                "text": "Sorry, I couldn't find any relevant schema information.",
                "sql": None
            }
        }

    schema_context = "\n".join([f"{r['document']}" for r in results])

    prompt = f"""
        You are a SQL expert. Generate a valid SELECT SQL query based on the following schemas:

        {schema_context}

        User question: "{user_input.query}"

        Respond in JSON:
        {{
            "type": "sql" | "generic" | "out_of_scope" | "need_more_info",
            "text": "Natural language explanation or response for UI display",
            "sql": "SELECT ..."
        }}
    """

    messages = [
        SystemMessage(content="You are a helpful assistant that writes SQL."),
        HumanMessage(content=prompt)
    ]

    response = model(messages).content

    try:
        data = json.loads(response)

        if data['type'] == 'sql':
            result = db.execute(text(data['sql']))
            rows = result.fetchall()
            columns = result.keys()
            result_data = [dict(zip(columns, row)) for row in rows]
            data["result"] = result_data
            return {"response": data}
        else:
            return {"response": data}

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Model response could not be parsed as JSON")


@router.get("/vectors/schemas")
def get_schemas(id: str = None):
    return vector_store.schema_collection.get(ids = id or None)


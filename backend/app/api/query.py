from fastapi import APIRouter, Request
from sqlalchemy import create_engine
import pandas as pd

from app.services.gemini_service import generate_sql, generate_answer

router = APIRouter()

engine = create_engine("sqlite:///./business.db")


@router.post("/query")
async def query_data(request: Request):
    # ---------------- READ BODY ----------------
    try:
        data = await request.json()
    except:
        return {"error": "Invalid JSON body"}

    question = data.get("question")

    if not question:
        return {"error": "Please provide 'question'"}

    schema = "Table: invoices(id, customer_id, totalnetamount)"

    # ---------------- GENERATE SQL ----------------
    try:
        sql = generate_sql(question, schema)
    except Exception as e:
        return {"error": f"SQL generation failed: {str(e)}"}

    # ---------------- GUARDRAIL ----------------
    if sql == "INVALID":
        return {
            "answer": "This system is designed to answer questions related to the provided dataset only."
        }

    # ---------------- VALIDATE SQL ----------------
    if not sql.strip().lower().startswith("select"):
        return {
            "error": "Only SELECT queries allowed",
            "sql": sql
        }

    # ---------------- EXECUTE SQL ----------------
    try:
        df = pd.read_sql(sql, engine)
    except Exception as e:
        return {
            "error": f"SQL execution failed: {str(e)}",
            "sql": sql
        }

    result = df.head(10).to_dict(orient="records")

    # ---------------- GENERATE ANSWER ----------------
    try:
        answer = generate_answer(question, sql, result)
    except:
        answer = f"Query executed successfully. Returned {len(result)} rows."

    # ---------------- RESPONSE ----------------
    return {
        "question": question,
        "sql": sql,
        "result": result,
        "answer": answer
    }
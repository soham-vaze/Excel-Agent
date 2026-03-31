from llm.ollama import call_ollama_json
from llm.prompt import INTENT_PROMPT
from agent.schemas import Intent
from tools.excel_tools import setup_excel, get_headers


def build_prompt(user_input: str) -> str:
    headers = setup_excel()
    column_names = get_headers(headers)

    return f"""
You are an Excel assistant.

Available columns:
{column_names}

Instructions:
- Always use column names EXACTLY as provided above
- Do NOT invent column names
- Convert user query into JSON

{INTENT_PROMPT}

User: {user_input}

Return ONLY JSON:
"""

def parse_intent(user_input: str) -> Intent | None:
    prompt = build_prompt(user_input)

    response = call_ollama_json(prompt)

    if not response:
        print("❌ Empty or invalid LLM response")
        return None

    try:
        intent = Intent(**response)
        return intent
    except Exception as e:
        print("❌ Intent validation failed:", e)
        print("RAW:", response)
        return None
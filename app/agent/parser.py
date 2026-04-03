from llm.ollama import call_ollama_json
from llm.prompt import INTENT_PROMPT
from agent.schemas import Intent
from tools.excel_tools import setup_excel, get_headers


def build_prompt(user_input: str,graph_token,drive_id,item_id) -> str:
    headers, base_url = setup_excel(graph_token,drive_id,item_id)
    column_names = get_headers(headers)

    return f"""
You are an Excel assistant.

Available columns:
{column_names}

Instructions:
- Always use column names EXACTLY as provided above
- What is status for task wth requirement reference MID-16-1?
- Do NOT invent column names
- Convert user query into JSON

{INTENT_PROMPT}

User: {user_input}

Return ONLY JSON:
""" 

def parse_intent(user_input: str,graph_token,drive_id,item_id) -> Intent | None:
    prompt = build_prompt(user_input,graph_token,drive_id,item_id)

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
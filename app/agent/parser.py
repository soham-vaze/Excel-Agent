from llm.ollama import call_ollama_json
from llm.prompt import INTENT_PROMPT
from agent.schemas import Intent


def build_prompt(user_input: str) -> str:
    return f"""
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
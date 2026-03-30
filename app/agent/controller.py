from agent.parser import parse_intent
from tools.excel_tools import get_row_tool


def run_agent(user_input: str):
    print(f"\n🧠 User Input: {user_input}")

    intent = parse_intent(user_input)

    if not intent:
        return "❌ Could not understand request"

    print(f"📦 Parsed Intent: {intent}")

    # 🔀 Routing
    if intent.action == "get_rows":
        return get_row_tool(intent)

    else:
        return f"❌ Unsupported action: {intent.action}"
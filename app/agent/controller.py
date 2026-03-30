from agent.parser import parse_intent
from tools.excel_tools import get_row_tool, add_column_tool


def run_agent(user_input: str):
    print(f"\n🧠 User Input: {user_input}")

    intent = parse_intent(user_input)

    if not intent:
        return "❌ Could not understand request"

    print(f"📦 Parsed Intent: {intent}")

    # 🔀 Routing logic
    if intent.action == "get_row":
        return get_row_tool(intent)

    elif intent.action == "add_column":
        return add_column_tool(intent)

    else:
        return f"❌ Unknown action: {intent.action}"
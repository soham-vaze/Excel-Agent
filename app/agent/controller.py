from agent.parser import parse_intent
from tools.excel_tools import (
    get_row_tool,
    add_row_tool,
    add_column_tool,
    read_cell_tool,
    count_rows_tool,
    filter_column_tool,
    aggregate_column_tool,
    update_cell_tool,
    explain_task_tool
)


def run_agent(user_input: str,graph_token:str):
    print(f"\n🧠 User Input: {user_input}")

    intent = parse_intent(user_input,graph_token)

    if not intent:
        return "❌ Could not understand request"

    print(f"📦 Parsed Intent: {intent}")

    if intent.action == "get_rows":
        return get_row_tool(intent,graph_token)

    elif intent.action == "add_row":
        return add_row_tool(intent,graph_token)

    elif intent.action == "add_column":
        return add_column_tool(intent,graph_token)

    elif intent.action == "read_cell":
        return read_cell_tool(intent,graph_token)
    
    elif intent.action == "count_rows":
        return count_rows_tool(intent,graph_token)

    elif intent.action == "filter_column":
        return filter_column_tool(intent,graph_token)
    elif intent.action == "aggregate_column":
        return aggregate_column_tool(intent,graph_token)
    elif intent.action == "update_cell":
        return update_cell_tool(intent,graph_token)
    elif intent.action == "explain_task":
        return explain_task_tool(intent, graph_token)
    else:
        return f"❌ Unknown action: {intent.action}"
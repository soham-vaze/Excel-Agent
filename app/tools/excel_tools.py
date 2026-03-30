from tools.graph_tools import create_session, get_tables, get_rows, add_row
from auth.auth import get_delegated_token
from utils.helpers import match_value

# 🔥 CONFIG (you can later move to config file)
DRIVE_ID = "b!cBQeHIOjTUyKfCgiQU2fgYLJ3o0sOOZPr6n4euCpEUmFH-YD-1qBQrKLtih9OujQ"
FILE_ID = "01I4F6FAUMCZQBWCKFAVA3IX3JDEDE4K4B"


def setup_excel():
    token = get_delegated_token()

    session_id = create_session(token, DRIVE_ID, FILE_ID)

    headers = {
        "Authorization": f"Bearer {token}",
        "workbook-session-id": session_id
    }

    tables = get_tables(headers, DRIVE_ID, FILE_ID)

    if not tables.get("value"):
        raise Exception("No tables found in Excel")

    table_id = tables["value"][0]["id"]

    return headers, table_id


# ✅ GET ROW TOOL (REAL)
def get_row_tool(intent):
    headers, table_id = setup_excel()

    data = get_rows(headers, DRIVE_ID, FILE_ID, table_id)

    rows = data.get("value", [])

    for row in rows:
        values = row["values"][0]

        # Assuming first column = name
        if match_value(values[0], intent.filter.get("name")):
            # Assuming second column = id
            return values[1]

    return "❌ Not found"


# ✅ ADD ROW TOOL (REAL)
def add_row_tool(intent):
    headers, table_id = setup_excel()

    values = list(intent.values.values())

    res = add_row(headers, DRIVE_ID, FILE_ID, table_id, values)

    return "✅ Row added successfully"
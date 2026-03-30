from auth.auth import get_delegated_token
from tools.graph_tools import create_session, get_rows, get_columns
from utils.helpers import build_column_map
from utils.logger import log
import os
# 🔹 CONFIG (replace with your values)
DRIVE_ID = os.getenv("DRIVE_ID")
ITEM_ID = os.getenv("EXCEL_FILE_ID")
TABLE_ID = os.getenv("TABLE_ID")

BASE_URL = f"https://graph.microsoft.com/v1.0/drives/{DRIVE_ID}/items/{ITEM_ID}"


def setup_excel():
    token = get_delegated_token()

    headers = {
        "Authorization": f"Bearer {token}"
    }

    headers = create_session(BASE_URL, headers)

    return headers


def get_headers(headers):
    data = get_columns(BASE_URL, TABLE_ID, headers)

    columns = data.get("value", [])
    header_names = [col["name"] for col in columns]

    log("Headers", header_names)

    return header_names


def get_all_rows(headers):
    data = get_rows(BASE_URL, TABLE_ID, headers)

    rows = data.get("value", [])
    values = [row["values"][0] for row in rows]

    log("Rows", values)

    return values


# =========================
# 🎯 TOOL: GET ROW
# =========================
def get_row_tool(intent):
    
    headers = setup_excel()

    header_names = get_headers(headers)
    rows = get_all_rows(headers)

    column_map = build_column_map(header_names)

    log("Column Map", column_map)

    if not intent.column:
        return "❌ Column not specified in query"

    if not intent.filter:
        return "❌ Filter condition missing"

    # Extract intent
    filter_key = list(intent.filter.keys())[0].lower()
    filter_value = intent.filter[filter_key]
    target_column = intent.column.lower()

    if filter_key not in column_map:
        return f"❌ Column '{filter_key}' not found"

    if target_column not in column_map:
        return f"❌ Column '{target_column}' not found"

    filter_idx = column_map[filter_key]
    target_idx = column_map[target_column]

    for row in rows:
        if str(row[filter_idx]).lower() == str(filter_value).lower():
            return row[target_idx]

    return "❌ Not found"
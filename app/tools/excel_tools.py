from auth.auth import get_delegated_token, get_valid_token
from tools.graph_tools import create_session, get_rows, get_columns
from utils.helpers import build_column_map
from utils.logger import log
from tools.graph_tools import add_row_api
from tools.graph_tools import add_column_api
import requests
import os
# 🔹 CONFIG (replace with your values)
DRIVE_ID = os.getenv("DRIVE_ID")
ITEM_ID = os.getenv("EXCEL_FILE_ID")
TABLE_ID = os.getenv("TABLE_ID")

BASE_URL = f"https://graph.microsoft.com/v1.0/drives/{DRIVE_ID}/items/{ITEM_ID}"


def setup_excel():
    token = get_valid_token()

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

    # log("Rows", values)

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


def add_row_tool(intent):
    headers = setup_excel()

    header_names = get_headers(headers)
    column_map = build_column_map(header_names)

    values_dict = intent.values

    if not values_dict:
        return "❌ No values provided"

    # Build row in correct order
    row = [None] * len(header_names)

    for key, value in values_dict.items():
        key = key.lower()

        if key not in column_map:
            return f"❌ Column '{key}' not found"

        idx = column_map[key]
        row[idx] = value

    res = add_row_api(BASE_URL, TABLE_ID, headers, row)

    return "✅ Row added successfully"


def add_column_tool(intent):
    token = get_valid_token()

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # =========================
    # 1️⃣ Create session
    # =========================
    session_url = f"{BASE_URL}/drives/{DRIVE_ID}/items/{ITEM_ID}/workbook/createSession"

    session_res = requests.post(
        session_url,
        headers=headers,
        json={"persistChanges": True}
    )

    session_id = session_res.json().get("id")
    headers["workbook-session-id"] = session_id

    # =========================
    # 2️⃣ Get current headers
    # =========================
    header_url = f"{BASE_URL}/drives/{DRIVE_ID}/items/{ITEM_ID}/workbook/tables/{TABLE_ID}/headerRowRange"

    res = requests.get(header_url, headers=headers)
    header_values = res.json()["values"][0]

    # =========================
    # 3️⃣ Add new column name
    # =========================
    new_column = intent.column_name

    if new_column in header_values:
        return f"⚠️ Column '{new_column}' already exists"

    updated_headers = header_values + [new_column]

    # =========================
    # 4️⃣ Update header row
    # =========================
    update_header_url = f"{BASE_URL}/drives/{DRIVE_ID}/items/{ITEM_ID}/workbook/tables/{TABLE_ID}/headerRowRange"

    requests.patch(
        update_header_url,
        headers=headers,
        json={"values": [updated_headers]}
    )

    # =========================
    # 5️⃣ Get all rows
    # =========================
    rows_url = f"{BASE_URL}/drives/{DRIVE_ID}/items/{ITEM_ID}/workbook/tables/{TABLE_ID}/rows"

    res = requests.get(rows_url, headers=headers)
    rows_data = res.json().get("value", [])

    default_val = intent.default_value

    # =========================
    # 6️⃣ Update each row
    # =========================
    for row in rows_data:
        row_values = row["values"][0]

        # append default OR None
        if default_val is not None:
            row_values.append(default_val)
        else:
            row_values.append(None)

        update_row_url = f"{BASE_URL}/drives/{DRIVE_ID}/items/{ITEM_ID}/workbook/tables/{TABLE_ID}/rows/{row['index']}"

        requests.patch(
            update_row_url,
            headers=headers,
            json={"values": [row_values]}
        )

    # =========================
    # ✅ Done
    # =========================
    if default_val is not None:
        return f"✅ Column '{new_column}' added with default '{default_val}'"
    else:
        return f"✅ Column '{new_column}' added (empty)"

def read_cell_tool(intent):
    headers = setup_excel()

    rows = get_all_rows(headers)

    if intent.row is None or intent.column_index is None:
        return "❌ Row or column index missing"

    row_idx = intent.row - 1
    col_idx = intent.column_index - 1

    try:
        return rows[row_idx][col_idx]
    except Exception:
        return "❌ Invalid row/column index"
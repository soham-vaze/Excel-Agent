from auth.auth import get_valid_token
from tools.graph_tools import create_session, get_rows, get_columns, add_row_api
from utils.helpers import build_column_map
from utils.logger import log
import requests
import os

# 🔹 CONFIG
DRIVE_ID = os.getenv("DRIVE_ID")
ITEM_ID = os.getenv("EXCEL_FILE_ID")
TABLE_ID = os.getenv("TABLE_ID")

BASE_URL = f"https://graph.microsoft.com/v1.0/drives/{DRIVE_ID}/items/{ITEM_ID}"


# =========================
# 🔧 SETUP
# =========================
def setup_excel():
    token = get_valid_token()

    headers = {
        "Authorization": f"Bearer {token}"
    }

    headers = create_session(BASE_URL, headers)
    return headers


# =========================
# 📊 HELPERS
# =========================
def get_headers(headers):
    data = get_columns(BASE_URL, TABLE_ID, headers)
    columns = data.get("value", [])
    return [col["name"] for col in columns]


def get_all_rows(headers):
    data = get_rows(BASE_URL, TABLE_ID, headers)
    rows = data.get("value", [])

    values = [row["values"][0] for row in rows]
    return values


def get_all_rows_dict(headers):
    header_names = get_headers(headers)
    column_map = build_column_map(header_names)

    rows = get_all_rows(headers)

    result = []
    for row in rows:
        row_dict = {}
        for col, idx in column_map.items():
            row_dict[col] = row[idx] if idx < len(row) else None
        result.append(row_dict)

    return result


# =========================
# 🎯 TOOL: GET ROW
# =========================
def get_row_tool(intent):
    headers = setup_excel()

    header_names = get_headers(headers)
    rows = get_all_rows(headers)
    column_map = build_column_map(header_names)

    if not intent.column or not intent.filter:
        return "❌ Missing column or filter"

    filter_key = list(intent.filter.keys())[0].lower()
    filter_value = intent.filter[filter_key]
    target_column = intent.column.lower()

    if filter_key not in column_map:
        return f"❌ Column '{filter_key}' not found"

    if target_column not in column_map:
        return f"❌ Column '{target_column}' not found"

    for row in rows:
        if str(row[column_map[filter_key]]).lower() == str(filter_value).lower():
            return row[column_map[target_column]]

    return "❌ Not found"


# =========================
# ➕ TOOL: ADD ROW
# =========================
def add_row_tool(intent):
    headers = setup_excel()

    header_names = get_headers(headers)
    column_map = build_column_map(header_names)

    values_dict = intent.values

    if not values_dict:
        return "❌ No values provided"

    row = [None] * len(header_names)

    for key, value in values_dict.items():
        key = key.lower()

        if key not in column_map:
            return f"❌ Column '{key}' not found"

        row[column_map[key]] = value

    add_row_api(BASE_URL, TABLE_ID, headers, row)

    return "✅ Row added"


# =========================
# ➕ TOOL: ADD COLUMN
# =========================
def add_column_tool(intent):
    headers = setup_excel()

    column_name = intent.column_name
    default_value = getattr(intent, "default_value", None)

    # Add column
    url = f"{BASE_URL}/workbook/tables/{TABLE_ID}/columns/add"

    res = requests.post(
        url,
        headers=headers,
        json={"name": column_name}
    )

    if res.status_code not in [200, 201]:
        return f"❌ Failed: {res.text}"

    # Fill default values
    if default_value is not None:
        rows = get_all_rows(headers)
        header_names = get_headers(headers)
        column_map = build_column_map(header_names)

        col_idx = column_map[column_name.lower()]

        for i, row in enumerate(rows):
            row[col_idx] = default_value

            update_url = f"{BASE_URL}/workbook/tables/{TABLE_ID}/rows/{i}"

            requests.patch(
                update_url,
                headers=headers,
                json={"values": [row]}
            )

    return f"✅ Column '{column_name}' added"


# =========================
# 📖 TOOL: READ CELL
# =========================
def read_cell_tool(intent):
    headers = setup_excel()
    rows = get_all_rows(headers)

    try:
        return rows[intent.row - 1][intent.column_index - 1]
    except:
        return "❌ Invalid row/column index"


# =========================
# 🔢 TOOL: COUNT ROWS
# =========================
def count_rows_tool(intent):
    headers = setup_excel()
    rows = get_all_rows_dict(headers)

    count = 0

    for row in rows:
        match = True

        if intent.filter:
            for key, value in intent.filter.items():
                if str(row.get(key.lower(), "")).lower() != str(value).lower():
                    match = False
                    break

        if match:
            count += 1

    return f"✅ Count: {count}"


# =========================
# 📊 TOOL: FILTER COLUMN
# =========================
def filter_column_tool(intent):
    headers = setup_excel()
    rows = get_all_rows_dict(headers)

    result = []

    for row in rows:
        match = True

        if intent.filter:
            for key, value in intent.filter.items():
                if str(row.get(key.lower(), "")).lower() != str(value).lower():
                    match = False
                    break

        if match:
            result.append(row.get(intent.column.lower()))

    if not result:
        return "❌ No matching data"

    return result[:20]
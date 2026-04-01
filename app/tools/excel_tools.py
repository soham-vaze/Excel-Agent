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
def setup_excel(graph_token):
    headers = {
        "Authorization": f"Bearer {graph_token}",
        "Content-Type": "application/json"
    }
    # If create_session adds specific workbook session IDs, keep it
    # Otherwise, this simple header is often enough for Graph
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
def get_row_tool(intent,graph_token):
    headers = setup_excel(graph_token)

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
def add_row_tool(intent,graph_token):
    headers = setup_excel(graph_token)

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
def get_excel_column_letter(n):
    result = ""
    while n >= 0:
        result = chr(n % 26 + 65) + result
        n = n // 26 - 1
    return result

# def add_column_tool(intent):
#     headers = setup_excel()

#     column_name = intent.column_name
#     default_value = intent.default_value

#     if not column_name:
#         return "❌ Column name missing"

#     # =========================
#     # 1️⃣ Get existing columns
#     # =========================
#     header_names = get_headers(headers)
#     column_map = build_column_map(header_names)

#     if column_name.lower() in column_map:
#         return f"⚠️ Column '{column_name}' already exists"

#     # =========================
#     # 2️⃣ Create column (Graph API)
#     # =========================
#     url = f"{BASE_URL}/workbook/tables/{TABLE_ID}/columns/add"

#     payload = {
#         "name": column_name
#     }

#     res = requests.post(url, headers=headers, json=payload)

#     if res.status_code not in [200, 201]:
#         return f"❌ Failed to create column: {res.text}"

#     log("Column Created", column_name)

#     # =========================
#     # 3️⃣ Fill default values (if provided)
#     # =========================
#     if default_value is not None:

#     # Refresh headers
#         header_names = get_headers(headers)
#         column_map = build_column_map(header_names)

#         new_col_key = column_name.lower()
#         new_col_idx = column_map[new_col_key]

#         rows_data = get_rows(BASE_URL, TABLE_ID, headers).get("value", [])

#         for i, row in enumerate(rows_data):

#             # Excel uses A1 notation → convert column index
#             col_letter = get_excel_column_letter(new_col_idx)  # A, B, C...
#             cell_address = f"{col_letter}{i + 2}"  # +2 because header is row 1

#             range_url = f"{BASE_URL}/workbook/worksheets('Sheet1')/range(address='{cell_address}')"

#             requests.patch(
#                 range_url,
#                 headers=headers,
#                 json={
#                     "values": [[default_value]]
#                 }
#             )

#     return f"✅ Column '{column_name}' added with default '{default_value}'"

def add_column_tool(intent,graph_token):
    headers = setup_excel(graph_token)

    column_name = intent.column_name
    default_value = intent.default_value
    position = intent.position
    ref_col = intent.reference_column

    header_names = get_headers(headers)
    rows = get_all_rows(headers)

    column_map = build_column_map(header_names)

    # Step 1: Add column normally (at end)
    url = f"{BASE_URL}/workbook/tables/{TABLE_ID}/columns/add"
    res = requests.post(url, headers=headers, json={"name": column_name})

    if res.status_code not in [200, 201]:
        return "❌ Failed to create column"

    # Step 2: If no positioning needed → normal flow
    if not position or not ref_col:
        return "✅ Column added"

    # Step 3: Re-fetch updated headers
    header_names = get_headers(headers)
    column_map = build_column_map(header_names)

    new_col = find_best_column(column_map, column_name)
    ref_col = find_best_column(column_map, ref_col)

    if not ref_col:
        return f"❌ Reference column '{intent.reference_column}' not found"

    new_idx = column_map[new_col]
    ref_idx = column_map[ref_col]

    # Step 4: Decide new position
    if position == "left":
        target_idx = ref_idx
    else:
        target_idx = ref_idx + 1

    # Step 5: Reorder headers
    headers_new = header_names.copy()
    col_name_actual = headers_new.pop(new_idx)
    headers_new.insert(target_idx, col_name_actual)

    # Step 6: Reorder rows
    updated_rows = []
    for row in rows:
        val = default_value if default_value else None
        row.append(val)

        item = row.pop(new_idx)
        row.insert(target_idx, item)

        updated_rows.append(row)

    # Step 7: Rewrite entire table (IMPORTANT)
    range_url = f"{BASE_URL}/workbook/tables/{TABLE_ID}/range"

    requests.patch(
        range_url,
        headers=headers,
        json={"values": [headers_new] + updated_rows}
    )

    return f"✅ Column '{column_name}' added {position} of '{ref_col}'"

# =========================
# 📖 TOOL: READ CELL
# =========================
def read_cell_tool(intent,graph_token):
    headers = setup_excel(graph_token)
    rows = get_all_rows(headers)

    try:
        return rows[intent.row - 1][intent.column_index - 1]
    except:
        return "❌ Invalid row/column index"


# =========================
# 🔢 TOOL: COUNT ROWS
# =========================
def count_rows_tool(intent,graph_token):
    headers = setup_excel(graph_token)
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

def find_best_column(column_map, target):
    target = normalize(target)

    for col in column_map:
        if normalize(col) == target:
            print(f"Founf best column {col}")
            return col

    return None

def normalize(text):
    return text.lower().replace("_", " ").strip()


# =========================
# 📊 TOOL: FILTER COLUMN
# =========================
# def filter_column_tool(intent):
#     headers = setup_excel()

#     # ✅ Step 1: Get headers + rows
#     header_names = get_headers(headers)
#     rows = get_all_rows_dict(headers)

#     # ✅ Step 2: Build column map
#     column_map = build_column_map(header_names)

#     # ✅ Step 3: Resolve target column
#     target_column = find_best_column(column_map, intent.column)

#     if not target_column:
#         return f"❌ Column '{intent.column}' not found"

#     result = []

#     # ✅ Step 4: Iterate rows
#     for row in rows:
#         match = True

#         if intent.filter:
#             for key, value in intent.filter.items():
#                 mapped_key = find_best_column(column_map, key)

#                 if not mapped_key:
#                     return f"❌ Column '{key}' not found"

#                 if str(row.get(mapped_key, "")).lower() != str(value).lower():
#                     match = False
#                     break

#         if match:
#             val = row.get(target_column)
#             if val is not None:
#                 result.append(val)

#     if not result:
#         return "❌ No matching data"

#     return result[:20]  

def filter_column_tool(intent,graph_token):
    headers = setup_excel(graph_token)

    # Step 1: Get headers + rows
    header_names = get_headers(headers)
    rows = get_all_rows_dict(headers)

    column_map = build_column_map(header_names)

    # Step 2: Resolve target column
    target_column = find_best_column(column_map, intent.column)

    if not target_column:
        return f"❌ Column '{intent.column}' not found"

    results = []

    # Step 3: Iterate rows
    for row in rows:
        match = True

        if intent.filter:
            for key, value in intent.filter.items():
                mapped_key = find_best_column(column_map, key)

                if not mapped_key:
                    return f"❌ Column '{key}' not found"

                cell_value = str(row.get(mapped_key, "")).strip().lower()
                filter_value = str(value).strip().lower()

                if cell_value != filter_value:
                    match = False
                    break

        if match:
            val = row.get(target_column)

            # ✅ IMPORTANT: ignore empty / None
            if val not in [None, "", "nan"]:
                results.append(val)

    if not results:
        return "❌ No matching data"

    return results

def aggregate_column_tool(intent,graph_token):
    headers = setup_excel(graph_token)

    # Step 1: Get headers + rows
    header_names = get_headers(headers)
    rows = get_all_rows_dict(headers)

    column_map = build_column_map(header_names)

    # Step 2: Resolve column
    target_column = find_best_column(column_map, intent.column)

    if not target_column:
        return f"❌ Column '{intent.column}' not found"

    freq = {}

    # Step 3: Count frequencies
    for row in rows:
        val = row.get(target_column)

        if val in [None, "", "nan"]:
            continue

        val = str(val).strip()

        if val not in freq:
            freq[val] = 0

        freq[val] += 1

    if not freq:
        return "❌ No data found"

    return freq

def update_cell_tool(intent,graph_token):
    headers = setup_excel(graph_token)

    header_names = get_headers(headers)
    column_map = build_column_map(header_names)

    rows_data = get_rows(BASE_URL, TABLE_ID, headers).get("value", [])

    if not intent.column or not intent.filter or not intent.value:
        return "❌ Missing column/filter/value"

    # ✅ Normalize columns
    target_column = find_best_column(column_map, intent.column)

    filter_key = list(intent.filter.keys())[0]
    filter_value = intent.filter[filter_key]

    filter_column = find_best_column(column_map, filter_key)

    if not target_column or not filter_column:
        return "❌ Column not found"

    target_idx = column_map[target_column]
    filter_idx = column_map[filter_column]

    updated = False

    for row in rows_data:
        row_values = row["values"][0]

        if str(row_values[filter_idx]).lower() == str(filter_value).lower():

            row_values[target_idx] = intent.value

            update_url = f"{BASE_URL}/workbook/tables/{TABLE_ID}/rows/{row['index']}"

            requests.patch(
                update_url,
                headers=headers,
                json={"values": [row_values]}
            )

            updated = True

    if not updated:
        return "❌ No matching rows found"

    return f"✅ Updated '{target_column}' to '{intent.value}'"
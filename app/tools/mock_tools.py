mock_db = [
    {"name": "Somesh", "id": 101, "role": "Doctor"},
    {"name": "Ravi", "id": 102, "role": "Nurse"}
]


def get_row_tool(intent):
    name = intent.filter.get("name")

    for row in mock_db:
        if row["name"].lower() == name.lower():
            return row.get(intent.column)

    return "❌ Not found"


def add_column_tool(intent):
    col = intent.column_name

    for row in mock_db:
        row[col] = None

    return f"✅ Column '{col}' added"   
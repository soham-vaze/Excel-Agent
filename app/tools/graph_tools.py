import requests


def create_session(base_url, headers):
    url = f"{base_url}/workbook/createSession"

    res = requests.post(url, headers=headers, json={"persistChanges": True})

    if res.status_code == 201:
        session_id = res.json()["id"]
        headers["workbook-session-id"] = session_id
        return headers

    raise Exception(f"❌ Session failed: {res.json()}")


def get_columns(base_url, table_id, headers):
    url = f"{base_url}/workbook/tables/{table_id}/columns"
    return requests.get(url, headers=headers).json()


def get_rows(base_url, table_id, headers):
    url = f"{base_url}/workbook/tables/{table_id}/rows"
    return requests.get(url, headers=headers).json()

def add_row_api(base_url, table_id, headers, values):
    url = f"{base_url}/workbook/tables/{table_id}/rows/add"

    body = {
        "values": [values]
    }

    return requests.post(url, headers=headers, json=body).json()


def add_column_api(base_url, table_id, headers, column_name):
    url = f"{base_url}/workbook/tables/{table_id}/columns/add"

    body = {
        "name": column_name
    }

    return requests.post(url, headers=headers, json=body).json()
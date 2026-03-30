import requests

BASE_URL = "https://graph.microsoft.com/v1.0"

def create_session(token, drive_id, file_id):
    url = f"{BASE_URL}/drives/{drive_id}/items/{file_id}/workbook/createSession"

    res = requests.post(
        url,
        headers={"Authorization": f"Bearer {token}"},
        json={"persistChanges": True}
    )

    if res.status_code != 201:
        raise Exception(f"Session failed: {res.text}")

    return res.json()["id"]


def get_tables(headers, drive_id, file_id):
    url = f"{BASE_URL}/drives/{drive_id}/items/{file_id}/workbook/tables"
    return requests.get(url, headers=headers).json()


def get_rows(headers, drive_id, file_id, table_id):
    url = f"{BASE_URL}/drives/{drive_id}/items/{file_id}/workbook/tables/{table_id}/rows"
    return requests.get(url, headers=headers).json()


def add_row(headers, drive_id, file_id, table_id, values):
    url = f"{BASE_URL}/drives/{drive_id}/items/{file_id}/workbook/tables/{table_id}/rows/add"

    payload = {"values": [values]}

    return requests.post(url, headers=headers, json=payload).json()
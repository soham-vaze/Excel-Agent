def log_info(msg: str):
    print(f"[INFO] {msg}")

def log_error(msg: str):
    print(f"[ERROR] {msg}")

def log_debug(msg: str):
    print(f"[DEBUG] {msg}")

def log(title, data=None):
    print(f"\n🔹 {title}")
    if data:
        print(data)
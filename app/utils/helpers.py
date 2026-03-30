def normalize(text: str) -> str:
    return text.strip().lower()


def build_column_map(headers: list) -> dict:
    """
    Converts headers → column index mapping
    """
    return {normalize(col): idx for idx, col in enumerate(headers)}
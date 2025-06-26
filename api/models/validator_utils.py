import os


def validate_directory_path(path: str):
    if not path:
        raise ValueError("Directory path is required.")
    if not os.path.exists(path):
        raise ValueError(f"Log data path does not exists: {path}")
    return path

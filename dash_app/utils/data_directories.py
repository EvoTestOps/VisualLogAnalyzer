import os
from flask import current_app


# In general these functions are kind of bad since they brake the server and frontend roles.


def get_runs(log_directory: str) -> list[str]:
    if not log_directory or not os.path.exists(log_directory):
        return []

    runs = [
        item
        for item in os.listdir(log_directory)
        if os.path.isdir(log_directory + item)
    ]

    return sorted(runs)


# TODO: Only *.log files
def get_all_filenames(log_directory: str) -> list[str]:
    if not log_directory or not os.path.exists(log_directory):
        return []

    all_files = []
    for dirpath, _, filenames in os.walk(log_directory):
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            all_files.append(full_path)
    return sorted(all_files)


def get_all_root_log_directories() -> tuple[list[str], list[str]]:
    base_path = current_app.config["LOG_DATA_PATH"]
    directories = next(os.walk(base_path))[1]
    return directories, [os.path.join(base_path, dir) + "/" for dir in directories]

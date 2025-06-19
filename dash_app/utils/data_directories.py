import os

# conf file?
DATA_DIRECTORY = "log_data/"


def get_log_root_directories():
    return [
        item
        for item in os.listdir(DATA_DIRECTORY)
        if os.path.isdir(DATA_DIRECTORY + item)
    ]


def get_runs(log_directory):
    if not log_directory or not os.path.exists(log_directory):
        return []

    runs = [
        item
        for item in os.listdir(log_directory)
        if os.path.isdir(log_directory + item)
    ]

    return sorted(runs)

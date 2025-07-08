import os


# Maybe this should be done in the backend
def get_runs(log_directory):
    if not log_directory or not os.path.exists(log_directory):
        return []

    runs = [
        item
        for item in os.listdir(log_directory)
        if os.path.isdir(log_directory + item)
    ]

    return sorted(runs)


# TODO: Only *.log files
def get_all_filenames(log_directory):
    if not log_directory or not os.path.exists(log_directory):
        return []

    all_files = []
    for dirpath, _, filenames in os.walk(log_directory):
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            all_files.append(full_path)
    return sorted(all_files)

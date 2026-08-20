import os
from flask import current_app


# In general these functions are kind of bad since they brake the server and frontend roles.


def get_runs(log_directory: str) -> list[str]:
    if (
        not log_directory
        or not os.path.exists(log_directory)
        or not os.path.isdir(log_directory)
    ):
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


def get_all_root_log_directories(base_path=None) -> tuple[list[str], list[str]]:
    base_path = current_app.config["LOG_DATA_PATH"] if not base_path else base_path

    entries = next(os.walk(base_path))
    directories = entries[1]
    files = entries[2]

    directory_paths = [os.path.join(base_path, dir) + "/" for dir in directories]
    file_paths = [os.path.join(base_path, file) for file in files]

    names = [f"{os.path.basename(base_path) or base_path} (root)"] + directories + files
    paths = [os.path.abspath(base_path) + "/"] + directory_paths + file_paths

    return names, paths


def get_base_path_directories(
    selected_path: str | None = None, max_depth: int = 1
) -> tuple[list[str], list[str]]:
    """Directories that can be picked as a project base path.

    Lists the log data root and the directories directly below it. When a
    directory is already selected, the directories inside it are listed as
    well, so that deeper paths are reached one level at a time by selecting a
    directory and opening the dropdown again. Names are relative to the log
    data root so that they read like the paths a user would type by hand.
    """
    root = os.path.abspath(current_app.config["LOG_DATA_PATH"])

    if not os.path.isdir(root):
        return [], []

    paths = _walk_directories(root, max_depth)

    if selected_path:
        selected = os.path.abspath(selected_path)
        if selected != root and _is_inside(selected, root):
            # The selection and the directories leading to it stay listed, so
            # that a deeper selection keeps showing in the dropdown and can be
            # stepped back out of.
            paths |= _path_and_parents(selected, root)
            paths |= _walk_directories(selected, max_depth)

    names = [f"{os.path.basename(root) or root} (root)"]
    sorted_paths = [root] + sorted(paths)
    names += [os.path.relpath(path, root) for path in sorted_paths[1:]]

    return names, sorted_paths


def _walk_directories(base_path: str, max_depth: int) -> set[str]:
    directories = set()

    for dirpath, dirnames, _ in os.walk(base_path):
        depth = dirpath[len(base_path) :].count(os.sep)
        if depth >= max_depth:
            dirnames.clear()
            continue

        dirnames[:] = [dir for dir in dirnames if not dir.startswith(".")]
        directories.update(os.path.join(dirpath, dir) for dir in dirnames)

    return directories


def _path_and_parents(path: str, root: str) -> set[str]:
    paths = set()

    while path != root and path != os.path.dirname(path):
        paths.add(path)
        path = os.path.dirname(path)

    return paths


def _is_inside(path: str, root: str) -> bool:
    return os.path.commonpath([path, root]) == root

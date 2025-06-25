from dash_app.utils.data_directories import get_runs, get_all_filenames


def get_filter_options(data_path, runs_or_files="runs"):
    if data_path is None:
        return [] 

    if runs_or_files == "runs":
        items = get_runs(data_path)
    elif runs_or_files == "files":
        items = get_all_filenames(data_path)
    else:
        items = []

    options = [{"label": item, "value": item} for item in items]
    return options
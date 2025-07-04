# Visual Log Analyzer
Web application for visualizing and analysing log files.

> [!WARNING]
> The frontend of this branch is currently completely broken due to changed api handling.

## Run locally
The application has been tested with **Python 3.12**. Other versions might work but with mixed results.

Setup virtual environment and install requirements.
```
python3 -m venv .venv
source .venv/bin/activate
pip intall -r ./requirements.txt
```
Run the application.
```
python3 main.py 
```

Dash frontend: [http://localhost:5000/dash/](http://localhost:5000/dash/)

API endpoints: [http://localhost:5000/api/](http://localhost:5000/api/)

### Expected log data structure
Currently the program expects log data to be stored in a `log_data/` directory located in the root of the project. The directory can contain multiple different datasets.

Example structure:
```
log_data/
├── hadoop
├── lo2_test
│   ├── run1
│   │   ├── log_file_1.log
│   │   ├── log_file_2.log
│   │   └── log_file_n.log
│   ├── run2
│   └── run-n
└── lo2_train
    ├── run1
    │   └── log_files_to_test.log
    └── run-n
```
To use for example `lo2_test`, input `log_data/lo2_test` to the directory path in the GUI.

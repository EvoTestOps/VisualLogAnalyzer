# Visual Log Analyzer
Web application for visualizing and analysing log files.

## Run locally (development mode)
By default, the program expects the datasets to be located within the `log_data/` directory. To change the location of the log data, update the `LOG_DATA_DIRECTORY` environment variable in the Docker Compose file and adjust the volume mapping accordingly. The analysis results are stored in `analysis_results/` as parquet files.


Run `docker compose up`

Dash frontend: [http://localhost:5000/dash/](http://localhost:5000/dash/)

API endpoints: [http://localhost:5000/api/](http://localhost:5000/api/)

### Expected log data structure
Example structure:
```
log_data/
├── hadoop
├── lo2_test
│   ├── error-1
│   │   ├── log_file_1.log
│   │   ├── log_file_2.log
│   │   └── log_file_n.log
│   ├── error-2
│   └── unknown-logs
└── lo2_train
    ├── correct-1
    │   └── passing_logs.log
    └── correct-n
```
For example, to use `lo2_test`, input `log_data/lo2_test` to the directory path in the GUI.

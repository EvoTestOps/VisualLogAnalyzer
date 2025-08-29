# Usage guide

Usage and installation overview of the core features. Additional helpful information can be found in the README.

## Installation

Before installing and starting the application, ensure Docker and Docker-compose are installed. Both can be installed according to the official Docker documentation. **If you’re a student in the University of Helsinki and using a fuksi laptop**, there are some other steps you need to take to install Docker correctly (Docker uses the root partition by default and if it gets filled your computer can become unusable). Information about installing Docker on cubbli-linux [here](https://version.helsinki.fi/cubbli/cubbli-help/-/wikis/Docker). After installing Docker on cubbli-linux, you can install the Docker-compose plugin according to the [official documentation](https://docs.docker.com/compose/install/linux/).

To run the application, execute the following commands:

```
git clone https://github.com/EvoTestOps/VisualLogAnalyzer.git
cd VisualLogAnalyzer
mkdir analysis_results    #  Optional but recommended to avoid permission issues
docker compose --env-file .env.sample up
```

To omit the `--env-file` flag, rename `.env.sample` to `.env`. For example with command: `mv .env.sample .env`

Building the application for the first time may take 1-2 minutes. Once the applitcation is running navigate to <http://localhost:5000/dash/> to access the homepage.

## Running analyses

The repository includes an example light-oauth-2 dataset. It contains a `Labeled` directory which has known cases (either correct or some type of error), and a `Hidden_Group_1` which contains unknown cases. Reviewing the dataset structure is recommended.

To use the dataset:

1. Navigate to the homepage.
2. Click "Create a new project", give it a name, and set the base path to `./log_data/LO2`

With setting the base path we are able to access the directories inside the LO2 directory.

![Project creation](/docs/images/project_creation.png)

After the project has been created click it on the list which should take you to the project view. Here we have four main components:

- List of analyses run in the project
- "Create a new analysis"-options. When a option is clicked e.g. "Anomaly Detection" it will give you options on which level you want to run it
- Settings box with relevant settings (hover for explanations)
- "Recent analyses" table for monitoring the status of analyses, inspecting logs and error messages.

![Project view](/docs/images/project_view.png)

Lets start by running an simple example analysis:

1. Click "High Level Visualisations" and then "Directory Level".
2. Select "Labeled" from the "Directory" dropdown and click "Analyze".

![High lvl viz form](/docs/images/high_lvl_viz_form.png)

This redirects you back to the project page, where the results will appear once the analysis is complete.

![High lvl viz complete](/docs/images/high_lvl_viz_complete.png)

Clicking the result will show a plot and analysis details. Hover over data points for more information.

![High lvl viz results](/docs/images/high_lvl_viz_results.png)

Next, lets try running anomaly detection:

1. Go back to the project page and select "Anomaly Detection" and then "Line Level".
2. Select `Labeled` from both "Train data directory" and "Test data directory".

- Compared to high level visualisations and log distance analysis, you will need to input train data directory and test data directory separately. This either means having two directories where one contains only train data and the other one only test data, or by filtering the data in the "Directories to include in train data" and "Directories to include in test data".

3. From the "Directories to include in train data" select only the correct cases.
4. For the "Directories to include in test data" select the rest which were not selected to the train data.
5. Select a "Regex mask type" (e.g. "Myllari" or "Myllari Extended")\*\*.

- In general it is a good idea to use a mask unless there is some really good reason not to.

6. Click "Analyze".

![Ano line lvl form](/docs/images/ano_line_lvl_form.png)

The results will be displayed on the list similarly as in the previous analysis. After clicking the results you can select plot (file) to display from the drop down. This will generate a plot and a table containing the analysis results of that specific file in line level. Clicking a data point on the plot takes you to the correct line on the table.

![Ano line lvl results](/docs/images/ano_line_results.png)

To view moving averages in the plots, navigate back to the project page and select either "Moving averages only" or "Show all" from the settings, and click "Apply". Now when navigating back to the results the moving averages are displayed.

![Ano line moving averages](/docs/images/ano_line_moving_avg.png)

In line level anomaly detection, you can create a multi-plot image to visualize multiple plots side-by-side. In a anomaly detection line level results page, click "Create multi-plot image" and from the form select the files and columns to include. In general using moving averages as the columns is the most useful.

![Multi-plot](/docs/images/multi_plot.png)

## Adding your own datasets

By default, the application looks for datasets in the `log_data`-directory. To add your own dataset, simply copy/move them in to that directory (you might need to refresh the page to see the directory). To use directories in the root of `log_data`, leave the base path of the project empty or use the default value. You can organize your datasets similarly as the example dataset was organized and specify the path in the base path input. The base path can also be used to navigate further down in the directory structure what the directory input options normally allows, which might be useful in some log data structures.

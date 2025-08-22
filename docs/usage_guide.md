# Usage guide

Usage and installation overview of the core features. Some other useful information will be in the README.

## Installation

Before installing and starting the application make sure you have Docker and Docker-compose installed. Both can be installed according to the official documentation of Docker. If you’re a student in the University of Helsinki and using a fuksi laptop, there might be some other steps you need to take to install Docker correctly (Docker might use the root partition and if it gets filled your computer might become unusable, since the size of the root-partition is small by design on fuksilaptops). Some information about installing Docker on cubbli-linux [here](https://version.helsinki.fi/cubbli/cubbli-help/-/wikis/Docker).

To run the application, execute the following commands:

```
git clone https://github.com/EvoTestOps/VisualLogAnalyzer.git
cd VisualLogAnalyzer
mkdir analysis_results
docker compose --env-file .env.sample up
```

The command `mkdir analysis_results` is optional but it is a good idea to create it yourself, so you don't run into permission issues if you ever want to manually read the results.

To omit the `--env-file` flag, rename `.env.sample` to `.env`. For example with command: `mv .env.sample .env`

It should now be building the images and after that starting the application. When building the application for the first time, it might take a while (around 1-2 minutes).

When the application is running, navigate to <http://localhost:5000/dash/>. Where you should see the homepage of the application.

## Running analyses

The repository comes with an example light-oauth-2 dataset, which you can use when trying out the application. It contains a `Labeled`-directory which has known cases (either correct or some type of error), and a `Hidden_Group_1` which contains unknown cases (we do not know if they are normal operation or anomalies). I recommend checking the structure of the dataset.

To use the dataset navigate to the homepage, click "Create a new project", give the project a name and then type `.log_data/LO2` to the base path. With setting the base path we are able to access the directories inside the LO2 directory.

![Project creation](/docs/images/project_creation.png)

After the project has been created click it on the list which should take you to the project-view. Here we have four main components:

- List of analyses run in the project
- "Create a new analysis"-options. When a option is clicked eg. "Anomaly Detection" it will give you options on which level you want to run it
- Settings-box, which contains some relevant settings. You can hover on the texts to see an explanation.
- "Recent analyses"-table. Here you can see the status of your recent analyses for example if it is running, successful or failed. Also you can inspect the logs and possible error messages of failed analyses.

![Project view](/docs/images/project_view.png)

Lets start by running an simple example analysis. Click "High Level Visualisations" and then "Directory Level". Which takes you to a form page. Select "Labeled" from the "Directory"-dropdown and click the "Analyze"-button.

![High lvl viz form](/docs/images/high_lvl_viz_form.png)

This should redirect you back to the project page, and the results should appear to the list pretty quickly since this is a very simple analysis.

![High lvl viz complete](/docs/images/high_lvl_viz_complete.png)

After clicking result on the list you should see a plot and some information about the analysis on the top of it. You can investigate the datapoints by hovering over them.

![High lvl viz results](/docs/images/high_lvl_viz_results.png)

Lets next try running anomaly detection. Go back to the project-page and select "Anomaly Detection" and then "Line Level". Now compared to high level visualisations and log distance analysis, you will need to input train data directory and test data directory separately. This either means having to directories of which one contains only train data and the other one only test data, or by filtering the data in the "Directories to include in train data" and "Directories to include in test data". Let's start by selecting `Labeled` from each "Train data directory" and "Test data directory". Then from the "Directories to include in train data" select only the correct cases. In the "Directories to include in test data" select the rest which were not selected to the train data. After that select a "Regex mask type", for example "Myllari" or "Myllari Extended". In general it is a good idea to use a mask unless there is some really good reason not to. Finally click "Analyze".

![Ano line lvl form](/docs/images/ano_line_lvl_form.png)

The results will be shown on the list similarly as in the previous one. After clicking the results you can select plot (file) to display from the dropdown. This will generate a plot and a datatable containing the analysis results of that specific file in line level. Clicking a datapoint on the plot takes you to the correct line on the table.

![Ano line lvl results](/docs/images/ano_line_results.png)

If you want to see moving averages in the plots, navigate back to the project-page and select either "Moving averages only" or "Show all" from the settings and click "Apply". Now when you navigate back to the results you should see the moving averages.

![Ano line moving averages](/docs/images/ano_line_moving_avg.png)

In line level anomaly detection there is also an option to create a multi-plot image to visualize multiple plots side-by-side. In a anomaly detection line level results page, click "Create multi-plot image" and from the form select the files and columns you want to include. In general using moving averages as the columns is the most useful.

![Multi-plot](/docs/images/multi_plot.png)

## Adding your own datasets

By default, the application looks for datasets in the `log_data`-directory. To add your own dataset you can simply copy/move them in to that directory (you might need to refresh the page for the directory to show). If you want to use directories in the root of the `log_data`, simply leave the base path of the project empty or leave the default value untouched. You can organize your datasets similarly as the example dataset was organized and just specify the path in the base path input. You can also use the base path to traverse further down in the directory structure what the directory input options normally allows, which might be useful in some log data structures.

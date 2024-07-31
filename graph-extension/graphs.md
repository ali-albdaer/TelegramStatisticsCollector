# Graphs Extension

This script converts the data obtained from the main collection script into various graphs using matplotlib. Currently, the graphs are:

- Activity-Time Plot: Shows how many messages the user sent each day. (GIF animation and static PNG)
- Category Histograms: Histograms to show the top entries in each category for each user. (GIF animation and static PNG)
- Metrics Radar Chart: A radar chart to display the user's dominant metrics (messages, media, activeness, ...) 
- Feelings Radar Chart: A radar chart for sentiment analysis data. (joy, fear, sadness, anger, ...)

All of these graphs are easily configurable, and new graphs can be added by following the function structure in `create_graphs.py`.

## Installation

After cloning the repository, install the additional dependecies:

```shell
cd graph-extension
pip install -r requirements.txt
```

## Configuration

1. **Create a `config.py` file in this `(graph-extension)` directory and specify the path for the json file (see `graph-extension/config.example.py`):**

    ```python
    # graph-extension/config.py
    json_file = "data/user_stats.json"
    ```

    OR

    ```python
    # graph-extension/config.py
    json_file = "data/global_stats.json"
    ```

    Notes: 
        - Similar to the wordclouds extension, global/user stats structure is automatically identified.
        - Depending on where you want to run the script from, you may want to specify the path as `user_stats.json` / `global_stats.json`,
        by manually moving the `.json` files to this directory.

2. **Configure the parameters in config.py:**

    ```python
    SHOW_PLOTS = False
    SAVE_PLOTS = True

    # Choose what graphs to generate.
    GENERATE_ACTIVITY_GIF = True
    GENERATE_ACTIVITY_PNG = True
    GENERATE_CATEGORY_HISTOGRAM_GIFS = True
    GENERATE_CATEGORY_HISTOGRAM_PNGS = True
    GENERATE_METRICS_RADAR = True
    GENERATE_FEELINGS_RADAR = True

    ACTIVITY_PARAMS = {
        'FIGURE_SIZE': (9.6, 5.4),
        'GRAPH_COLOR': 'blue',
        'GRAPH_BACKGROUND_COLOR': 'white',
        'AXIS_COLOR': 'black',
        'TEXT_COLOR': 'black',
        ...
    }

    # Check graph-extension/config.example.py for a full list.
    ```

## Usage

1. **Run the script:**

   ```sh
   python create_graphs.py
   ```

2. **View the data:**

    In the `output_folder` directory, a folder for each user will be created, which will contain 2 subfolders: `static` and `animation`, each containing relevant graph files. (PNG / GIF).

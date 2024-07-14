# Json to Word Clouds Extension

This part of the project is used to convert the data obtained in `.json` format to nice word clouds, see the (examples)[word-cloud/examples]

## Installation

After cloning the repository, install the additional dependecies:

```shell
cd word-cloud
pip install -r requirements.txt
```

## Configuration

1. **Create a `config.py` file in this `(word-cloud)` directory and specify the path for the json file (see `word-cloud/config.example.py`):**

    ```python
    # word-cloud/config.py
    json_file = "user_stats.json"
    GLOBAL_STATS = False
    ```

    - If you want to create a wordcloud for the `global_stats.json`, set `GLOBAL_STATS` to `True`.
    - This is needed since the json structures of `users` and `global` are different.

    ```python
    # word-cloud/config.py
    json_file = "global_stats.json"
    GLOBAL_STATS = True
    ```

    Note: Depending on where you are running the script from, you may want to manually move the `.json` files to this directory for easier usage.

2. **You can ptionally configure these other parameters:**

    ```python
    BACKGROUND_COLOR = "white"
    COLOR_MODE = "RGB"

    SIZE = (800, 600)
    FRAME_SIZE = (950, 750)

    WORD_COUNT = 100
    CATEGORY_WORD_COUNT = 100

    FRAME_DURATION = 3000
    LOOPS = 1

    # See word-cloud/config.example.py for the full list of parameters
    ```

## Usage

1. **Run the script:**

   ```sh
   python create_wordclouds.py
   ```

2. **View the data:**

    In the `output_folder` directory, a folder for each user and one folder for the global statistics will be generated.
    Each folder contains 3 sub-folders:
        - `top_words`: Contains 2 wordclouds in PNG format, with and without including common words.
        - `categories_gif`: Contains a GIF file where each frame has words from different categories. 
        - `categories_png`: Contains the frames of the GIF above in PNG format, can be optionally removed in `config.py`

## Contributing

This part of the project also welcomes contributions.

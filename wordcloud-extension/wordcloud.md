# Json to Word Clouds Extension

This part of the project is used to convert the data obtained in `.json` format to nice word clouds, see the (examples)[wordcloud-extension/examples]

## Installation

After cloning the repository, install the additional dependecies:

```shell
cd word-cloud
pip install -r requirements.txt
```

## Configuration

1. **Create a `config.py` file in this `(wordcloud-extension)` directory and specify the path for the json file (see `wordcloud-extension/config.example.py`):**

    ```python
    # word-cloud/config.py
    json_file = "data/user_stats.json"
    ```

    OR

    ```python
    # word-cloud/config.py
    json_file = "data/global_stats.json"
    ```

    Notes: 
        - The structures of the `.json` files are different but the script will correctly identify which type it is dealing with.
        - Depending on where you want to run the script from, you may want to specify the path as `user_stats.json` / `global_stats.json`,
        by manually moving the `.json` files to this directory.

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

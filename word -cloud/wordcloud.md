# Json to Word Clouds Extension

This part of the project is used to convert the data obtained in `.json` format to nice word clouds, see the (examples)[word-cloud/examples]

## Installation

After cloning the repository, install the additional dependecies:

```shell
cd word-cloud
pip install -r requirements.txt
```

## Configuration

1. **Create a `config.py` file in this `(word-cloud)` directory and provide the following data (see `config.example.py`):**

   ```python
   # word-cloud/config.py

   ```


2. **Choose the paths for the output files:**

    ```python
    global_stats_file = ''
    user_stats_file = ''
    ```


3. **Optionally configure the following parameters:**

    ```python
    SIZE = (800, 600)
    ```

## Usage

1. **Run the script:**

   ```sh
   python create_wordclouds.py
   ```

2. **View the data:**

    In the `output_folder` directory, a folder for each user and one folder for the global statistics will be generated.
    Each folder contains 3 sub-folders:
        - ``: 
        - ``: 
        - ``: 

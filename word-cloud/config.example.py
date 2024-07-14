import random

output_folder = "output"  # The folder where the word clouds will be saved
json_file  = "user_stats.json"  # The JSON file containing the user stats / global stats

GLOBAL_STATS = False  # Toggle to use global stats instead of user stats, this is needed since the structures of the JSON files are different.

word_data = "top_words"  # The key in the user data dictionary that contains the word data
category_data = "top_categories"  # The key in the user data dictionary that contains the category data

BACKGROUND_COLOR = "white"  # The background color of the word clouds
COLOR_MODE = "RGB"  # Color mode for images ("RGB" or "RGBA")

color_maps = ['Accent', 'Accent_r', 'Blues', 'Blues_r', 'BrBG', 'BrBG_r', 'BuGn', 'BuGn_r', 'BuPu', 'BuPu_r', 'CMRmap', 'CMRmap_r', 'GnBu', 'GnBu_r', 'OrRd', 'OrRd_r', 'Oranges', 'Oranges_r', 'PRGn', 'PRGn_r', 'Paired', 'Paired_r', 'Pastel1', 'Pastel1_r', 'Pastel2', 'Pastel2_r', 'PiYG', 'PiYG_r', 'PuBu', 'PuBuGn', 'PuBuGn_r', 'PuBu_r', 'PuOr', 'PuOr_r', 'PuRd', 'PuRd_r', 'Purples', 'Purples_r', 'RdBu', 'RdBu_r', 'RdGy', 'RdGy_r', 'RdPu', 'RdPu_r', 'RdYlBu', 'RdYlBu_r', 'RdYlGn', 'RdYlGn_r', 'Reds', 'Reds_r', 'Set1', 'Set1_r', 'Set2', 'Set2_r', 'Set3', 'Set3_r', 'Spectral', 'Spectral_r', 'Wistia', 'Wistia_r', 'YlGn', 'YlGnBu', 'YlGnBu_r', 'YlGn_r', 'YlOrBr', 'YlOrBr_r', 'YlOrRd', 'YlOrRd_r', 'afmhot', 'afmhot_r', 'autumn', 'autumn_r', 'binary', 'binary_r', 'bone', 'bone_r', 'brg', 'brg_r', 'bwr', 'bwr_r', 'cividis', 'cividis_r', 'cool', 'cool_r', 'coolwarm', 'coolwarm_r', 'copper', 'copper_r', 'cubehelix', 'cubehelix_r', 'flag', 'flag_r', 'gist_earth', 'gist_earth_r', 'gist_heat_r', 'gist_ncar', 'gist_ncar_r', 'gist_rainbow', 'gist_rainbow_r', 'gist_stern', 'gist_stern_r', 'gist_yarg', 'gist_yarg_r', 'gnuplot', 'gnuplot2', 'gnuplot2_r', 'gnuplot_r', 'gray', 'gray_r', 'hot', 'hot_r', 'hsv', 'hsv_r', 'inferno', 'inferno_r', 'jet', 'jet_r', 'magma', 'magma_r', 'nipy_spectral', 'nipy_spectral_r', 'ocean', 'ocean_r', 'pink', 'pink_r', 'plasma', 'plasma_r', 'prism', 'prism_r', 'rainbow', 'rainbow_r', 'seismic', 'seismic_r', 'spring', 'spring_r', 'summer', 'summer_r', 'tab10', 'tab10_r', 'tab20', 'tab20_r', 'tab20b', 'tab20b_r', 'tab20c', 'tab20c_r', 'terrain', 'terrain_r', 'twilight', 'twilight_r', 'twilight_shifted', 'twilight_shifted_r', 'viridis', 'viridis_r', 'winter', 'winter_r']
COLOR_MAP = lambda: random.choice(color_maps)  # An example function that chooses a color map for the word clouds

SIZE = (800, 600)  # The size of the word clouds, a tuple of width and height
FRAME_SIZE = (950, 750)  # The size for the frame around the word clouds, a tuple of width and height

MIN_FONT_SIZE = 10  # The minimum font size for the word clouds
MAX_FONT_SIZE = 200  # The maximum font size for the word clouds

WORD_COUNT = 100  # The number of words to include in the word clouds
CATEGORY_WORD_COUNT = 100  # The number of top words to include in each category word cloud
MIN_CATEGORY_WORDS = 2  # Minimum number of words in a category to generate a word cloud

FRAME_DURATION = 3000  # Duration of each frame in the GIFs in milliseconds
LOOPS = 1  # Integer indicating how many times the GIF should loop (set to 0 for infinite loop)

SKIP_UNKNOWN_CATEGORIES = True  # Toggle to skip categories that are not in the INCLUDED_CATEGORIES dictionary
SHOW_TITLES = False  # Toggle to show/hide titles on word clouds
SHOW_GIF_TITLE_FRAME = False  # Toggle to show/hide the title frame in the GIFs
KEEP_FRAMES = False  # Toggle to keep the frame files used in the GIFs

default_title_format = "{0}'s Top Mentioned {1} Words"  # Default title for the word clouds, {0} will be replaced with the user's name and {1} with the number of words
title_frame_format = "{0}'s Top {1} Words Categorized"  # Format for the title frame in the GIFs, {0} will be replaced with the user's name and {1} with the number of words

category_title_formats = {  # Title formats for each category word cloud, {} will be replaced with the user's name
    "common phrases": "{}'s Top Common Phrases",
    "languages": "{}'s Top Mentioned Languages",
    "countries": "{}'s Top Mentioned Countries",
    "cities": "{}'s Top Mentioned Cities",
    "continents": "{}'s Top Mentioned Continents",
    "animals": "{}'s Top Mentioned Animals",
    "colors": "{}'s Top Mentioned Colors",
    "months": "{}'s Top Mentioned Months",
    "days": "{}'s Top Mentioned Days",
    "planets": "{}'s Top Mentioned Planets",
    "numbers": "{}'s Top Mentioned Numbers",
    "brands": "{}'s Top Mentioned Brands",
    "fruits and veggies": "{}'s Top Mentioned Fruits and Veggies",
    "famous people": "{}'s Top Mentioned Famous People",
}

# A verison of the word cloud without these words will be generated.
common_words = {
    'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i', 'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
    'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she', 'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their',
    'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go', 'me', 'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him',
    'into', 'year', 'your', 'good', 'some', 'could', 'them', 'see', 'other', 'than', 'then', 'now', 'look', 'only', 'come',
    'its', 'over', 'also', 'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first', 'well', 'way', 'even', 'new', 'want', 'because', 'any',
    'these', 'day', 'most', 'us', *"abcdefghijklmnopqrstuvwxyz",
}

development = False

SHOW_PLOTS = False
SAVE_PLOTS = True

if development:
    output_folder = "graphs_dev"
    json_file  = "data_dev/user_stats.json"

else:
    output_folder = "graphs"
    json_file  = "data/user_stats.json"

# Choose what graphs to generate.
GENERATE_ACTIVITY_CHART = True
GENERATE_CATEGORY_HISTOGRAM_GIFS = True
GENERATE_CATEGORY_HISTOGRAM_PNGS = True
GENERATE_METRICS_RADAR = True

# Generate graphs for all users in the list. If the list is empty, generate graphs for all users in the json file.
GENERATE_FROM_LIST = []

ACTIVITY_PARAMS = {
    'FIGURE_SIZE': (9.6, 5.4),
    'GRAPH_COLOR': 'blue',
    'GRAPH_BACKGROUND_COLOR': 'white',
    'AXIS_COLOR': 'black',
    'TEXT_COLOR': 'black',

    'TITLE': '{name} - Activity Over Time',  # Can be set to None. {name} is optional.
    'SHOW_FIRST_MESSAGE': True,  # Show the first message date on the analytics.
    'SHOW_TOP_ACTIVE_DAYS': 3,  # Amount of most active days to show on the analytics.
    'SHOW_RATIOS': True,  # Show ratios such as messages per day and words per message.

    'X_LABEL': None,
    'Y_LABEL': "Amount of Messages Sent",

    'SHOW_DATES': True,  # Show dates on the x-axis, set to False to only show days as integers.
    'AXIS_DATE_FORMAT': '%Y-%m',  # Format for the dates on the x-axis.

    'DYNAMIC_PARAMETERS': True,  # Set to True to automatically set the limits and intervals. The 4 parameters below will be ignored.
    'X_LIMIT': None,  # None or a tuple with the limits for the x-axis.
    'Y_LIMIT': None,  # None or a tuple with the limits for the y-axis.
    'X_INTERVAL': None,  # None or an integer with the interval for the x-axis.
    'Y_INTERVAL': None,  # None or an integer with the interval for the y-axis.
    
    'ANIMATION_MODE': 'DURATION',  # 'DURATION' or 'SPEED' for exact time or speed between frames, 'AUTO' for a linear interpolation between the min and max values.
    
    'ANIMATION_FIXED_SPEED': 100,  # Time in milliseconds between each frame of the animation, ignored if mode is not 'SPEED'.
    'ANIMATION_FIXED_DURATION': 12000,  # Time in milliseconds for the whole animation, ignored if mode is not 'DURATION'.
    
    # Min and max values for the animation interpolation, ignored if mode is not 'AUTO'.
    'ANIMATION_MIN_DURATION': 1000,
    'ANIMATION_MAX_DURATION': 12000,
    'ANIMATION_MIN_FRAMES': 10,
    'ANIMATION_MAX_FRAMES': 200, 
}

CATEGORY_PARAMS = {
    'FIGURE_SIZE': (9.6, 5.4),
    'GRAPH_COLOR': 'blue',
    'GRAPH_BACKGROUND_COLOR': 'white',
    'AXIS_COLOR': 'black',
    'TEXT_COLOR': 'black',
    'TITLE': '{name}\'s Top Mentioned {category_name}',  # Title of the category histogram. Vars: {name}, {category_name}, {id}

    'X_LABEL': None,
    'Y_LABEL': 'Mentions',

    'DYNAMIC_PARAMETERS': True,  # Automatically detemine the limits.
    'X_LIMIT': None,
    'Y_LIMIT': None,

    'ANIMATION_MODE': 'DURATION',  # 'DURATION' or 'SPEED' or 'AUTO'

    'ANIMATION_FIXED_SPEED': 100,
    'ANIMATION_FIXED_DURATION': 6000,

    'ANIMATION_MIN_DURATION': 1000,
    'ANIMATION_MAX_DURATION': 8000,
    'ANIMATION_MIN_FRAMES': 10,
    'ANIMATION_MAX_FRAMES': 200,

    'BAR_ORDER': 'ALPHABETICAL',  # 'ASC' or 'DESC' or 'ALPHABETICAL'
    'COLORMAP': 'RdYlGn_r',  # Matplotlib colormap for the bars. (https://matplotlib.org/stable/tutorials/colors/colormaps.html)
    'GLOBAL_LIMIT': 10,  # Default limit of bars per category. 
    'CATEGORIES': {  # Limit of bars per category. Set to -1 to use the CATEGORY_GLOBAL_LIMIT.
        'common phrases': 10,
        'countries': 5,
        'languages': 5,
        'sports': -1,
        'colors': 6,
        'famous people': 15
    },
}


METRICS_RADAR_PARAMS = {
    'TITLE': '{names[0]} - Metrics',  # Title of the radar chart. Can be None.
    'FIGURE_SIZE': (9, 9),
    'FRAME': 'polygon',  # Or 'circle'
    'ANGLE': 2,  # Angle in degrees for the labels offset.
    'BACKGROUND_COLOR': 'white',
    'AXIS_COLOR': 'gray',
    'TEXT_COLOR': 'black',
    'COLORS': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'],  # For now, only the first color is used.
    'SHOW_LEGEND': True,
    
    'DYNAMIC_PARAMETERS': True,  # Set to True to automatically determine the ranges for data normalization. (highly recommended)
    'METRICS': {
        # Metric names and their ranges for normalization.
        # The ranges are used to normalize the data between 0 and 1.
        # If dynamic parameters is set to True, these ranges will be ignored.
        'message_count': ('Message Count', (0, 10000)),
        'word_count': ('Word Count', (0, 5000)),
        'ratios.word_per_message': ('Words per Message', (0, 100)),  # access nested dict values with a dot.
        'media_count': ('Media Count', (0, 1000)),
        'reactions_given_count': ('Reactions Given', (0, 500)),  # Note that global stats only have `reaction_count`
        'reactions_received_count': ('Reactions Received', (0, 500)),  # ^^^
        'loud_message_count': ('Loud Message Count', (0, 100)),
        'curse_count': ('Curse Count', (0, 100)),
    },
}

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

# Parameters for all graphs.
PARAMETERS = {
    # Global params
    'FIGURE_SIZE': (9.6, 5.4),
    'GRAPH_COLOR': 'blue',
    'GRAPH_BACKGROUND_COLOR': 'white',
    'AXIS_COLOR': 'black',
    'TEXT_COLOR': 'black',

    # Params for the activity-time graph
    'ACTIVITY_TITLE': 'Activity-Time Graph for {name} (ID: {id})',

    'ACTIVITY_SHOW_FIRST_MESSAGE': True,  # Show the first message date on the analytics.
    'ACTIVITY_SHOW_TOP_ACTIVE_DAYS': 3,  # Amount of most active days to show on the analytics.
    'ACTIVITY_SHOW_RATIOS': True,  # Show the ratios of messages sent by the user.

    'ACTIVITY_X_LABEL': "Days",
    'ACTIVITY_Y_LABEL': "Messages Sent",
    'ACTIVITY_SHOW_DATES': True,  # Show dates on the x-axis, set to False to only show days as integers.
    'ACTIVITY_AXIS_DATE_FORMAT': '%Y-%m',  # Format for the dates on the x-axis.

    'ACTIVITY_DYNAMIC_PARAMETERS': True,  # Set to True to automatically set the limits and intervals. The 4 parameters below will be ignored.
    'ACTIVITY_X_LIMIT': None,  # None or a tuple with the limits for the x-axis.
    'ACTIVITY_Y_LIMIT': None,  # None or a tuple with the limits for the y-axis.
    'ACTIVITY_X_INTERVAL': None,  # None or an integer with the interval for the x-axis.
    'ACTIVITY_Y_INTERVAL': None,  # None or an integer with the interval for the y-axis.

    'ACTIVITY_ANIMATION_MODE': 'DURATION',  # 'DURATION' or 'SPEED' for exact time or speed between frames, 'AUTO' for a linear interpolation between the min and max values.
    'ACTIVITY_ANIMATION_FIXED_SPEED': 100,  # Time in milliseconds between each frame of the animation, ignored if mode is not 'SPEED'.
    'ACTIVITY_ANIMATION_FIXED_DURATION': 10000,  # Time in milliseconds for the whole animation, ignored if mode is not 'DURATION'.

    # Min and max values for the animation interpolation, ignored if mode is not 'AUTO'.
    'ACTIVITY_ANIMATION_MIN_DURATION': 2000,
    'ACTIVITY_ANIMATION_MAX_DURATION': 10000,
    'ACTIVITY_ANIMATION_MIN_FRAMES': 10,
    'ACTIVITY_ANIMATION_MAX_FRAMES': 200, 


    # Params for the category histograms
    'CATEGORY_TITLE': '{name}\'s Top Mentioned {category_name} (ID: {id})',  # Title of the category histogram. All vars are optional.
    'CATEGORY_X_LABEL': 'Categories',
    'CATEGORY_Y_LABEL': 'Counts',

    'CATEGORY_DYNAMIC_PARAMETERS': True,
    'CATEGORY_X_LIMIT': None,
    'CATEGORY_Y_LIMIT': None,

    'CATEGORY_ANIMATION_MODE': 'AUTO',  # 'DURATION' or 'SPEED' or 'AUTO'
    'CATEGORY_ANIMATION_FIXED_SPEED': 100,
    'CATEGORY_ANIMATION_FIXED_DURATION': 4000,

    'CATEGORY_ANIMATION_MIN_DURATION': 2000,
    'CATEGORY_ANIMATION_MAX_DURATION': 10000,
    'CATEGORY_ANIMATION_MIN_FRAMES': 10,
    'CATEGORY_ANIMATION_MAX_FRAMES': 200,

    'CATEGORY_BAR_ORDER': 'DESC',  # 'ASC' or 'DESC' or 'ALPHABETICAL'
    'CATEGORY_COLORMAP': 'RdYlGn_r',  # Matplotlib colormap for the bars. (https://matplotlib.org/stable/tutorials/colors/colormaps.html)

    'CATEGORY_GLOBAL_LIMIT': 10,  # Default limit of bars per category. 
    'CATEGORIES': {  # Limit of bars per category. Set to -1 to use the CATEGORY_GLOBAL_LIMIT.
        'common phrases': 10,
        'countries': 5,
        'languages': 5,
        'sports': -1,
        'colors': 6,
        'famous people': 15
    },

    # Params for the radar chart
    'METRICS_RADAR_TITLE': '{names[0]}\'s Metrics',  # Title of the radar chart. Can be None.
    'METRICS_RADAR_FIGURE_SIZE': (9, 9),
    'METRICS_RADAR_FRAME': 'polygon',  # Or 'circle'
    'METRICS_RADAR_ANGLE': 2,  # Angle in degrees for the labels offset.
    'METRICS_RADAR_BACKGROUND_COLOR': 'white',
    'METRICS_RADAR_AXIS_COLOR': 'gray',
    'METRICS_RADAR_TEXT_COLOR': 'black',
    'METRICS_RADAR_COLORS': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'],  # For now, only the first color is used.
    'METRICS_RADAR_SHOW_LEGEND': True,
    'METRICS_RADAR_DYNAMIC_PARAMETERS': True,  # Set to True to automatically determine the ranges for data normalization. (highly recommended)
    'METRICS_RADAR_METRICS': {

        # Metric names and their ranges for normalization.
        # The ranges are used to normalize the data between 0 and 1.
        # If dynamic parameters is set to True, these ranges will be ignored.

        'message_count': ('Message Count', (0, 10000)),
        'word_count': ('Word Count', (0, 5000)),
        'letter_count': ('Letter Count', (0, 20000)),
        'media_count': ('Media Count', (0, 1000)),
        'reactions_given_count': ('Reactions Given', (0, 500)),  # Note that global stats only have `reaction_count`
        'reactions_received_count': ('Reactions Received', (0, 500)),
        'loud_message_count': ('Loud Message Count', (0, 100)),
        'curse_count': ('Curse Count', (0, 100)),
    },
}

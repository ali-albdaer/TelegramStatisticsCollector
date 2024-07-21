development = False

if development:
    output_folder = "graphs_dev"
    json_file  = "data_dev/global_stats.json"

else:
    output_folder = "graphs"
    json_file  = "data/global_stats.json"

# Generate graphs for all users in the list. If the list is empty, generate graphs for all users in the json file.
GENERATE_FROM_LIST = []

PARAMETERS = {
    # Global params
    'FIGURE_SIZE': (9.6, 5.4),
    'GRAPH_COLOR': 'blue',
    'GRAPH_BACKGROUND_COLOR': 'white',
    'AXIS_COLOR': 'black',
    'TEXT_COLOR': 'black',

    # Params for the activity-time graph
    'ACTIVITY_TITLE': 'Activity-Time Graph for {name} (ID: {id})',
    'ACTIVITY_SHOW_ANALYTICS': True,  # Show analytics on the right side of the graph (first message, most active day, etc.)
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

    'CATEGORY_GLOBAL_LIMIT': 10,  # Default limit of bars per category. 
    'CATEGORIES': {  # Limit of bars per category. Set to -1 to use the CATEGORY_GLOBAL_LIMIT.
        'common phrases': 10,
        'countries': 5,
        'languages': 5,
        'sports': -1,
        'colors': 6,
        'famous people': 15
    }
}

output_folder = "graphs"
json_file  = "data/user_stats.json"

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
    'ACTIVITY_ANIMATION_SPEED': 100,
    'ACTIVITY_X_LABEL': "Days",
    'ACTIVITY_Y_LABEL': "Messages Sent",
    'ACTIVITY_SHOW_DATES': True,  # Show dates on the x-axis, set to False to only show days as integers.
    'ACTIVITY_AXIS_DATE_FORMAT': '%Y-%m',  # Format for the dates on the x-axis.
    'ACTIVITY_DYNAMIC_PARAMETERS': True,  # Set to True to automatically set the limits and intervals. The parameters below will be ignored.
    'ACTIVITY_X_LIMIT': None,
    'ACTIVITY_Y_LIMIT': None,
    'ACTIVITY_X_INTERVAL': None,
    'ACTIVITY_Y_INTERVAL': None,

    # Params for the category histograms
    'CATEGORY_ANIMATION_SPEED': 100,
    'CATEGORY_X_LABEL': 'Categories',
    'CATEGORY_Y_LABEL': 'Counts',
    'CATEGORY_DYNAMIC_PARAMETERS': True,
    'CATEGORY_TITLE': 'Category Distribution for {name}',
    'CATEGORY_GLOBAL_LIMIT': 10,  # New global limit parameter
    'CATEGORIES': {  # Limit of bars per category. Set to -1 to use the CATEGORY_GLOBAL_LIMIT.
        'common phrases': 10,
        'countries': 5,
        'languages': 5,
        'sports': -1,
        'colors': 6,
        'famous people': 15
    }
}

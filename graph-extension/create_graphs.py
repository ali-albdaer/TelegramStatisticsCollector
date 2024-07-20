import os
import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from datetime import datetime, timedelta

from config import output_folder, json_file, PARAMETERS, GENERATE_FROM_LIST


def create_activity_animation(user_id, user_data, animations_folder, *, activity_factor=None):    
    # Getting the activity data
    activity_data = user_data['top_active_days']
    activity_factor = activity_factor or 1
    start_date = min(activity_data.keys())
    start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_date_dt = datetime.strptime(max(activity_data.keys()), '%Y-%m-%d')
    
    # Daily message counts
    current_date = start_date_dt
    date_list = []
    message_counts = []
    while current_date <= end_date_dt:
        date_str = current_date.strftime('%Y-%m-%d')
        date_list.append((current_date - start_date_dt).days)
        message_counts.append(activity_data.get(date_str, 0))
        current_date += timedelta(days=1)
    
    # Figure and axes
    fig, ax = plt.subplots(figsize=PARAMETERS['FIGURE_SIZE'])
    fig.patch.set_facecolor(PARAMETERS['GRAPH_BACKGROUND_COLOR'])

    ax.set_facecolor(PARAMETERS['GRAPH_BACKGROUND_COLOR'])
    ax.spines['bottom'].set_color(PARAMETERS['AXIS_COLOR'])
    ax.spines['left'].set_color(PARAMETERS['AXIS_COLOR'])
    ax.tick_params(axis='x', colors=PARAMETERS['AXIS_COLOR'])
    ax.tick_params(axis='y', colors=PARAMETERS['AXIS_COLOR'])
    ax.yaxis.label.set_color(PARAMETERS['TEXT_COLOR'])
    ax.xaxis.label.set_color(PARAMETERS['TEXT_COLOR'])
    ax.title.set_color(PARAMETERS['TEXT_COLOR'])
    
    # Set the limits and labels
    if PARAMETERS['ACTIVITY_DYNAMIC_PARAMETERS']:
        ax.set_xlim(0, len(date_list))
        ax.set_ylim(0, max(message_counts) + 10)
        ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
        ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))

    else:
        ax.set_xlim(PARAMETERS['ACTIVITY_X_LIMIT'])
        ax.set_ylim(PARAMETERS['ACTIVITY_Y_LIMIT'])

        if PARAMETERS['ACTIVITY_X_INTERVAL']:
            ax.xaxis.set_major_locator(plt.MultipleLocator(PARAMETERS['ACTIVITY_X_INTERVAL']))

        if PARAMETERS['ACTIVITY_Y_INTERVAL']:
            ax.yaxis.set_major_locator(plt.MultipleLocator(PARAMETERS['ACTIVITY_Y_INTERVAL']))

    ax.set_xlabel(PARAMETERS['ACTIVITY_X_LABEL'])
    ax.set_ylabel(PARAMETERS['ACTIVITY_Y_LABEL'])
    ax.set_title(PARAMETERS['ACTIVITY_TITLE'].format(name=user_data['name'], id=user_id))

    if PARAMETERS['ACTIVITY_SHOW_DATES']:
        ax.set_xticks(range(0, len(date_list), PARAMETERS['ACTIVITY_X_INTERVAL'] or max(1, len(date_list) // 10)))
        ax.set_xticklabels([(start_date_dt + timedelta(days=i)).strftime(PARAMETERS['ACTIVITY_AXIS_DATE_FORMAT']) for i in range(0, len(date_list), PARAMETERS['ACTIVITY_X_INTERVAL'] or max(1, len(date_list) // 10))], rotation=45)

    else:
        ax.xaxis.set_major_locator(plt.MultipleLocator(PARAMETERS['ACTIVITY_X_INTERVAL'] or max(1, len(date_list) // 10)))

    line, = ax.plot([], [], marker='o', color=PARAMETERS['GRAPH_COLOR'])

    if PARAMETERS['ACTIVITY_SHOW_ANALYTICS']:
        plt.figtext(0.88, 0.85, f"First Message: {start_date_dt.strftime('%Y-%m-%d')}", ha='right', va='top', fontsize=10, color=PARAMETERS['TEXT_COLOR'])
        plt.figtext(0.88, 0.80, f"Most Active Day: {max(activity_data, key=activity_data.get)}", ha='right', va='top', fontsize=10, color=PARAMETERS['TEXT_COLOR'])
        plt.figtext(0.88, 0.75, f"Messages Sent That Day: {activity_data[max(activity_data, key=activity_data.get)]}", ha='right', va='top', fontsize=10, color=PARAMETERS['TEXT_COLOR'])
        plt.figtext(0.88, 0.70, f"Activeness: {(user_data['activeness'] * 150 / activity_factor):.2f}%", ha='right', va='top', fontsize=10, color=PARAMETERS['TEXT_COLOR'])
        plt.figtext(0.88, 0.65, f"Touch-Grass Rate: {100 - (user_data['activeness'] * 100 / activity_factor):.2f}%", ha='right', va='top', fontsize=10, color=PARAMETERS['TEXT_COLOR'])

    def init():
        line.set_data([], [])
        return line,
    
    def update(frame):
        line.set_data(date_list[:frame+1], message_counts[:frame+1])
        return line,
    
    ani = animation.FuncAnimation(
        fig, update, frames=len(date_list), init_func=init,
        blit=True, interval=PARAMETERS['ACTIVITY_ANIMATION_SPEED']
    )
    
    # Save the animation as a GIF
    gif_path = f"{animations_folder}/activity_time.gif"
    ani.save(gif_path, writer='pillow')
    plt.close(fig)

def create_category_histogram(user_id, user_data, animations_folder, static_graphs_folder):
    categories_dict = PARAMETERS['CATEGORIES']
    global_limit = PARAMETERS['CATEGORY_GLOBAL_LIMIT']
    
    for category, limit in categories_dict.items():
        category_data = user_data['top_categories'].get(category, {})

        if not category_data:
            continue

        entry_limit = limit if limit != -1 else global_limit

        sorted_category_data = sorted(category_data.items(), key=lambda x: x[1], reverse=True)[:entry_limit]
        labels, counts = zip(*sorted_category_data)
        labels, counts = list(labels)[::-1], list(counts)[::-1]

        fig, ax = plt.subplots(figsize=PARAMETERS['FIGURE_SIZE'])
        fig.patch.set_facecolor(PARAMETERS['GRAPH_BACKGROUND_COLOR'])

        ax.set_facecolor(PARAMETERS['GRAPH_BACKGROUND_COLOR'])
        ax.spines['bottom'].set_color(PARAMETERS['AXIS_COLOR'])
        ax.spines['left'].set_color(PARAMETERS['AXIS_COLOR'])
        ax.tick_params(axis='x', colors=PARAMETERS['AXIS_COLOR'])
        ax.tick_params(axis='y', colors=PARAMETERS['AXIS_COLOR'])
        ax.yaxis.label.set_color(PARAMETERS['TEXT_COLOR'])
        ax.xaxis.label.set_color(PARAMETERS['TEXT_COLOR'])
        ax.title.set_color(PARAMETERS['TEXT_COLOR'])

        ax.set_xlabel(PARAMETERS['CATEGORY_X_LABEL'])
        ax.set_ylabel(PARAMETERS['CATEGORY_Y_LABEL'])
        ax.set_title(PARAMETERS['CATEGORY_TITLE'].format(name=user_data['name'], id=user_id, category_name=category))

        if PARAMETERS['CATEGORY_DYNAMIC_PARAMETERS']:
            ax.set_xlim(-0.5, len(labels) - 0.5)
            ax.set_ylim(0, max(counts) + 10)
        else:
            ax.set_xlim(PARAMETERS['CATEGORY_X_LIMIT'])
            ax.set_ylim(PARAMETERS['CATEGORY_Y_LIMIT'])

        bars = ax.bar(labels, [0] * len(labels), color='green')

        def init():
            for bar in bars:
                bar.set_height(0)
            return bars,

        def update(frame):
            for i, bar in enumerate(bars):
                current_height = min(frame, counts[i])
                bar.set_height(current_height)
                color_value = current_height / max(counts)
                bar.set_color(plt.cm.get_cmap('RdYlGn_r')(color_value))
            return bars,

        ani = animation.FuncAnimation(
            fig, update, frames=max(counts) + 1, init_func=init,
            interval=PARAMETERS['CATEGORY_ANIMATION_SPEED']
        )

        gif_path = f"{animations_folder}/category_histogram_{category}.gif"
        ani.save(gif_path, writer='pillow')
        plt.close(fig)

        # Save the last frame as PNG in static_graphs
        fig, ax = plt.subplots(figsize=PARAMETERS['FIGURE_SIZE'])
        fig.patch.set_facecolor(PARAMETERS['GRAPH_BACKGROUND_COLOR'])

        ax.set_facecolor(PARAMETERS['GRAPH_BACKGROUND_COLOR'])
        ax.spines['bottom'].set_color(PARAMETERS['AXIS_COLOR'])
        ax.spines['left'].set_color(PARAMETERS['AXIS_COLOR'])
        ax.tick_params(axis='x', colors=PARAMETERS['AXIS_COLOR'])
        ax.tick_params(axis='y', colors=PARAMETERS['AXIS_COLOR'])
        ax.yaxis.label.set_color(PARAMETERS['TEXT_COLOR'])
        ax.xaxis.label.set_color(PARAMETERS['TEXT_COLOR'])
        ax.title.set_color(PARAMETERS['TEXT_COLOR'])

        ax.set_xlabel(PARAMETERS['CATEGORY_X_LABEL'])
        ax.set_ylabel(PARAMETERS['CATEGORY_Y_LABEL'])
        ax.set_title(PARAMETERS['CATEGORY_TITLE'].format(name=user_data['name'], id=user_id, category_name=category))

        if PARAMETERS['CATEGORY_DYNAMIC_PARAMETERS']:
            ax.set_xlim(-0.5, len(labels) - 0.5)
            ax.set_ylim(0, max(counts) + 10)
        else:
            ax.set_xlim(PARAMETERS['CATEGORY_X_LIMIT'])
            ax.set_ylim(PARAMETERS['CATEGORY_Y_LIMIT'])

        bars = ax.bar(labels, counts, color=[plt.cm.get_cmap('RdYlGn_r')(count / max(counts)) for count in counts])
        png_path = f"{static_graphs_folder}/category_histogram_{category}.png"
        fig.savefig(png_path)
        plt.close(fig)

def generate_data(user_stats):
    user_ids = GENERATE_FROM_LIST if GENERATE_FROM_LIST else user_stats.keys()

    # Calculate some global parameters
    max_activeness = max(user_stats[user_id]['activeness'] for user_id in user_ids)
    
    for user_id in user_ids:
        user_data = user_stats[user_id]
        user_name = user_data['name']

        print(f"Generating graphs for {user_name}...")

        user_folder = os.path.join(output_folder, f"{user_name}_{user_id}")
        if not os.path.exists(user_folder):
            os.makedirs(user_folder)
        
        # Create animations folder
        animations_folder = f"{user_folder}/animations"
        if not os.path.exists(animations_folder):
            os.makedirs(animations_folder)
        
        # Create static graphs folder
        static_graphs_folder = f"{user_folder}/static_graphs"
        if not os.path.exists(static_graphs_folder):
            os.makedirs(static_graphs_folder)
        
        create_activity_animation(user_id, user_data, animations_folder, activity_factor=max_activeness)
        create_category_histogram(user_id, user_data, animations_folder, static_graphs_folder)


if __name__ == '__main__':
    os.makedirs(output_folder, exist_ok=True)

    with open(json_file, 'r') as file:
        user_stats = json.load(file)

    generate_data(user_stats)

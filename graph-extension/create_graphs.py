import os
import json
import numpy as np
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Circle, RegularPolygon
from matplotlib.path import Path
from matplotlib.projections import register_projection
from matplotlib.projections.polar import PolarAxes
from matplotlib.spines import Spine
from matplotlib.transforms import Affine2D

from config import *


def normalize_data(data, ranges):
    normalized_data = {}

    for key, value in data.items():
        min_val, max_val = ranges[key]
        normalized_value = (value - min_val) / (max_val - min_val) if max_val != min_val else 0
        normalized_data[key] = normalized_value
        
    return normalized_data


def determine_normalization_ranges(stats, *, metrics):
    ranges = {metric: (float('inf'), float('-inf')) for metric in metrics}

    # If we only have 1 user, we can't automatically determine the ranges; we'll just use the user's data and display a warning.
    if len(stats) == 1:
        print("WARNING: Only 1 user found. Set 'METRICS_RADAR_DYNAMIC_PARAMETERS' to False to manually set the normalization ranges.")
        return ranges

    for user_data in stats.values():
        for metric in metrics:
            value = user_data.get(metric, 0)
            min_val, max_val = ranges[metric]
            ranges[metric] = (min(min_val, value), max(max_val, value))

    return ranges


def determine_histogram_bar_order(data, limit):
    """Determine the order of bars in the histogram. Not that the data show is still the top N entries."""

    data = list(data)[:limit]

    if PARAMETERS['CATEGORY_BAR_ORDER'] == 'ASC':
        data = sorted(data, key=lambda x: x[1])

    elif PARAMETERS['CATEGORY_BAR_ORDER'] == 'DESC':
        data = sorted(data, key=lambda x: x[1], reverse=True)

    elif PARAMETERS['CATEGORY_BAR_ORDER'] == 'ALPHABETICAL':
        data = sorted(data, key=lambda x: x[0])

    return zip(*data)


def radar_factory(num_vars, frame='circle'):
    """
    Create a radar chart with `num_vars` Axes.

    This function creates a RadarAxes projection and registers it.

    Parameters
    ----------
    num_vars : int
        Number of variables for radar chart.
    frame : {'circle', 'polygon'}
        Shape of frame surrounding Axes.

    * This function is a modified version of the original radar_factory function from the Matplotlib library.
    * Link: https://matplotlib.org/stable/gallery/specialty_plots/radar_chart.html
    """

    # calculate evenly-spaced axis angles
    theta = np.linspace(0, 2 * np.pi, num_vars, endpoint=False)

    class RadarTransform(PolarAxes.PolarTransform):
        def transform_path_non_affine(self, path):
            # Paths with non-unit interpolation steps correspond to gridlines,
            # in which case we force interpolation (to defeat PolarTransform's
            # autoconversion to circular arcs).
            if path._interpolation_steps > 1:
                path = path.interpolated(num_vars)

            return Path(self.transform(path.vertices), path.codes)

    class RadarAxes(PolarAxes):
        name = 'radar'
        PolarTransform = RadarTransform

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.set_theta_zero_location('N')

        def fill(self, *args, closed=True, **kwargs):
            """Override fill so that line is closed by default"""
            return super().fill(closed=closed, *args, **kwargs)

        def plot(self, *args, **kwargs):
            """Override plot so that line is closed by default"""
            lines = super().plot(*args, **kwargs)
            for line in lines:
                self._close_line(line)

        def _close_line(self, line):
            x, y = line.get_data()
            if x[0] != x[-1]:
                x = np.append(x, x[0])
                y = np.append(y, y[0])
                line.set_data(x, y)

        def set_varlabels(self, labels):
            self.set_thetagrids(np.degrees(theta), labels)

        def _gen_axes_patch(self):
            if frame == 'circle':
                return Circle((0.5, 0.5), 0.5)
            
            elif frame == 'polygon':
                return RegularPolygon((0.5, 0.5), num_vars, radius=.5, edgecolor="k")
            
            else:
                raise ValueError(f"Unknown value for 'frame': {frame}")

        def _gen_axes_spines(self):
            if frame == 'circle':
                return super()._gen_axes_spines()

            elif frame == 'polygon':
                # spine_type must be 'left'/'right'/'top'/'bottom'/'circle'.
                spine = Spine(axes=self, spine_type='circle', path=Path.unit_regular_polygon(num_vars))
                # unit_regular_polygon gives a polygon of radius 1 centered at
                # (0, 0) but we want a polygon of radius 0.5 centered at (0.5,
                # 0.5) in axes coordinates.
                spine.set_transform(Affine2D().scale(.5).translate(.5, .5) + self.transAxes)
                return {'polar': spine}
            
            else:
                raise ValueError(f"Unknown value for 'frame': {frame}")

    register_projection(RadarAxes)
    return theta


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
        ax.set_ylim(0, int(max(message_counts) * 1.05))
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

    Y = 0.90
    if PARAMETERS['ACTIVITY_SHOW_FIRST_MESSAGE']:
        plt.figtext(0.88, (Y:=Y-0.05), f"First Message: {start_date_dt.strftime('%Y-%m-%d')}", ha='right', va='top', fontsize=10, color=PARAMETERS['TEXT_COLOR'])

    if (N:=PARAMETERS['ACTIVITY_SHOW_TOP_ACTIVE_DAYS']):
        most_active_days = sorted(activity_data, key=activity_data.get, reverse=True)[:min(N, len(activity_data))]
        for i, day in enumerate(most_active_days, 1):
            plt.figtext(0.88, (Y:=Y-0.05), f"#{i}: {day} ({activity_data[day]} messages)", ha='right', va='top', fontsize=10, color=PARAMETERS['TEXT_COLOR'])

    if PARAMETERS['ACTIVITY_SHOW_RATIOS'] and activity_factor != -1:
        plt.figtext(0.88, (Y:=Y-0.05), f"Activeness: {(user_data['messages_per_day'] * 150 / activity_factor):.2f}%", ha='right', va='top', fontsize=10, color=PARAMETERS['TEXT_COLOR'])
        plt.figtext(0.88, (Y:=Y-0.05), f"Touch-Grass Rate: {100 - (user_data['messages_per_day'] * 100 / activity_factor):.2f}%", ha='right', va='top', fontsize=10, color=PARAMETERS['TEXT_COLOR'])

    def init():
        line.set_data([], [])
        return line,
    
    def update(frame):
        line.set_data(date_list[:frame+1], message_counts[:frame+1])
        return line,

    if PARAMETERS['ACTIVITY_ANIMATION_MODE'] == 'DURATION':
        interval = PARAMETERS['ACTIVITY_ANIMATION_FIXED_DURATION'] / len(date_list)

    elif PARAMETERS['ACTIVITY_ANIMATION_MODE'] == 'SPEED':
        interval = PARAMETERS['ACTIVITY_ANIMATION_FIXED_SPEED']

    elif PARAMETERS['ACTIVITY_ANIMATION_MODE'] == 'AUTO':
        MIN_FRAMES = PARAMETERS['ACTIVITY_ANIMATION_MIN_FRAMES']
        MAX_FRAMES = PARAMETERS['ACTIVITY_ANIMATION_MAX_FRAMES']
        MIN_DURATION = PARAMETERS['ACTIVITY_ANIMATION_MIN_DURATION']
        MAX_DURATION = PARAMETERS['ACTIVITY_ANIMATION_MAX_DURATION']

        frame_count = len(date_list)
        clamped_frame_count = max(MIN_FRAMES, min(MAX_FRAMES, frame_count))

        total_duration = MIN_DURATION + (MAX_DURATION - MIN_DURATION) * ((clamped_frame_count - MIN_FRAMES) / (MAX_FRAMES - MIN_FRAMES))
        interval = total_duration / frame_count

    else:
        raise ValueError(f"Invalid animation mode: {PARAMETERS['ACTIVITY_ANIMATION_MODE']}")
    
    ani = animation.FuncAnimation(fig, update, frames=len(date_list), init_func=init, interval=interval, blit=True)
    
    if SHOW_PLOTS:
        plt.show()

    if SAVE_PLOTS:
        gif_path = os.path.join(animations_folder, "activity_time.gif")
        ani.save(gif_path, writer='pillow')
        plt.close(fig)


def create_category_histograms_animation(user_id, user_data, animations_folder):
    categories_dict = PARAMETERS['CATEGORIES']
    global_limit = PARAMETERS['CATEGORY_GLOBAL_LIMIT']
    
    for category, limit in categories_dict.items():
        category_data = user_data['top_categories'].get(category, {})

        if not category_data:
            continue

        entry_limit = limit if limit != -1 else global_limit
        labels, counts = determine_histogram_bar_order(category_data.items(), entry_limit)
        
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
                bar.set_color(plt.get_cmap(PARAMETERS['CATEGORY_COLORMAP'])(color_value))
            return bars,
    
        if PARAMETERS['CATEGORY_ANIMATION_MODE'] == 'DURATION':
            interval = PARAMETERS['CATEGORY_ANIMATION_FIXED_DURATION'] / max(counts)

        elif PARAMETERS['CATEGORY_ANIMATION_MODE'] == 'SPEED':
            interval = PARAMETERS['CATEGORY_ANIMATION_FIXED_SPEED']

        elif PARAMETERS['CATEGORY_ANIMATION_MODE'] == 'AUTO':
            MIN_FRAMES = PARAMETERS['CATEGORY_ANIMATION_MIN_FRAMES']
            MAX_FRAMES = PARAMETERS['CATEGORY_ANIMATION_MAX_FRAMES']
            MIN_DURATION = PARAMETERS['CATEGORY_ANIMATION_MIN_DURATION']
            MAX_DURATION = PARAMETERS['CATEGORY_ANIMATION_MAX_DURATION']

            frame_count = max(counts)
            clamped_frame_count = max(MIN_FRAMES, min(MAX_FRAMES, frame_count))

            total_duration = MIN_DURATION + (MAX_DURATION - MIN_DURATION) * ((clamped_frame_count - MIN_FRAMES) / (MAX_FRAMES - MIN_FRAMES))
            interval = total_duration / frame_count

        else:
            raise ValueError(f"Invalid animation mode: {PARAMETERS['CATEGORY_ANIMATION_MODE']}")

        ani = animation.FuncAnimation(fig, update, frames=max(counts) + 1, init_func=init, interval=interval)

        if SHOW_PLOTS:
            plt.show()

        if SAVE_PLOTS:
            category_animations_folder = os.path.join(animations_folder, "category_histograms")
            os.makedirs(category_animations_folder, exist_ok=True)
            gif_path = os.path.join(category_animations_folder, f"{category}.gif")
            ani.save(gif_path, writer='pillow')
            plt.close(fig)


def create_category_histograms_static(user_id, user_data, static_graphs_folder):
    categories_dict = PARAMETERS['CATEGORIES']
    global_limit = PARAMETERS['CATEGORY_GLOBAL_LIMIT']

    for category, limit in categories_dict.items():
        category_data = user_data['top_categories'].get(category, {})

        if not category_data:
            continue

        entry_limit = limit if limit != -1 else global_limit
        labels, counts = determine_histogram_bar_order(category_data.items(), entry_limit)

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

        bars = ax.bar(labels, counts, color=[plt.get_cmap(PARAMETERS['CATEGORY_COLORMAP'])(count / max(counts)) for count in counts])

        if SHOW_PLOTS:
            plt.show()

        if SAVE_PLOTS:
            category_static_graphs_folder = os.path.join(static_graphs_folder, "category_histograms")
            os.makedirs(category_static_graphs_folder, exist_ok=True)
            png_path = os.path.join(category_static_graphs_folder, f"{category}.png")
            fig.savefig(png_path)
            plt.close(fig)


def create_metrics_radar_chart(data, static_graphs_folder, *, ranges):    
    # Define plot colors
    colors = PARAMETERS['METRICS_RADAR_COLORS']

    # Extract labels and corresponding user data
    metrics = list(ranges.keys())
    data_values = [{key: user_data[key] for key in metrics} for user_data in data.values()]
    
    # Normalize data values
    normalized_values = [normalize_data(user_values, ranges) for user_values in data_values]
    user_data = [list(normalized_values.values()) for normalized_values in normalized_values]    
        
    # Create radar chart
    N = len(metrics)
    theta = radar_factory(N, frame=PARAMETERS['METRICS_RADAR_FRAME'])
    
    fig, ax = plt.subplots(figsize=PARAMETERS['METRICS_RADAR_FIGURE_SIZE'], subplot_kw=dict(projection='radar'))
    fig.subplots_adjust(wspace=0.25, hspace=0.20, top=0.85, bottom=0.05)
    ax.set_rgrids([0.2, 0.4, 0.6, 0.8, 1.0], angle=PARAMETERS['METRICS_RADAR_ANGLE'])
    
    # Plot data
    for d, color in zip(user_data, colors):
        ax.plot(theta, d, color=color, marker='o')
        ax.fill(theta, d, facecolor=color, alpha=0.25, label='_nolegend_')
    
    # Set variable labels
    labels = [metric[0] for metric in PARAMETERS['METRICS_RADAR_METRICS'].values()] or metrics
    ax.set_varlabels(labels)
    
    # Enhance grid lines and labels
    ax.yaxis.grid(True, color=PARAMETERS['METRICS_RADAR_AXIS_COLOR'], linestyle='--', linewidth=0.5)
    ax.xaxis.grid(True, color=PARAMETERS['METRICS_RADAR_AXIS_COLOR'], linestyle='--', linewidth=0.5)
    ax.tick_params(axis='y', labelsize=10, color=PARAMETERS['METRICS_RADAR_AXIS_COLOR'])
    
    names = [user_data['name'] for user_data in data.values()]

    # Add legend
    if PARAMETERS['METRICS_RADAR_SHOW_LEGEND']:
        ax.legend(names, loc=(0.9, .95), labelspacing=0.1, fontsize='small')
    
    # Add title
    if PARAMETERS['METRICS_RADAR_TITLE']:
        fig.text(0.515, 0.925, PARAMETERS['METRICS_RADAR_TITLE'].format(names=names), horizontalalignment='center', color='black', weight='bold', size='large')
    
    if SHOW_PLOTS:
        plt.show()

    if SAVE_PLOTS:
        png_path = os.path.join(static_graphs_folder, "metrics_radar.png")
        fig.savefig(png_path)
        plt.close(fig)


def generate_data(user_stats):
    user_ids = GENERATE_FROM_LIST if GENERATE_FROM_LIST else user_stats.keys()

    # Calculate some global parameters
    max_activeness = max(user_stats[user_id].get('messages_per_day', -1) for user_id in user_ids)

    if GENERATE_METRICS_RADAR:
        if PARAMETERS['METRICS_RADAR_DYNAMIC_PARAMETERS']:
            metrics = PARAMETERS['METRICS_RADAR_METRICS']
            ranges = determine_normalization_ranges(user_stats, metrics=metrics)

        else:
            ranges = {metric: value[1] for metric, value in PARAMETERS['METRICS_RADAR_METRICS'].items()}
    
    for user_id in user_ids:
        user_data = user_stats[user_id]
        user_name = user_data['name']

        print(f"Generating graphs for {user_name}...")

        user_folder = os.path.join(output_folder, f"{user_name}_{user_id}")
        if SAVE_PLOTS and not os.path.exists(user_folder):
            os.makedirs(user_folder)
        
        animations_folder = os.path.join(user_folder, "animations")
        if SAVE_PLOTS and not os.path.exists(animations_folder):
            os.makedirs(animations_folder)
        
        static_graphs_folder = os.path.join(user_folder, "static_graphs")
        if SAVE_PLOTS and not os.path.exists(static_graphs_folder):
            os.makedirs(static_graphs_folder)
        
        if GENERATE_ACTIVITY_CHART:
            create_activity_animation(user_id, user_data, animations_folder, activity_factor=max_activeness)
        
        if GENERATE_CATEGORY_HISTOGRAM_GIFS:
            create_category_histograms_animation(user_id, user_data, animations_folder)

        if GENERATE_CATEGORY_HISTOGRAM_PNGS:
            create_category_histograms_static(user_id, user_data, static_graphs_folder)
        
        if GENERATE_METRICS_RADAR:
            create_metrics_radar_chart({user_id: user_data}, static_graphs_folder, ranges=ranges)


if __name__ == '__main__':
    if SAVE_PLOTS:
        os.makedirs(output_folder, exist_ok=True)

    with open(json_file, 'r', encoding='utf-8') as file:
        stats = json.load(file)

    id = stats.get("id", None)  # Handle global stats
    if id:
        stats = {str(id): stats}

    generate_data(stats)

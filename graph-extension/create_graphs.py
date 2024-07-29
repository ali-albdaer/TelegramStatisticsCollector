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
    ranges = {
        metric: {submetric: (float('inf'), float('-inf')) for submetric in value}
        if isinstance(value, dict)
        else (float('inf'), float('-inf'))
        for metric, value in metrics.items()
    }

    # If we only have 1 user, we can't automatically determine the ranges; we'll just use the user's data and display a warning.
    if len(stats) == 1:
        print("WARNING: Only 1 user found. Set 'METRICS_RADAR: DYNAMIC_PARAMETERS' to False to manually set the normalization ranges.")
        return ranges

    for user_data in stats.values():
        for metric in metrics:
            if '.' in metric:
                main_metric, sub_metric = metric.split('.')
                value = user_data.get(main_metric, {}).get(sub_metric, 0)

            else:
                value = user_data.get(metric, 0)

            min_val, max_val = ranges[metric]
            ranges[metric] = (min(min_val, value), max(max_val, value))

    return ranges


def determine_histogram_bar_order(data, limit, category_bar_order='ASC'):
    """Determine the order of bars in the histogram. Not that the data show is still the top N entries."""

    data = list(data)[:limit]

    if category_bar_order == 'ASC':
        data = sorted(data, key=lambda x: x[1])

    elif category_bar_order == 'DESC':
        data = sorted(data, key=lambda x: x[1], reverse=True)

    elif category_bar_order == 'ALPHABETICAL':
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


def create_activity_animation(
    user_id, 
    user_data, 
    animations_folder,
    *,
    activity_factor=None, 
    figure_size=(9.6, 5.4),
    graph_color='blue',
    graph_background_color='white',
    axis_color='black',
    text_color='black',
    dynamic_parameters=True,
    x_limit=None,
    y_limit=None,
    x_interval=None,
    y_interval=None,
    x_label=None,
    y_label='Amount of Messages Sent',
    title='{name} - Activity Over Time',
    show_dates=True,
    axis_date_format='%Y-%m',
    show_first_message=True,
    show_top_active_days=3,
    show_ratios=True,
    repeat=False,
    repeat_delay=2000,
    animation_mode='AUTO',
    animation_fixed_speed=100,
    animation_fixed_duration=12000,
    animation_min_duration=1000,
    animation_max_duration=12000,
    animation_min_frames=10,
    animation_max_frames=200
):    
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
    fig, ax = plt.subplots(figsize=figure_size)
    fig.patch.set_facecolor(graph_background_color)

    ax.set_facecolor(graph_background_color)
    ax.spines['bottom'].set_color(axis_color)
    ax.spines['left'].set_color(axis_color)
    ax.tick_params(axis='x', colors=axis_color)
    ax.tick_params(axis='y', colors=axis_color)
    ax.yaxis.label.set_color(text_color)
    ax.xaxis.label.set_color(text_color)
    ax.title.set_color(text_color)
    
    # Set the limits and labels
    if dynamic_parameters:
        ax.set_xlim(0, len(date_list))
        ax.set_ylim(0, int(max(message_counts) * 1.05))
        ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
        ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))

    else:
        ax.set_xlim(x_limit)
        ax.set_ylim(y_limit)

        if x_interval:
            ax.xaxis.set_major_locator(plt.MultipleLocator(x_interval))

        if y_interval:
            ax.yaxis.set_major_locator(plt.MultipleLocator(y_interval))

    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title.format(name=user_data['name'], id=user_id))

    if show_dates:
        ax.set_xticks(range(0, len(date_list), x_interval or max(1, len(date_list) // 10)))
        ax.set_xticklabels([(start_date_dt + timedelta(days=i)).strftime(axis_date_format) for i in range(0, len(date_list), x_interval or max(1, len(date_list) // 10))], rotation=45)

    else:
        ax.xaxis.set_major_locator(plt.MultipleLocator(x_interval or max(1, len(date_list) // 10)))

    line, = ax.plot([], [], marker='o', color=graph_color)

    Y = 0.90
    if show_first_message:
        plt.figtext(0.88, (Y:=Y-0.05), f"First Message: {start_date_dt.strftime('%Y-%m-%d')}", ha='right', va='top', fontsize=10, color=text_color)

    if (N:=show_top_active_days):
        most_active_days = sorted(activity_data, key=activity_data.get, reverse=True)[:min(N, len(activity_data))]
        for i, day in enumerate(most_active_days, 1):
            plt.figtext(0.88, (Y:=Y-0.05), f"#{i}: {day} ({activity_data[day]} messages)", ha='right', va='top', fontsize=10, color=text_color)

    if show_ratios and activity_factor != -1:
        plt.figtext(0.88, (Y:=Y-0.05), f"Activeness: {(user_data['ratios']['messages_per_day'] * 150 / activity_factor):.2f}%", ha='right', va='top', fontsize=10, color=text_color)
        plt.figtext(0.88, (Y:=Y-0.05), f"Touch-Grass Rate: {100 - (user_data['ratios']['messages_per_day'] * 100 / activity_factor):.2f}%", ha='right', va='top', fontsize=10, color=text_color)

    def init():
        line.set_data([], [])
        return line,
    
    def update(frame):
        line.set_data(date_list[:frame+1], message_counts[:frame+1])
        return line,

    if animation_mode == 'DURATION':
        interval = animation_fixed_duration / len(date_list)

    elif animation_mode == 'SPEED':
        interval = animation_fixed_speed

    elif animation_mode == 'AUTO':
        MIN_FRAMES = animation_min_frames
        MAX_FRAMES = animation_max_frames
        MIN_DURATION = animation_min_duration
        MAX_DURATION = animation_max_duration

        frame_count = len(date_list)
        clamped_frame_count = max(MIN_FRAMES, min(MAX_FRAMES, frame_count))

        total_duration = MIN_DURATION + (MAX_DURATION - MIN_DURATION) * ((clamped_frame_count - MIN_FRAMES) / (MAX_FRAMES - MIN_FRAMES))
        interval = total_duration / frame_count

    else:
        raise ValueError(f"Invalid animation mode: {animation_mode}")
    
    ani = animation.FuncAnimation(fig, update, frames=len(date_list), init_func=init, interval=interval, blit=True, repeat=repeat, repeat_delay=repeat_delay)
    
    if SHOW_PLOTS:
        plt.show()

    if SAVE_PLOTS:
        gif_path = os.path.join(animations_folder, "activity_time.gif")
        ani.save(gif_path, writer='pillow')
        plt.close(fig)


def create_category_histograms_animation(
    user_id, 
    user_data, 
    animations_folder,
    *,
    categories_dict,
    global_limit,
    category_bar_order='ASC',
    figure_size=(9.6, 5.4),
    graph_background_color='white',
    axis_color='black',
    text_color='black',
    dynamic_parameters=True,
    x_limit=None,
    y_limit=None,
    x_label=None,
    y_label=None,
    title='{name} - {category_name}',
    colormap='viridis',
    repeat=False,
    repeat_delay=2000,
    animation_mode='AUTO',
    animation_fixed_speed=100,
    animation_fixed_duration=12000,
    animation_min_duration=1000,
    animation_max_duration=12000,
    animation_min_frames=10,
    animation_max_frames=200
):
    
    for category, limit in categories_dict.items():
        category_data = user_data['top_categories'].get(category, {})

        if not category_data:
            continue

        entry_limit = limit if limit != -1 else global_limit
        labels, counts = determine_histogram_bar_order(category_data.items(), entry_limit, category_bar_order)
        
        fig, ax = plt.subplots(figsize=figure_size)
        fig.patch.set_facecolor(graph_background_color)

        ax.set_facecolor(graph_background_color)
        ax.spines['bottom'].set_color(axis_color)
        ax.spines['left'].set_color(axis_color)
        ax.tick_params(axis='x', colors=axis_color)
        ax.tick_params(axis='y', colors=axis_color)
        ax.yaxis.label.set_color(text_color)
        ax.xaxis.label.set_color(text_color)
        ax.title.set_color(text_color)

        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.set_title(title.format(name=user_data['name'], id=user_id, category_name=category))

        if dynamic_parameters:
            ax.set_xlim(-0.5, len(labels) - 0.5)
            ax.set_ylim(0, max(counts) + 10)
        else:
            ax.set_xlim(x_limit)
            ax.set_ylim(y_limit)

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
                bar.set_color(plt.get_cmap(colormap)(color_value))
            return bars,
    
        if animation_mode == 'DURATION':
            interval = animation_fixed_duration / max(counts)

        elif animation_mode == 'SPEED':
            interval = animation_fixed_speed

        elif animation_mode == 'AUTO':
            MIN_FRAMES = animation_min_frames
            MAX_FRAMES = animation_max_frames
            MIN_DURATION = animation_min_duration
            MAX_DURATION = animation_max_duration

            frame_count = max(counts)
            clamped_frame_count = max(MIN_FRAMES, min(MAX_FRAMES, frame_count))

            total_duration = MIN_DURATION + (MAX_DURATION - MIN_DURATION) * ((clamped_frame_count - MIN_FRAMES) / (MAX_FRAMES - MIN_FRAMES))
            interval = total_duration / frame_count

        else:
            raise ValueError(f"Invalid animation mode: {animation_mode}")

        ani = animation.FuncAnimation(fig, update, frames=max(counts) + 1, init_func=init, interval=interval, blit=True, repeat=repeat, repeat_delay=repeat_delay)

        if SHOW_PLOTS:
            plt.show()

        if SAVE_PLOTS:
            category_animations_folder = os.path.join(animations_folder, "category_histograms")
            os.makedirs(category_animations_folder, exist_ok=True)
            gif_path = os.path.join(category_animations_folder, f"{category}.gif")
            ani.save(gif_path, writer='pillow')
            plt.close(fig)


def create_category_histograms_static(
    user_id, 
    user_data, 
    static_graphs_folder,
    *,
    categories_dict,
    global_limit,
    category_bar_order='ASC',
    figure_size=(9.6, 5.4),
    graph_background_color='white',
    axis_color='black',
    text_color='black',
    dynamic_parameters=True,
    x_limit=None,
    y_limit=None,
    x_label=None,
    y_label=None,
    title='{name} - {category_name}',
    colormap='viridis'
):

    for category, limit in categories_dict.items():
        category_data = user_data['top_categories'].get(category, {})

        if not category_data:
            continue

        entry_limit = limit if limit != -1 else global_limit
        labels, counts = determine_histogram_bar_order(category_data.items(), entry_limit, category_bar_order)

        fig, ax = plt.subplots(figsize=figure_size)
        fig.patch.set_facecolor(graph_background_color)

        ax.set_facecolor(graph_background_color)
        ax.spines['bottom'].set_color(axis_color)
        ax.spines['left'].set_color(axis_color)
        ax.tick_params(axis='x', colors=axis_color)
        ax.tick_params(axis='y', colors=axis_color)
        ax.yaxis.label.set_color(text_color)
        ax.xaxis.label.set_color(text_color)
        ax.title.set_color(text_color)

        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.set_title(title.format(name=user_data['name'], id=user_id, category_name=category))

        if dynamic_parameters:
            ax.set_xlim(-0.5, len(labels) - 0.5)
            ax.set_ylim(0, max(counts) + 10)
        else:
            ax.set_xlim(x_limit)
            ax.set_ylim(y_limit)

        bars = ax.bar(labels, counts, color=[plt.get_cmap(colormap)(count / max(counts)) for count in counts])

        if SHOW_PLOTS:
            plt.show()

        if SAVE_PLOTS:
            category_static_graphs_folder = os.path.join(static_graphs_folder, "category_histograms")
            os.makedirs(category_static_graphs_folder, exist_ok=True)
            png_path = os.path.join(category_static_graphs_folder, f"{category}.png")
            fig.savefig(png_path)
            plt.close(fig)


def create_radar_chart(
    data, 
    static_graphs_folder, 
    *,
    ranges,
    radar_metrics,
    radar_colors,
    figure_size=(9.6, 5.4),
    frame='circle',
    show_legend=True,
    title=None,
    axis_angle=45,
    axis_color='black'
):
    
    # Extract labels and corresponding user data
    metrics = list(ranges.keys())

    """
    Example metric structure:

    metrics = {
        'message_count': (0, 1000),
        'media_count': (0, 100),
        'ratios.messages_per_day': (0, 100),  # Handling nested metrics
        'ratios.words_per_message': (0, 100),
    }
    """

    data_values = [
        {
            key: user_data[key.split('.')[0]][key.split('.')[1]] if '.' in key 
            else user_data[key]
            for key in metrics
        }
        for user_data in data.values()
    ]
    
    # Normalize data values
    normalized_values = [normalize_data(user_values, ranges) for user_values in data_values]
    user_data = [list(normalized_values.values()) for normalized_values in normalized_values]
        
    # Create radar chart
    N = len(metrics)
    theta = radar_factory(N, frame=frame)
    
    fig, ax = plt.subplots(figsize=figure_size, subplot_kw=dict(projection='radar'))
    fig.subplots_adjust(wspace=0.25, hspace=0.20, top=0.85, bottom=0.05)
    ax.set_rgrids([0.2, 0.4, 0.6, 0.8, 1.0], angle=axis_angle)
    
    # Plot data
    for d, color in zip(user_data, radar_colors):
        ax.plot(theta, d, color=color, marker='o')
        ax.fill(theta, d, facecolor=color, alpha=0.25, label='_nolegend_')
    
    # Set variable labels
    labels = [metric[0] for metric in radar_metrics.values()] or metrics
    ax.set_varlabels(labels)
    
    # Enhance grid lines and labels
    ax.yaxis.grid(True, color=axis_color, linestyle='--', linewidth=0.5)
    ax.xaxis.grid(True, color=axis_color, linestyle='--', linewidth=0.5)
    ax.tick_params(axis='y', labelsize=10, color=axis_color)
    
    names = [user_data['name'] for user_data in data.values()]

    # Add legend
    if show_legend:
        ax.legend(names, loc=(0.9, .95), labelspacing=0.1, fontsize='small')
    
    # Add title
    if title:
        fig.text(0.515, 0.925, title.format(names=names), horizontalalignment='center', color='black', weight='bold', size='large')
    
    if SHOW_PLOTS:
        plt.show()

    if SAVE_PLOTS:
        png_path = os.path.join(static_graphs_folder, "metrics_radar.png")
        fig.savefig(png_path)
        plt.close(fig)


def generate_data(user_stats):
    if not GENERATE_FROM_LIST:
        user_ids = list(user_stats.keys())

    else:
        user_ids = [user_id for user_id in user_stats.keys() if user_id in GENERATE_FROM_LIST]

    # Calculate some global parameters
    if GENERATE_ACTIVITY_CHART:
        max_activeness = max(user_stats[user_id]['ratios'].get('messages_per_day', -1) for user_id in user_ids) if ACTIVITY_PARAMS['SHOW_RATIOS'] else -1

    if GENERATE_METRICS_RADAR:
        if METRICS_RADAR_PARAMS['DYNAMIC_PARAMETERS']:
            metrics = METRICS_RADAR_PARAMS['METRICS']
            metric_ranges = determine_normalization_ranges(user_stats, metrics=metrics)

        else:
            metric_ranges = {metric: value[1] for metric, value in METRICS_RADAR_PARAMS['METRICS'].items()}

    if GENERATE_FEELINGS_RADAR:
        if FEELINGS_RADAR_PARAMS['DYNAMIC_PARAMETERS']:
            feelings = FEELINGS_RADAR_PARAMS['FEELINGS']
            feeling_ranges = determine_normalization_ranges(user_stats, metrics=feelings)

        else:
            feeling_ranges = {feeling: value[1] for feeling, value in FEELINGS_RADAR_PARAMS['FEELINGS'].items()}
    
    # Generate graphs for each user
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
            create_activity_animation(
                user_id, 
                user_data, 
                animations_folder, 
                activity_factor=max_activeness,
                figure_size=ACTIVITY_PARAMS['FIGURE_SIZE'],
                graph_color=ACTIVITY_PARAMS['GRAPH_COLOR'],
                graph_background_color=ACTIVITY_PARAMS['GRAPH_BACKGROUND_COLOR'],
                axis_color=ACTIVITY_PARAMS['AXIS_COLOR'],
                text_color=ACTIVITY_PARAMS['TEXT_COLOR'],
                dynamic_parameters=ACTIVITY_PARAMS['DYNAMIC_PARAMETERS'],
                x_limit=ACTIVITY_PARAMS['X_LIMIT'],
                y_limit=ACTIVITY_PARAMS['Y_LIMIT'],
                x_interval=ACTIVITY_PARAMS['X_INTERVAL'],
                y_interval=ACTIVITY_PARAMS['Y_INTERVAL'],
                x_label=ACTIVITY_PARAMS['X_LABEL'],
                y_label=ACTIVITY_PARAMS['Y_LABEL'],
                title=ACTIVITY_PARAMS['TITLE'],
                show_dates=ACTIVITY_PARAMS['SHOW_DATES'],
                axis_date_format=ACTIVITY_PARAMS['AXIS_DATE_FORMAT'],
                show_first_message=ACTIVITY_PARAMS['SHOW_FIRST_MESSAGE'],
                show_top_active_days=ACTIVITY_PARAMS['SHOW_TOP_ACTIVE_DAYS'],
                show_ratios=ACTIVITY_PARAMS['SHOW_RATIOS'],
                repeat=ACTIVITY_PARAMS['REPEAT'],
                repeat_delay=ACTIVITY_PARAMS['REPEAT_DELAY'],
                animation_mode=ACTIVITY_PARAMS['ANIMATION_MODE'],
                animation_fixed_speed=ACTIVITY_PARAMS['ANIMATION_FIXED_SPEED'],
                animation_fixed_duration=ACTIVITY_PARAMS['ANIMATION_FIXED_DURATION'],
                animation_min_duration=ACTIVITY_PARAMS['ANIMATION_MIN_DURATION'],
                animation_max_duration=ACTIVITY_PARAMS['ANIMATION_MAX_DURATION'],
                animation_min_frames=ACTIVITY_PARAMS['ANIMATION_MIN_FRAMES'],
                animation_max_frames=ACTIVITY_PARAMS['ANIMATION_MAX_FRAMES']
            )
        
        if GENERATE_CATEGORY_HISTOGRAM_GIFS:
            create_category_histograms_animation(
                user_id, 
                user_data, 
                animations_folder,
                categories_dict=CATEGORY_PARAMS['CATEGORIES'],
                global_limit=CATEGORY_PARAMS['GLOBAL_LIMIT'],
                category_bar_order=CATEGORY_PARAMS['BAR_ORDER'],
                figure_size=CATEGORY_PARAMS['FIGURE_SIZE'],
                graph_background_color=CATEGORY_PARAMS['GRAPH_BACKGROUND_COLOR'],
                axis_color=CATEGORY_PARAMS['AXIS_COLOR'],
                text_color=CATEGORY_PARAMS['TEXT_COLOR'],
                dynamic_parameters=CATEGORY_PARAMS['DYNAMIC_PARAMETERS'],
                x_limit=CATEGORY_PARAMS['X_LIMIT'],
                y_limit=CATEGORY_PARAMS['Y_LIMIT'],
                x_label=CATEGORY_PARAMS['X_LABEL'],
                y_label=CATEGORY_PARAMS['Y_LABEL'],
                title=CATEGORY_PARAMS['TITLE'],
                colormap=CATEGORY_PARAMS['COLORMAP'],
                repeat=CATEGORY_PARAMS['REPEAT'],
                repeat_delay=CATEGORY_PARAMS['REPEAT_DELAY'],
                animation_mode=CATEGORY_PARAMS['ANIMATION_MODE'],
                animation_fixed_speed=CATEGORY_PARAMS['ANIMATION_FIXED_SPEED'],
                animation_fixed_duration=CATEGORY_PARAMS['ANIMATION_FIXED_DURATION'],
                animation_min_duration=CATEGORY_PARAMS['ANIMATION_MIN_DURATION'],
                animation_max_duration=CATEGORY_PARAMS['ANIMATION_MAX_DURATION'],
                animation_min_frames=CATEGORY_PARAMS['ANIMATION_MIN_FRAMES'],
                animation_max_frames=CATEGORY_PARAMS['ANIMATION_MAX_FRAMES']
            )

        if GENERATE_CATEGORY_HISTOGRAM_PNGS:
            create_category_histograms_static(
                user_id, 
                user_data, 
                static_graphs_folder,
                categories_dict=CATEGORY_PARAMS['CATEGORIES'],
                global_limit=CATEGORY_PARAMS['GLOBAL_LIMIT'],
                category_bar_order=CATEGORY_PARAMS['BAR_ORDER'],
                figure_size=CATEGORY_PARAMS['FIGURE_SIZE'],
                graph_background_color=CATEGORY_PARAMS['GRAPH_BACKGROUND_COLOR'],
                axis_color=CATEGORY_PARAMS['AXIS_COLOR'],
                text_color=CATEGORY_PARAMS['TEXT_COLOR'],
                dynamic_parameters=CATEGORY_PARAMS['DYNAMIC_PARAMETERS'],
                x_limit=CATEGORY_PARAMS['X_LIMIT'],
                y_limit=CATEGORY_PARAMS['Y_LIMIT'],
                x_label=CATEGORY_PARAMS['X_LABEL'],
                y_label=CATEGORY_PARAMS['Y_LABEL'],
                title=CATEGORY_PARAMS['TITLE'],
                colormap=CATEGORY_PARAMS['COLORMAP']
            )
        
        if GENERATE_METRICS_RADAR:
            create_radar_chart(
                {user_id: user_data}, 
                static_graphs_folder, 
                ranges=metric_ranges,
                radar_metrics=METRICS_RADAR_PARAMS['METRICS'],
                radar_colors=METRICS_RADAR_PARAMS['COLORS'],
                figure_size=METRICS_RADAR_PARAMS['FIGURE_SIZE'],
                frame=METRICS_RADAR_PARAMS['FRAME'],
                show_legend=METRICS_RADAR_PARAMS['SHOW_LEGEND'],
                title=METRICS_RADAR_PARAMS['TITLE'],
                axis_angle=METRICS_RADAR_PARAMS['ANGLE'],
                axis_color=METRICS_RADAR_PARAMS['AXIS_COLOR']
            )

        if GENERATE_FEELINGS_RADAR:
            create_radar_chart(
                {user_id: user_data}, 
                static_graphs_folder, 
                ranges=feeling_ranges,
                radar_metrics=FEELINGS_RADAR_PARAMS['FEELINGS'],
                radar_colors=FEELINGS_RADAR_PARAMS['COLORS'],
                figure_size=FEELINGS_RADAR_PARAMS['FIGURE_SIZE'],
                frame=FEELINGS_RADAR_PARAMS['FRAME'],
                show_legend=FEELINGS_RADAR_PARAMS['SHOW_LEGEND'],
                title=FEELINGS_RADAR_PARAMS['TITLE'],
                axis_angle=FEELINGS_RADAR_PARAMS['ANGLE'],
                axis_color=FEELINGS_RADAR_PARAMS['AXIS_COLOR']
            )


if __name__ == '__main__':
    if SAVE_PLOTS:
        os.makedirs(output_folder, exist_ok=True)

    with open(json_file, 'r', encoding='utf-8') as file:
        stats = json.load(file)

    id = stats.get("id", None)  # Handle global stats
    if id:
        stats = {str(id): stats}

    generate_data(stats)

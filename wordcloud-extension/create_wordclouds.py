import os
import shutil
import json
import re
import wordcloud
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from config import *


def create_wordcloud(words, title, filepath, max_words=WORD_COUNT):
    mask = np.array(Image.open(MASK)) if MASK else None
    wc = wordcloud.WordCloud(
        width=SIZE[0], height=SIZE[1],
        min_font_size=MIN_FONT_SIZE,
        background_color=BACKGROUND_COLOR,
        max_words=max_words,
        colormap=COLOR_MAP(),
        mask=mask,
    ).generate_from_frequencies(words, max_font_size=MAX_FONT_SIZE)
    
    image = Image.new(COLOR_MODE, FRAME_SIZE, color=BACKGROUND_COLOR)
    wc_image = wc.to_image()
    image.paste(wc_image, ((FRAME_SIZE[0] - SIZE[0]) // 2, (FRAME_SIZE[1] - SIZE[1]) // 2))
    
    if SHOW_TITLES:
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype("arial.ttf", 36)
        bbox = draw.textbbox((0, 0), title, font=font)
        text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(((FRAME_SIZE[0] - text_width) / 2, 20), title, font=font, fill=FONT_COLOR)
    
    if INCREASE_FILE_INDEX:
        base_name, ext = os.path.splitext(filepath)
        index = 1
        while os.path.exists(filepath):
            filepath = generate_filename(base_name, index, ext)
            index += 1

    image.save(filepath)

def process_user_data(user_data):
    id = str(user_data["id"])
    user_name = user_data["name"]

    if REMOVE_ACCENTS_IN_WORDS:
        user_data = {key: {word.translate(str.maketrans(ACCENTED_CHARS)) if isinstance(word, str) else word: count for word, count in data.items()} for key, data in user_data.items()}

    if REMOVE_ACCENTS_IN_FILENAMES:
        for letter, accents in ACCENTED_CHARS.items():
            user_name = re.sub(f'[{accents}]', letter, user_name)

    user_name = user_name.replace(" ", "_").lower() + (f"_{id}" if IDS_IN_FILENAMES else "")
    user_folder = os.path.join(output_folder, user_name) 
    
    os.makedirs(user_folder, exist_ok=True)
    top_words_folder = os.path.join(user_folder, word_data)
    categories_gif_folder = os.path.join(user_folder, "categories_gif")
    
    os.makedirs(top_words_folder, exist_ok=True)
    os.makedirs(categories_gif_folder, exist_ok=True)

    if os.path.exists(os.path.join(user_folder, "categories_png")):
        index = 1
        while os.path.exists(os.path.join(user_folder, f"categories_png_{index}")):
            index += 1
        
        categories_png_folder = os.path.join(user_folder, f"categories_png_{index}")

    else:
        categories_png_folder = os.path.join(user_folder, "categories_png") 

    os.makedirs(categories_png_folder, exist_ok=True)
    
    top_words = {word: count for word, count in user_data[word_data].items()}
    filtered_words = {word: count for word, count in top_words.items() if word not in common_words}
    
    create_wordcloud(top_words, unfiltered_title_format.format(user_data['name'], WORD_COUNT), os.path.join(top_words_folder, generate_filename(f"{user_name}_top_{WORD_COUNT}_words_unfiltered")))
    create_wordcloud(filtered_words, filtered_title_format.format(user_data["name"], WORD_COUNT), os.path.join(top_words_folder, generate_filename(f"{user_name}_top_{WORD_COUNT}_unique_words")))
    
    png_filepaths = []
    for category, words in user_data.get(category_data, {}).items():
        if category not in category_title_formats and SKIP_UNKNOWN_CATEGORIES:
            continue
        
        if category in category_title_formats:
            category_title = category_title_formats[category].format(user_data['name'])

        else:
            category_title = default_title_format.format(user_data['name'], category)

        if len(words) >= MIN_CATEGORY_WORDS:
            png_filepath = os.path.join(categories_png_folder, generate_filename(f"{user_name}_top_{CATEGORY_WORD_COUNT}_words_{category}"))
            create_wordcloud(words, category_title, png_filepath, max_words=CATEGORY_WORD_COUNT)
            png_filepaths.append(png_filepath)
    
    gif_frames = []
    if SHOW_GIF_TITLE_FRAME:
        title_frame = Image.new(COLOR_MODE, FRAME_SIZE, color=BACKGROUND_COLOR)
        draw = ImageDraw.Draw(title_frame)
        font = ImageFont.truetype("arial.ttf", 36)
        _text = title_frame_format.format(user_data['name'], CATEGORY_WORD_COUNT)
        text_width, text_height = draw.textsize(_text, font=font)
        draw.text(((FRAME_SIZE[0] - text_width) / 2, (FRAME_SIZE[1] - text_height) / 2), _text, font=font, fill=FONT_COLOR)
        gif_frames.append(title_frame)
    
    for png_filepath in png_filepaths:
        if os.path.exists(png_filepath):
            gif_frames.append(Image.open(png_filepath))
    
    if gif_frames:
        gif_filepath = os.path.join(categories_gif_folder, generate_filename(f"{user_name}_top_{CATEGORY_WORD_COUNT}_words_categorized", extension=".gif"))
        if INCREASE_FILE_INDEX:
            base_name, ext = os.path.splitext(gif_filepath)
            index = 1
            while os.path.exists(gif_filepath):
                gif_filepath = generate_filename(base_name, index, ext)
                index += 1
        gif_frames[0].save(gif_filepath, save_all=True, append_images=gif_frames[1:], duration=FRAME_DURATION, loop=LOOPS)

    if not KEEP_FRAMES:
        shutil.rmtree(categories_png_folder)


if __name__ == "__main__":
    with open(json_file, "r", encoding="utf-8") as f:
        stats = json.load(f)

    id = stats.get("id", None)
    if id:
        stats = {str(id): stats}

    if user_ids and GENERATE_FROM_LIST:
        stats = {str(id): stats[str(id)] for id in user_ids if str(id) in user_ids}

    elif user_ids and not GENERATE_FROM_LIST:
        stats = {str(id): stats[str(id)] for id in stats if str(id) not in user_ids}

    else:
        pass

    processed_users = 0
    total_users = len(stats)
    
    if not total_users:
        print("No users to process.")
        exit()

    for id, user_data in stats.items():
        process_user_data(user_data)

        processed_users += 1
        print(f"Processed Users: [{processed_users}/{total_users}]", end="\r")
    
    print("[ Program Finished. ] ")

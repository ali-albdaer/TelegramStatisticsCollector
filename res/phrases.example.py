"""
Change the name of this file to `phrases.py` or create a new file named `phrases.py` in this directory.

This file contains all keywords / phrases that will be collected and analyzed. (except curse words which are stored in `res/explicit.py`)
By default, everything is treated as case-insensitive. You may change the `CASE_INSENSITIVE` flag in `res/config.py`.

`category_sets`: A dictionary of categories with sets of keywords or phrases. 
Use tuples for aliases, e.g. ('james', 'jimmy', 'jim') will match any of 'james', 'jimmy' or 'jim' and store them as 'james' (first entry).
You can have the same words across multiple categories. For example, 'apple' can be in both 'fruits' and 'companies'.

`ignored_words`: Words that should be ignored in the analysis. The words will still be counted but not shown as top_words.
By default nothing is ignored. Set `IGNORE_COMMON_WORDS` in `config.py` to `True` to ignore these words.
"""


from res.explicit import curses


category_sets = {  # Words only, no phrases
    'names': {('james', 'jimmy', 'jim'), 'rose', ('michael', 'mike'), ('jessica', 'jess')}, # Use tuple for aliases
    'fruits': {'apple', 'banana', 'pineapple', 'durian', 'mango', 'orange', 'grape', 'kiwi', 'strawberry', 'watermelon'},
    'companies': {'apple', 'microsoft', 'google', 'amazon', 'facebook', 'tesla', 'netflix', 'twitter', 'uber'},
    'countries': {('united states of america', 'united states', 'usa'), 'canada', 'mexico', ('united kingdom', 'uk')},  # Longest phrase first
    'animals': {'dog', 'cat', 'elephant', 'giraffe', 'lion', 'tiger', 'bear', 'panda', 'koala', 'kangaroo'},
    'colors': {'red', 'blue', 'green', 'yellow', 'orange', 'purple', 'black', 'white', 'brown', 'pink'},
    'numbers': set(map(str, range(1001))),  # Make sure to use strings.
    'responses': {'yes', 'no', 'maybe'},
    'common phrases': {('thank you', 'thanks', 'ty', 'thx'), ('good morning', 'goodmorning', 'gm'), ('good night', 'goodnight', 'gn')},
    'curses': curses,  # Imported from explicit.py
}

ignored_words = {  # Set IGNORE_COMMON_WORDS in res/config.py to True to ignore these words.
    'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'it', 
    'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at', 'this', 
    'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she', 
    'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 
    'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 
    'go', 'me', 'i', 'when', 'make', 'is', 'was', 'am', 'are',
}

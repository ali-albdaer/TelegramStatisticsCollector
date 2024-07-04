"""
This file contains all keywords that should be collected and analyzed.
* By default, everything is treated as case-insensitive. You may change the flag `CASE_INSENSITIVE` in config.py.

category_sets: A dictionary of categories with sets of words. The keys are the category names and the values are sets of words.
* Use tuples for aliases, e.g. ('james', 'jimmy', 'jim') will match 'james' and 'jimmy' and 'jim' and store them 'james' (first entry).

ignored_words: Words that should be ignored in the analysis. The words will still be counted but not shown as top_words.
* Set IGNORE_COMMON_WORDS in config.py to True to ignore these words.

curses: Words that are considered curses. They are used to calculate the "naughtiness ratio".
* The "naughtiness ratio" is the ratio of curse words to total words used by a user.
"""

category_sets = {  # Words only, no phrases
    'people': {('james', 'jimmy', 'jim'), 'rose', ('michael', 'mike'), ('jessica', 'jess')}, # Use tuple for aliases
    'fruits': {'apple', 'banana', 'pineapple', 'durian', 'mango', 'orange', 'grape', 'kiwi', 'strawberry', 'watermelon'},
    'countries': {('usa', 'america'), 'canada', 'mexico', 'panama', ('uk', 'britian')},  # Use tuple for aliases
    'animals': {'dog', 'cat', 'elephant', 'giraffe', 'lion', 'tiger', 'bear', 'panda', 'koala', 'kangaroo'},
    'colors': {'red', 'blue', 'green', 'yellow', 'orange', 'purple', 'black', 'white', 'brown', 'pink'},
    'numbers': set(map(str, range(1001))),  # Make sure to use strings.
    'celebrities': {'musk', 'bezos', 'gates', 'zuckerberg'},
    'responses': {'yes', 'no', 'maybe'},
}

ignored_words = {
    'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'it', 
    'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at', 'this', 
    'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she', 
    'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 
    'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 
    'go', 'me', 'i', 'when', 'make'
}

curses = {"slubberdagullion", "gobemouche", "fopdoodle", "tatterdemalion", "scallywag"}

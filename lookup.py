"""
This file contains all keywords that should be collected and analyzed.
* By default, everything is treated as case-insensitive. You may change the flag `CASE_INSENSITIVE` in config.py.

category_sets: A dictionary of categories with sets of words. The keys are the category names and the values are sets of words.
* Use tuples for aliases, e.g. ('usa', 'america') will match both 'usa' and 'america' and store them as 'usa' (first entry).

ignored_words: Words that should be ignored in the analysis. The words will still be counted but not shown as top_words.
* Set IGNORE_COMMON_WORDS in config.py to True to ignore these words.

curses: Words that are considered curses. They are used to calculate the "naughtiness ratio".
* The "naughtiness ratio" is the ratio of curse words to total words used by a user.
"""

category_sets = {
    'fruits': {'apple', 'banana', 'pineapple', 'durian', 'mango', 'orange', 'grape', 'kiwi', 'strawberry', 'watermelon'},
    'countries': {('usa', 'america'), 'canada', 'mexico', 'panama', ('uk', 'britian')},  # Use tuple for aliases
    'animals': {'dog', 'cat', 'elephant', 'giraffe', 'lion', 'tiger', 'bear', 'panda', 'koala', 'kangaroo'},
    'colors': {'red', 'blue', 'green', 'yellow', 'orange', 'purple', 'black', 'white', 'brown', 'pink'},
    'numbers': set(map(str, range(1001))),  # Make sure to use strings.
}

ignored_words = {"the", "in", "a", "it", "is", "and", "to", "of", "i", "you", "that", "my", "your"}
curses = {"slubberdagullion", "gobemouche", "fopdoodle", "tatterdemalion", "scallywag", "ragamuffin", "caterwaul", "milksop"}

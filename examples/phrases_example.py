"""
This file contains all keywords (or phrases) that should be collected and analyzed. (except curse words which are stored in in `explicit.py`)
By default, everything is treated as case-insensitive. You may change the flag `CASE_INSENSITIVE` in `config.py`.

`category_sets`: A dictionary of categories with sets of keywords or phraes. 
Use tuples for aliases, e.g. ('james', 'jimmy', 'jim') will match 'james', 'jimmy' and 'jim' and store them as 'james' (first entry).

To prevent overcounting, always put the longest phrase that refers to the same elemnt first. 
For example, put 'united states of america' before 'united states'. (and both before 'usa', phrases before words.)

`ignored_words`: Words that should be ignored in the analysis. The words will still be counted but not shown as top_words.
By default nothing is ignored. Set `IGNORE_COMMON_WORDS` in `config.py` to `True` to ignore these words.
"""

category_sets = {  # Words only, no phrases
    'names': {('james', 'jimmy', 'jim'), 'rose', ('michael', 'mike'), ('jessica', 'jess')}, # Use tuple for aliases
    'fruits': {'apple', 'banana', 'pineapple', 'durian', 'mango', 'orange', 'grape', 'kiwi', 'strawberry', 'watermelon'},
    'countries': {('united states of america', 'united states', 'usa'), 'canada', 'mexico', ('united kingdom', 'uk')},  # Longest phrase first
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

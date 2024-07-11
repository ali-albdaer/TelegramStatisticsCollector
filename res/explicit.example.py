"""
Change the name of this file to `explicit.py` or create a new file named `explicit.py` in this directory.


`curses`: A set of words or phrases that are considered curses. They are used to calculate the "naughtiness" of a user, 
the percentage of curse words used.

You can have multiple words or phrases in a tuple to group them together. For example, ('scallywag', 'scalliwag', 'scallawag') will
group all three words together as one curse word. (First entry)

It is recommended to implement your own logic (fuzzy matching, etc.) to handle curse words. This is just a simple example.
"""

curses = {("slubberdagullion", "sludderbaguillion"), "tatterdemalion", ("scally wag", "scallywag", "scalliwag")}

"""
phrase.py: 

Phrase is a db.Model object for storing the many strings that are used 
by buzz referee for building comment output based on chosen post attributes

* Author:       Mitchell Bowden <mitchellbowden AT gmail DOT com>
* License:      MIT License: http://creativecommons.org/licenses/MIT/
"""

from google.appengine.ext import db

phrase_types = [
  "intro", "begin", "adj_pos", "adj_neg", "end", 
  "already_called", "op_sole_poster", "caller",
  "creator", "has_won", 
  "lc", "sc", "mc", "fc", "mw", "fw", "ml", "fl", 
  "op", "first", "last", "no_reason"
  ]

class Phrase(db.Model):
  str = db.StringProperty(required=True)
  type = db.StringProperty(required=True, choices=set(phrase_types))

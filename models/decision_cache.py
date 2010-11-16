"""
decision_cache.py: 

DecisionCache is a db.Model object for caching a referee decision

* Author:       Mitchell Bowden <mitchellbowden AT gmail DOT com>
* License:      MIT License: http://creativecommons.org/licenses/MIT/
"""

from google.appengine.ext import db

class DecisionCache(db.Model):
  winner_id = db.StringProperty()
  date = db.DateTimeProperty(auto_now_add=True)

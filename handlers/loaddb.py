"""
loaddb.py:
Handler for loading and reinitializing the data store.

* Author:       Mitchell Bowden <mitchellbowden AT gmail DOT com>
* License:      MIT License: http://creativecommons.org/licenses/MIT/
"""

from google.appengine.ext import webapp
from google.appengine.ext import db

import os
import sys
import models.phrase

class LoadDbHandler(webapp.RequestHandler):
  def get(self):
    self.loaddb()
    self.response.out.write('Saved data:<br />')

  def loaddb(self):
    # clear db first
    past_phrases = db.GqlQuery("SELECT * FROM Phrase")
    for pastp in past_phrases:
      pastp.delete()

    # load every phrase type
    for t in models.phrase.phrase_types:
      try:
        path = os.path.join(
          os.path.dirname(__file__), "../data/" + t
        )
        df = open(path, 'rU')
      except IOError:
        continue
      else:
        for p in df:
          np = models.phrase.Phrase(type=t, str=p.rstrip('\n'))
          np.put()

"""
admin.py:

Main GAE entry point for admin pages.

* Author:       Mitchell Bowden <mitchellbowden AT gmail DOT com>
* License:      MIT License: http://creativecommons.org/licenses/MIT/
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'third_party'))

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

import handlers.loaddb
import handlers.admin

def main():
    application = webapp.WSGIApplication([
      ('/admin', handlers.admin.AdminHandler),
      ('/admin/', handlers.admin.AdminHandler),
      ('/admin/loaddb', handlers.loaddb.LoadDbHandler)
    ], debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()

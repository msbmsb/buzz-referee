"""
buzzref.py:

Handler for BuzzReferee, main target for ref task. 
On a post call, retrieves consumption feed and 
processes the posts. If a decision is emitted for 
a post, adds a new comment.

* Author:       Mitchell Bowden <mitchellbowden AT gmail DOT com>
* License:      MIT License: http://creativecommons.org/licenses/MIT/
"""

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api.labs import taskqueue

import os
import traceback
import time
import buzz
import yaml
import logging

import lib.referee
import utils.consts
from models.decision_cache import DecisionCache

OAUTH_CONFIG = yaml.load(open('oauth.yaml').read())

OAUTH_CONSUMER_KEY = OAUTH_CONFIG['oauth_consumer_key']
OAUTH_CONSUMER_SECRET = OAUTH_CONFIG['oauth_consumer_secret']
OAUTH_TOKEN_KEY = OAUTH_CONFIG['oauth_token_key']
OAUTH_TOKEN_SECRET = OAUTH_CONFIG['oauth_token_secret']

class BuzzRefereeHandler(webapp.RequestHandler):
  # handle to the buzz client with auth for buzzreferee
  @property
  def client(self):
    if not hasattr(self, '_client') or not self._client:
      self._client = buzz.Client()
      self._client.oauth_scopes=[buzz.FULL_ACCESS_SCOPE]
      self._client.build_oauth_consumer(
        OAUTH_CONSUMER_KEY, OAUTH_CONSUMER_SECRET
      )
      self._client.build_oauth_access_token(
        OAUTH_TOKEN_KEY, OAUTH_TOKEN_SECRET
      )
    return self._client

  # GET
  def get(self):
    cron = False

    if self.request.headers.get('X-AppEngine-Cron') == 'true':
      cron = True
    elif self.request.headers.get('Referer') and \
        self.request.headers.get('Referer').find('/_ah/admin/cron') != -1:
      cron = True

    if cron:
      try:
        result_task = taskqueue.Task(url='/ref')
        result_task.add()
      except:
        result_task = None

    template_values = {
      'http_get': True,
      'message': None
    }

    path = os.path.join(
      os.path.dirname(__file__), '..', 'templates', 'ref.html'
    )
    self.response.out.write(template.render(path, template_values))

  # POST
  def post(self):
    post_id = self.request.get('post_id')

    message = ''

    if post_id:
      message = self.ref_post(post_id)
    else:
      message = self.queue_ref()

    template_values = {
      'http_get': False,
      'message': message
    }

    path = os.path.join(
      os.path.dirname(__file__), '..', 'templates', 'ref.html'
    )
    self.response.out.write(template.render(path, template_values))

  # get available posts for examination and queue the posts one-at-a-time
  # in the taskqueue
  # filtering by dates is not desired - old posts are just as eligible as new
  def queue_ref(self):
    # get consumption posts
    posts = self.client.posts(type_id='@consumption', user_id='@me', max_results=5000).data

    ret_str = '#posts: ' + str(len(posts)) + '<br />'

    for post in posts:
      
      if DecisionCache.get_by_key_name(str(post.id[25:])) is None and \
          post.placeholder is None and \
          post.actor.id != utils.consts.BUZZREFEREE_ID:
        try:
          result_task = taskqueue.Task(
            name="%s-%d" % (post.id[25:], int(time.time())),
            params={
              'post_id': post.id
            },
            url='/ref',
            countdown=1
          )
          result_task.add()
          ret_str += 'Added post id: ' + post.id + '<br />'
        except:
          result_task = None
          ret_str += 'taskqueue exception<br />'

    return ret_str

  # make a referee decision for the given buzz post
  def ref_post(self, post_id):
    ret_str = ''
    logging.info('ref_post called with id: ' + post_id)
    try:
      post = self.client.post(post_id).data
      ref = lib.referee.Referee(post)
      decision = ref.referee_decision
      if decision is not None:
        # post here
        try:
          new_comment = buzz.Comment(content=decision, post_id=post_id)
          self.client.create_comment(new_comment)

          # cache this decision
          pid = str(post.id[25:])
          if DecisionCache.get_by_key_name(pid) is None:
            new_decision = DecisionCache(key_name=pid)
            new_decision.winner_id = str(ref.winner.id)
            new_decision.put()

          ret_str = "Writing comment: " + decision + "<br />" + \
              "to post.id = " + post.id
        except:
          ret_str = "<h2>Error:</h2><br />" + "Writing comment: " + \
              decision + "<br />" + "to post.id = " + post.id + \
              "<br />" + "<pre>"  + traceback.format_exc()  + "</pre>"
    except:
      ret_str = "<h2>Error:</h2><br />" + "Getting post: " + post_id + \
          "<br />" + "<pre>"  + traceback.format_exc()  + "</pre>"

    logging.info('returning: ' + ret_str)
    return ret_str

  # just for testing
  def force_post(self):
    # get consumption posts
    posts = self.client.posts(type_id='@consumption', user_id='@me').data
    print 'num posts = %i' % len(posts)

    ret_str = ''

    for p in posts:
      print p
      print '\n'
      if p.placeholder is None and \
          p.actor.id != utils.consts.BUZZREFEREE_ID:
        try:
          post = self.client.post(p.id).data
          decision = lib.referee.Referee(post).referee_decision
          if decision is not None:
            # post here
            try:
              new_comment = buzz.Comment(content=decision, post_id=post.id)
              #self.client.create_comment(new_comment)
              ret_str = "Writing comment: " + decision + "<br />" + \
                  "to post.id = " + post.id
            except:
              ret_str = "<h2>Error:</h2><br />" + "Writing comment: " + \
                  decision + "<br />" + "to post.id = " + post.id + \
                  "<br />" + "<pre>"  + traceback.format_exc()  + "</pre>"
        except:
          ret_str = "<h2>Error:</h2><br />" + "Getting post: " + post.id + \
              "<br />" + "<pre>"  + traceback.format_exc()  + "</pre>"

    return ret_str

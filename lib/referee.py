"""
referee.py:

The Referee class for processing a post and emitting 
a decision string to the handler.

* Author:       Mitchell Bowden <mitchellbowden AT gmail DOT com>
* License:      MIT License: http://creativecommons.org/licenses/MIT/
"""

from google.appengine.ext import db
import random
import logging
import lib.post_attributes
import utils.consts
import models.phrase

class Referee(object):
  def __init__(self, post):
    self.post = post
    self.winner = None

  @property
  def referee_decision(self):
    if not hasattr(self, '_ref_decision') or not self._ref_decision:
      attributes = lib.post_attributes.PostAttributes(self.post)

      comments = self.post.comments()
      
      comments_list = []
      for comment in comments:
        attributes.update_attributes(comment)
        comments_list.append(comment)

      if len(comments_list) > 0:
        attributes.set('last', comments_list[-1].actor.id)
      else:
        attributes.set('last', self.post.actor.id)

      attributes.finalize_attributes()

      winner_id = random.choice(attributes.commenters.keys())
      self.winner = attributes.commenters_o[winner_id]

      self._ref_decision = self.build_referee_decision(attributes)
      if self._ref_decision == '':
        self._ref_decision = None
    return self._ref_decision

  # construct the final decision string
  # return None if nothing should be posted in reply
  def build_referee_decision(self, attributes):
    # some ordering here...

    # check for num_times_ref_called
    if attributes.get('num_times_ref_replied') == 1 and attributes.get('num_times_ref_called') > 1:
      return self.get_random_phrase('already_called')
    elif attributes.get('num_times_ref_replied') >= 2:
      logging.info('build_referee_decision: Returning None because num_times_ref_replied >= 2')
      return None
    elif attributes.get('num_times_ref_replied') == attributes.get('num_times_ref_called'):
      logging.info('build_referee_decision: Returning None because num_times_ref_replied == num_times_ref_called')
      return None
    
    # check if original poster is caller and there are no other comments
    if len(attributes.commenters.keys()) == 1:
      return self.get_random_phrase('op_sole_poster')

    if self.winner.id == utils.consts.BUZZREFEREE_ID:
      return self.get_random_phrase('buzzref_wins')

    matching_attribs = attributes.get_matches(self.winner.id)

    # even if there are no matching attributes, don't self-doubt!
    if len(matching_attribs) == 0:
      return self.get_random_phrase('no_reason')

    # in the case of multiple matching attributes, 
    # select one at random
    winning_reason = random.choice(matching_attribs)

    # the winner called the referee
    if winning_reason == 'caller':
      return self.get_random_phrase('caller')

    # the winner wrote this comment 
    if winning_reason == 'creator':
      return self.get_random_phrase('creator')

    # build the decision string
    # the phrase components are made to look best
    # in a certain pattern:
    # {intro} {winner_name} {has_won} {begin_reason} {adj} {reason} {end}
    begin = self.get_random_phrase('begin')
    adj = self.get_random_phrase('adj_pos')
    return "%(intro)s %(name)s %(haswon)s %(begin)s%(dt)s %(adj)s%(reason)s." % {
      'intro': self.get_random_phrase('intro'),
      'name': '*'+self.winner.name+'*',
      'haswon': self.get_random_phrase('has_won'),
      'begin': begin,
      'dt': self.get_DT(begin, adj),
      'adj': adj,
      'reason': self.get_random_phrase(winning_reason)
    }

  # select a random phrase from the given type
  def get_random_phrase(self, type_in):
    random.seed()
    phrases = models.phrase.Phrase.all()
    cnt = phrases.filter('type =',type_in).count(1000)
    if cnt == 0:
      return ''
    if cnt == 1:
      r = 1
    else:
      r = random.randrange(1, cnt, 1)
    phrase = phrases.filter('type =',type_in).fetch(limit = 1, offset = r-1)[0]
    return phrase.str.replace(utils.consts.NAME_PLACEHOLDER, '*'+self.winner.name+'*').replace('  ', ' ')

  # given that the previous 'begin' phrase may end with a determiner,
  # make sure the DT agrees with the next adjective
  def get_DT(self, begin, adj):
    if begin[-1] != 'a':
      return '' 

    if adj[0].lower() in ['a','e','i','o','u']:
      return 'n'
    else:
      return ''

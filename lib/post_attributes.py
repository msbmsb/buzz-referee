"""      
post_attributes.py:

PostAttributes store selected information extracted from each post
in buzz referee's comnsumption stream. For an input post, the 
attributes are identified and stored by set(), retrieved by get().

post attributes extracted:
  lc:       longest comment
  sc:       shortest comment
  mc:       most comments
  fc:       fewest comments
  mw:       most words
  fw:       fewest words
  ml:       most supporting links
  fl:       fewest supporting links
  op:       original poster
  first:    first commenter
  last:     last commenter
  caller:   caller of referee
  creator:  creator of referee
  total number of comments
  number of times referee called
  number of times referee replied

* Author:       Mitchell Bowden <mitchellbowden AT gmail DOT com>
* License:      MIT License: http://creativecommons.org/licenses/MIT/
"""

import types
import re
import logging
import buzz 
import utils.consts

class PostAttributes(object):
  def __init__(self, post):
    self.attributes = {'lc':None, 'sc':None, 'mc':None, 'fc':None, 'mw':None, 'fw':None, 'ml':None, 'fl':None, 'op':None, 'first':None, 'last':None, 'caller':None, 'creator':utils.consts.BUZZREF_CREATOR_ID, 'num_times_ref_called':0, 'num_times_ref_replied':0, 'num_comments':0}
    # map of actors to # of comments
    self.commenters = {}
    self.commenters_o = {}
    self.comment_sizes = {}
    self.number_of_words = {}
    self.number_of_links = {}
    self.attributes['op'] = post.actor.id
    self.update_attributes(post)
    self.set('first', None)

  def to_str(self):
    ret_str = ''
    for k in self.attributes:
      if self.attributes[k] is not None:
        ret_str += k + ":" + str(self.attributes[k]) + " "
#         ret_str += "%s: %s " % {k, str(self.attributes[k])}
      else:
        ret_str += "%s: None " % k
    return ret_str

  def get(self, key):
    if key in self.attributes:
      return self.attributes[key]
    else:
      return None

  def set(self, key, value):
    if key == 'creator':
      return
    if key in self.attributes:
      self.attributes[key] = value

  def update_attributes(self, comment):
    comment_content = comment.content.lower().strip().replace(u'\u2019', '\'')
    comment_content = re.sub('<br />|\\r|\\n', ' ', comment_content)
    self.add_to_commenters(comment.actor)
    commenter_id = comment.actor.id
    self.set('num_comments', self.get('num_comments') + 1)

    # attribute extraction
    comment_size = len(comment_content)
    self.comment_sizes[commenter_id] = \
      self.comment_sizes.get(commenter_id,0) + comment_size
    num_comments = self.commenters[commenter_id]
    num_words = len(comment_content.split())
    self.number_of_words[commenter_id] = \
      self.number_of_words.get(commenter_id,0) + num_words
    # every buzz comment has at least two links
    # one for the user profile, one for the comment permalink
    num_links = comment_content.count('a href') - 2
    if num_links > 0:
      self.number_of_links[commenter_id] = \
        self.number_of_links.get(commenter_id,0) + num_links

    # first!!1!1
    if self.get('first') == None:
      self.set('first', commenter_id)

    # caller ...
    if self.comment_calls_ref(comment_content):
      if self.get('caller') == None:
        self.set('caller', commenter_id)
      # num_times_ref_called ...
      self.set('num_times_ref_called', self.get('num_times_ref_called') + 1)

    # buzzreferee reply
    if commenter_id == utils.consts.BUZZREFEREE_ID:
      self.set('num_times_ref_replied', self.get('num_times_ref_replied') + 1)

  def finalize_attributes(self):
    # set most/least for:
    # lc/sc, mc/fc, mw/fw, ml/fl
    comment_sizes_sorted = self.get_sorted_grouped(self.comment_sizes)
    num_comments_sorted = self.get_sorted_grouped(self.commenters)
    number_of_words_sorted = self.get_sorted_grouped(self.number_of_words)
    number_of_links_sorted = self.get_sorted_grouped(self.number_of_links)

    if len(comment_sizes_sorted) > 0:
      self.set('lc', comment_sizes_sorted[-1][1])
      self.set('sc', comment_sizes_sorted[0][1])
    if len(num_comments_sorted) > 0:
      self.set('mc', num_comments_sorted[-1][1])
      self.set('fc', num_comments_sorted[0][1])
    if len(number_of_words_sorted) > 0:
      self.set('mw', number_of_words_sorted[-1][1])
      self.set('fw', number_of_words_sorted[0][1])
    if len(number_of_links_sorted) > 0:
      self.set('ml', number_of_links_sorted[-1][1])
      self.set('fl', number_of_links_sorted[0][1])

  def get_sorted_grouped(self, d):
    out = {}
    for k in d:
      out.setdefault(d[k], []).append(k)
    return sorted(out.items())

  # determine if the comment is @-mentioning buzzreferee
  def comment_calls_ref(self, content):
    if content.find('href="http://www.google.com/profiles/'+utils.consts.BUZZREFEREE_ID) != -1:
      return True
    if content.find('href="http://www.google.com/profiles/'+utils.consts.BUZZREFEREE_ID_STR) != -1:
      return True
    return False

  def add_to_commenters(self, actor):
    if actor.id in self.commenters:
      self.commenters[actor.id] = self.commenters[actor.id] + 1
    else:
      self.commenters[actor.id] = 1
      self.commenters_o[actor.id] = actor

  def get_matches(self, winner_id):
    matches = []
    for a in self.attributes.keys():
      if type(self.attributes[a]) is types.ListType:
        logging.info('attribute: %s' % a)
        logging.info(self.attributes[a])
        if winner_id in self.attributes[a]:
          if (a == 'fc' or a == 'fl') and \
              len(self.attributes[a]) > (len(self.commenters) * 0.40):
            continue
          matches.append(a)
      elif type(self.attributes[a]) is types.UnicodeType or \
          type(self.attributes[a]) is types.StringType:
        if self.attributes[a] == winner_id:
          matches.append(a)
    return matches

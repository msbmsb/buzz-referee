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

import re
import buzz 
import utils.consts

class PostAttributes(object):
  def __init__(self, post):
    self.attributes = {'lc':None, 'sc':None, 'mc':None, 'fc':None, 'mw':None, 'fw':None, 'ml':None, 'fl':None, 'op':None, 'first':None, 'last':None, 'caller':None, 'creator':utils.consts.BUZZREF_CREATOR_ID, 'num_times_ref_called':0, 'num_times_ref_replied':0, 'num_comments':0}
    # map of actors to # of comments
    self.commenters = {}
    self.attributes['op'] = post.actor.id
    self.update_attributes(post)

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
    num_comments = self.commenters[comment.actor]
    num_words = len(comment_content.split())
    num_links = comment_content.count('a href')

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

    # longest/shortest comment
    self.set_paired_attributes('lc','sc', comment_size, commenter_id)
    # most/fewest comments
    self.set_paired_attributes('mc','fc', num_comments, commenter_id)
    # most/fewest words
    self.set_paired_attributes('mw','fw', num_words, commenter_id)
    # most/fewest links
    self.set_paired_attributes('ml','fl', num_links, commenter_id)

  def set_paired_attributes(self, l_attrib, s_attrib, val, actor_id):
    if self.get(l_attrib) is None:
      self.set(l_attrib, [val, set([actor_id])])
      self.set(s_attrib, [val, set([actor_id])])
    else:
      l = self.get(l_attrib)
      s = self.get(s_attrib)
      if val > l[0]:
        self.set(l_attrib, [val, set([actor_id])])
      elif val == l[0]:
        self.get(l_attrib)[1].add(actor_id)
      if val < s[0]:
        self.set(s_attrib, [val, set([actor_id])])
      elif val == s[0]:
        self.get(s_attrib)[1].add(actor_id)

  # determine if the comment is @-mentioning buzzreferee
  def comment_calls_ref(self, content):
    if content.find('href="http://www.google.com/profiles/'+utils.consts.BUZZREFEREE_ID) != -1:
      return True
    if content.find('href="http://www.google.com/profiles/'+utils.consts.BUZZREFEREE_ID_STR) != -1:
      return True
    return False

  def add_to_commenters(self, actor):
    if actor in self.commenters:
      self.commenters[actor] += 1
    else:
      self.commenters[actor] = 1

  def get_matches(self, winner_id):
    matches = []
    for a in self.attributes.keys():
      if self.attributes[a] == winner_id:
        matches.append(a)
    return matches

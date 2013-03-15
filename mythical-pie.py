#!/usr/bin/env python
#@+leo-ver=5-thin
#@+node:peckj.20130315135233.1439: * @file mythical-pie.py
#@@first
#@@language python

#@+<< imports >>
#@+node:peckj.20130315135233.1440: ** << imports >>
import random
#@-<< imports >>
#@+others
#@+node:peckj.20130315135233.1441: ** random rolls
def roll(faces):
  random.randint(1,faces)

def roll_d10():
  roll(10)

def roll_d100():
  roll(100)
#@+node:peckj.20130315135233.1442: ** gamestate class
class Gamestate:
  #@+others
  #@+node:peckj.20130315135233.1443: *3* init
  def __init__(self, chaos=5):
    self.chaos = chaos
    self.scenes = []
    self.threads = []
    self.npcs = []
    self.pcs = []
  #@+node:peckj.20130315135233.1444: *3* chaos
  def _delta_chaos(self, dc):
    self.chaos += dc
    if self.chaos > 9:
      self.chaos = 9
    elif self.chaos < 1:
      self.chaos = 1

  def increase_chaos(self):
    self._delta_chaos(1)
    
  def decrease_chaos(self):
    self._delta_chaos(-1)
  #@+node:peckj.20130315135233.1445: *3* scenes
  def add_scene(self, scene):
    self.scenes.append(scene)
  #@+node:peckj.20130315135233.1446: *3* threads
  def add_thread(self, thread):
    self.threads.append(thread)

  def remove_thread(self, thread):
    self.threads.remove(thread)
  #@+node:peckj.20130315135233.1447: *3* npcs
  def add_npc(self, character):
    self.npcs.append(character)

  def remove_npc(self, character):
    self.npcs.remove(character)
  #@+node:peckj.20130315135233.1449: *3* pcs
  def add_pc(self, character):
    self.pcs.append(character)

  def remove_pc(self, character):
    self.pcs.remove(character)
  #@-others

#@+node:peckj.20130315135233.1450: ** scene/thread/character wrapper class
class StringWrapper:
  def init(self, str):
    self.value = str
#@+node:peckj.20130315135233.1451: ** fate table class
class FateTable:
  #@+others
  #@+node:peckj.20130315135233.1452: *3* init
  def __init__(self):
    # likelihood of the answer being yes
    self.name_to_rank = {
      'Impossible': 0, 
      'No way': 1, 
      'Very unlikely': 2,
      'Unlikely': 3,
      '50/50': 4,
      'Somewhat likely': 5,
      'Likely': 6,
      'Very likely': 7,
      'Near sure thing': 8,
      'A sure thing': 9,
      'Has to be': 10 
    } 
    # the 'big numbers' on the table
    # yes_thresholds[chaos_value][name_to_rank['rank']] gives you the right value
    self.yes_thresholds = {
      1: [-20,  0,  5,  5, 10, 20,  25,  45,  50,  55,  80],
      2: [  0,  5,  5, 10, 15, 25,  35,  50,  55,  65,  85],
      3: [  0,  5, 10, 15, 25, 45,  50,  65,  75,  80,  90],
      4: [  5, 10, 15, 20, 35, 50,  55,  75,  80,  85,  95],
      5: [  5, 15, 25, 35, 50, 65,  75,  85,  90,  90,  95],
      6: [ 10, 25, 45, 50, 65, 80,  85,  90,  95,  95, 100],
      7: [ 15, 35, 50, 55, 75, 85,  90,  95,  95,  95, 100],
      8: [ 25, 50, 65, 75, 85, 90,  95,  95, 100, 110, 130],
      9: [ 50, 75, 85, 90, 95, 95, 100, 105, 115, 125, 145]
    }
    # same scheme as yes_thresholds
    self.exceptional_yes_thresholds = {
      1: [ 0,  0,  1,  1,  2,  4,  5,  9, 10, 11, 16],
      2: [ 0,  1 , 1,  2,  3,  5,  7, 10, 11, 13, 16],
      3: [ 0,  1,  2,  3,  5,  9, 10, 13, 15, 16, 18],
      4: [ 1,  2,  3,  4,  7, 10, 11, 15, 16, 16, 19],
      5: [ 1,  3,  5,  7, 10, 13, 15, 16, 18, 18, 19],
      6: [ 2,  5,  9, 10, 13, 16, 16, 18, 19, 19, 20],
      7: [ 3,  7, 10, 11, 15, 16, 18, 19, 19, 19, 20],
      8: [ 5, 10, 13, 15, 16, 18, 19, 19, 20, 22, 26],
      9: [10, 15, 16, 18, 19, 19, 20, 21, 23, 25, 26]
    }
    self.exceptional_no_thresholds = {
      1: [77, 81, 82, 82,  83,  85,  86,  90,  91,  92,  97],
      2: [81, 82, 82, 83,  84,  86,  88,  91,  92,  94,  97],
      3: [81, 82, 83, 84,  86,  90,  91,  94,  96,  97,  99],
      4: [82, 83, 84, 85,  88,  91,  92,  96,  97,  97, 100],
      5: [82, 84, 86, 88,  91,  94,  96,  97,  99,  99, 100],
      6: [83, 86, 90, 91,  94,  97,  97,  99, 100, 100,   0],
      7: [84, 88, 91, 92,  96,  97,  99, 100, 100, 100,   0],
      8: [86, 91, 94, 96,  97,  99, 100, 100,   0,   0,   0],
      9: [91, 96, 97, 99, 100, 100,   0,   0,   0,   0,   0]
    }
    # event_meaning_action[roll-1] = correct value
    self.event_meaning_action = [
      'Attainment','Starting','Neglect','Fight','Recruit','Triumph',
      'Violate','Oppose','Malice','Communicate','Persecute','Increase',
      'Decrease','Abandon','Gratify','Inquire','Antagonise','Move','Waste',
      'Truce','Release','Befriend','Judge','Desert','Dominate','Procrastinate',
      'Praise','Separate','Take','Break','Heal','Delay','Stop','Lie','Return',
      'Immitate','Struggle','Inform','Bestow','Postpone','Expose','Haggle',
      'Imprison','Release','Celebrate','Develop','Travel','Block','Harm',
      'Debase','Overindulge','Adjourn','Adversity','Kill','Disrupt','Usurp',
      'Create','Betray','Agree','Abuse','Oppress','Inspect','Ambush','Spy',
      'Attach','Carry','Open','Carelessness','Ruin','Extravagance','Trick',
      'Arrive','Propose','Divide','Refuse','Mistrust','Deceive','Cruelty',
      'Intolerance','Trust','Excitement','Activity','Assist','Care','Negligence',
      'Passion','Work hard','Control','Attract','Failure','Pursue','Vengeance',
      'Proceedings','Dispute','Punish','Guide','Transform','Overthrow','Oppress',
      'Change'
    ]
    self.event_meaning_subject = [
      'Goals','Dreams','Environment','Outside','Inside','Reality','Allies','Enemies',
      'Evil','Good','Emotions','Opposition','War','Peace','The innocent','Love',
      'The spiritual','The intellectual','New ideas','Joy','Messages','Energy',
      'Balance','Tension','Friendship','The physical','A project','Pleasures',
      'Pain','Possessions','Benefits','Plans','Lies','Expectations','Legal matters',
      'Bureaucracy','Business','A path','News','Exterior factors','Advice','A plot',
      'Competition','Prison','Illness','Food','Attention','Success','Failure','Travel',
      'Jealousy','Dispute','Home','Investment','Suffering','Wishes','Tactics','Stalemate',
      'Randomness','Misfortune','Death','Disruption','Power','A burden','Intrigues','Fears',
      'Ambush','Rumor','Wounds','Extravagance','A representative','Adversities','Opulence',
      'Liberty','Military','The mundane','Trials','Masses','Vehicle','Art','Victory','Dispute',
      'Riches','Status quo','Technology','Hope','Magic','Illusions','Portals','Danger','Weapons',
      'Animals','Weather','Elements','Nature','The public','Leadership','Fame','Anger',
      'Information'
    ]
  #@+node:peckj.20130315135233.1455: *3* random event
  def random_event_happens?(self, gamestate, roll):
    return roll % 11 == 0 and roll / 11 <= gamestate.chaos

  def random_event_subject(self):
    return self.event_meaning_subject[roll_d100()-1]

  def random_event_action(self):
    return self.event_meaning_action[roll_d100()-1]

  def random_event_focus(self):
    roll = roll_d100()
    if roll <= 7:
      return 'Remote event'
    elif roll <= 28:
      return 'NPC action'
    elif roll <= 35:
      return 'Introduce a new NPC'
    elif roll <= 45:
      return 'Move toward a thread'
    elif roll <= 52:
      return 'Move away from a thread'
    elif roll <= 55:
      return 'Close a thread'
    elif roll <= 67:
      return 'PC negative'
    elif roll <= 75:
      return 'PC positive'
    elif roll <= 83:
      return 'Ambiguous event'
    elif roll <= 92:
      return 'NPC negative'
    else:
      return 'NPC positive'

  def roll_random_event(self):
    """ returns a tuple consisting of (focus, action, subject) """
    focus = self.random_event_focus()
    action = self.random_event_action()
    subject = self.random_event_subject()
    return (focus, action, subject)
  #@+node:peckj.20130315135233.1456: *3* rolling
  def roll_fate(self, gamestate, rank):
    """ returns a tuple consisting of (answer, event, roll), where
        answer is "yes", "no", or the "exceptional" varieties,
        event is None (for no event), or a tuple consisting of 
        (focus, action, subject), and roll is the number on the
        d100 that was rolled
    """
    roll = roll_d100()
    yes = self.yes_thresholds[gamestate.chaos][rank]
    answer = ''
    if roll <= yes:
      # yes, is it exceptional?
      ex_yes = self.exceptional_yes_thresholds[gamestate.chaos][rank]
      if roll <= ex_yes:
        answer = 'Exceptional Yes' % roll
      else:
        answer = 'Yes'
    else:
      # no, is it exceptional?
      ex_no = self.exceptional_no_thresholds[gamestate.chaos][rank]
      if roll >= ex_no:
        answer = 'Exceptional No'
      else:
        answer = 'No'
    event = None
    if self.random_event_happens?(gamestate, roll):
      event = self.roll_random_event()
    return (answer, event, roll)
    
  #@-others
#@-others
#@-leo

#!/usr/bin/env python
#@+leo-ver=5-thin
#@+node:peckj.20130315135233.1439: * @file mythical-pie.py
#@@first
#@@language python

#@+<< imports >>
#@+node:peckj.20130315135233.1440: ** << imports >>
import random

gamestate = None
fatetable = None
#@-<< imports >>
#@+others
#@+node:peckj.20130315135233.1441: ** random rolls
def roll_dN(faces):
  return random.randint(1,faces)

def roll_d10():
  return roll_dN(10)

def roll_d100():
  return roll_dN(100)
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

#@+node:peckj.20130315135233.1451: ** fate table class
class FateTable:
  #@+others
  #@+node:peckj.20130315135233.1452: *3* init
  def __init__(self):
    # likelihood of the answer being yes
    self.name_to_rank = {
      0:  'Impossible', 
      1:  'No way', 
      2:  'Very unlikely',
      3:  'Unlikely',
      4:  '50/50',
      5:  'Somewhat likely',
      6:  'Likely',
      7:  'Very likely',
      8:  'Near sure thing',
      9:  'A sure thing',
      10: 'Has to be' 
    } 
    # the 'big numbers' on the table
    # yes_thresholds[chaos_value][rank] gives you the right value
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
    # event focus
    self.event_focus_standard = {
      7: 'Remote event',
      28: 'NPC action',
      35: 'Introduce a new NPC',
      45: 'Move toward a thread',
      52: 'Move away from a thread',
      55: 'Close a thread',
      67: 'PC negative',
      75: 'PC positive',
      83: 'Ambiguous event',
      92: 'NPC negative',
      100: 'NPC positive'
    }
    self.event_focus_horror = {
      10: 'Horror - PC',
      23: 'Horror - NPC',
      30: 'Remote event',
      49: 'NPC action',
      52: 'New NPC',
      55: 'Move toward a thread',
      62: 'Move away from a thread',
      72: 'PC negative',
      75: 'PC positive',
      82: 'Ambiguous event',
      97: 'NPC negative',
      100: 'NPC positive'
    }
    self.event_focus_action = {
      16: 'Action!',
      24: 'Rempote event',
      44: 'NPC action',
      52: 'New NPC',
      56: 'Move toward a thread',
      64: 'Move away from a thread',
      76: 'PC negative',
      80: 'PC positive',
      84: 'Ambiguous event',
      96: 'NPC negative',
      100: 'NPC positive'
    }
    self.event_focus_mystery = {
      8: 'Remote event',
      20: 'NPC action',
      32: 'New NPC',
      52: 'Move toward a thread',
      64: 'Move away from a thread',
      72: 'PC negative',
      80: 'PC positive',
      88: 'Ambiguous event',
      96: 'NPC negative',
      100: 'NPC positive'
    }
    self.event_focus_social = {
      12: 'Drop a bomb!',
      24: 'Remote event',
      36: 'NPC action',
      44: 'New NPC',
      56: 'Move toward a thread',
      60: 'Move away from a thread',
      64: 'Close a thread',
      72: 'PC negative',
      80: 'PC positive',
      92: 'Ambiguous event',
      96: 'NPC negative',
      100: 'NPC positive'
    }
    self.event_focus_personal = {
      7: 'Remote event',
      24: 'NPC action',
      28: 'PC NPC action',
      35: 'New NPC',
      42: 'Move toward a thread',
      45: 'Move toward a PC thread',
      50: 'Move away from a thread',
      52: 'Move away from a PC thread',
      54: 'Close thread',
      55: 'Close PC thread',
      67: 'PC negative',
      75: 'PC positive',
      83: 'Ambiguous event',
      90: 'NPC negative',
      92: 'PC NPC negative',
      99: 'NPC positive',
      100: 'PC NPC positive'
    }
    self.event_focus_epic = {
      12: 'Thread escalates',
      16: 'Remote event',
      30: 'NPC action',
      42: 'New NPC',
      46: 'Move toward a thread',
      58: 'Move away from a thread',
      72: 'PC negative',
      80: 'PC positive',
      84: 'Ambiguous event',
      92: 'NPC negative',
      100: 'NPC positive'
    }
    
    self.event_focus = [self.event_focus_standard]
  #@+node:peckj.20130315135233.1455: *3* random event
  def random_event_happens(self, gamestate, roll):
    return (roll % 11 == 0 and roll / 11 <= gamestate.chaos) or roll == 100

  def random_event_subject(self):
    return self.event_meaning_subject[roll_d100()-1]

  def random_event_action(self):
    return self.event_meaning_action[roll_d100()-1]

  def random_event_focus(self):
    roll = roll_d100()
    table = random.choice(self.event_focus)
    while roll <= 100:
      r = table.get(roll, None)
      if r is not None:
        return r
      else:
        roll += 1

  def roll_random_event(self):
    """ returns a tuple consisting of (focus, action, subject) """
    focus = self.random_event_focus()
    action = self.random_event_action()
    subject = self.random_event_subject()
    return (focus, action, subject)

  def roll_complex_question(self):
    """ returns a tuple consisting of (action, subject) """
    action = self.random_event_action()
    subject = self.random_event_subject()
    return (action, subject)
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
        answer = 'Exceptional Yes'
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
    if self.random_event_happens(gamestate, roll):
      event = self.roll_random_event()
    return (answer, event, roll)
    
  #@-others
#@+node:peckj.20130315194435.1392: ** menus
def menu():
  exit = False
  while not exit:
    exit = main_menu()
#@+node:peckj.20130315194435.1394: *3* main menu
def main_menu():
  print "\n"
  print "Main Menu:"
  print "  1. Create a new scene"
  print "  2. End the current scene"
  print "  3. Add a PC"
  print "  4. Remove a PC"
  print "  5. Add an NPC"
  print "  6. Remove an NPC"
  print "  7. Add a thread"
  print "  8. Close a thread"
  print "  9. Roll Fate"
  print " 10. Ask a complex question"
  print " 11. Roll a random PC"
  print " 12. Roll a random NPC"
  print " 13. Roll a random thread"
  print " 14. List PCs"
  print " 15. List NPCs"
  print " 16. List threads"
  print " 17. List scenes"
  print " 18. Print game stats"
  print "  0. End adventure"
  choice = raw_input('What is your choice? ')
  options = {
    '1' : create_scene,
    '2' : end_scene,
    '3' : add_pc,
    '4' : remove_pc,
    '5' : add_npc,  
    '6' : remove_npc,
    '7' : add_thread,
    '8' : close_thread,
    '9' : roll_fate,
    '10': complex_question,
    '11': random_pc,
    '12': random_npc,
    '13': random_thread,
    '14': list_pcs,
    '15': list_npcs,
    '16': list_threads,
    '17': list_scenes,
    '18': print_game_stats,
    '0' : end_adventure
  }
  print "\n"
  if choice in options:
    return options[choice]()
  else:
    return invalid_choice()
#@+node:peckj.20130315194435.1402: *3* scenes
#@+node:peckj.20130315194435.1397: *4* create a new scene
def create_scene():
  print "Think of a scene setup.  When you're ready, press enter."
  raw_input("  Press enter.")
  roll = roll_d10()
  if roll <= gamestate.chaos:
    # scene setup is modified
    if roll % 2 == 0: 
      # even roll, scene is interrupted
      print "Oh no! The scene has been interrupted!  The interrupting event is:"
      focus, action, subject = fatetable.roll_random_event()
      print "  Focus:   %s" % focus
      print "  Action:  %s" % action
      print "  Subject: %s" % subject
    else:
      # odd roll, scene is altered
      print "Ooh, sorry about that!  Scene has been altered."
  print "Alright, now, what's your scene setup?"
  scene = raw_input("?> ")
  gamestate.add_scene(scene)
  return False
#@+node:peckj.20130315194435.1406: *4* end current scene
def end_scene():
  if len(gamestate.scenes) < 1:
    print "Please add some Scenes to the game first."
  else:
    print "Were the PCs in control of the scene?"
    print "  1. Yes (less chaotic)"
    print "  2. No (more chaotic)"
    choice = raw_input("What is your choice? ")
    options = {
      '1': gamestate.decrease_chaos,
      '2': gamestate.increase_chaos
    }
    if choice in options:
      options[choice]()
    else:
      invalid_choice()
      return end_scene()
  return False
#@+node:peckj.20130315194435.1407: *4* list scenes
def list_scenes():
  print "Scenes in the current game:"
  if len(gamestate.scenes) > 0:
    for scene in gamestate.scenes:
      print "  %s. %s" % (gamestate.scenes.index(scene) + 1, scene)
  else:
    print "  None! Please add some!"
  return False
#@+node:peckj.20130315194435.1403: *3* pcs
#@+node:peckj.20130315194435.1395: *4* add a pc
def add_pc():
  name = raw_input("What is the PC's name? ")
  gamestate.add_pc(name)
#@+node:peckj.20130315194435.1401: *4* remove a pc
def remove_pc():
  if len(gamestate.pcs) < 1:
    print "Please add some PCs to the game first."
  else:
    list_pcs()
    print "  0. Cancel this action"
    choice = raw_input("Which PC would you like to delete? ")
    try:
      choice = int(choice)
    except ValueError:
      return invalid_choice()
    if choice == 0:
      return False
    elif choice > 0 and choice <= len(gamestate.pcs):
      gamestate.pcs.pop(choice - 1)
    else:
      return invalid_choice()
  return False
#@+node:peckj.20130315194435.1408: *4* roll random pc
def random_pc():
  if len(gamestate.pcs) < 1:
    print "Please add some PCs to the game first."
  else:
    print "Rolling a random PC..."
    print "  %s" % random.choice(gamestate.pcs)
  return False
#@+node:peckj.20130315194435.1409: *4* list pcs
def list_pcs():
  print "PCs in the current game:"
  if len(gamestate.pcs) > 0:
    for pc in gamestate.pcs:
      print "  %s. %s" % (gamestate.pcs.index(pc) + 1, pc)
  else:
    print "  None! Please add some!"
  return False
#@+node:peckj.20130315194435.1404: *3* npcs
#@+node:peckj.20130315194435.1396: *4* create an npc
def add_npc():
  name = raw_input("What is the NPC's name? ")
  gamestate.add_npc(name)
#@+node:peckj.20130315194435.1410: *4* remove an npc
def remove_npc():
  if len(gamestate.npcs) < 1:
    print "Please add some NPCs to the game first."
  else:
    list_npcs()
    print "  0. Cancel this action"
    choice = raw_input("Which NPC would you like to delete? ")
    try:
      choice = int(choice)
    except ValueError:
      return invalid_choice()
    if choice == 0:
      return False
    elif choice > 0 and choice <= len(gamestate.npcs):
      gamestate.npcs.pop(choice - 1)
    else:
      return invalid_choice()
  return False
#@+node:peckj.20130315194435.1412: *4* roll random npc
def random_npc():
  if len(gamestate.npcs) < 1:
    print "Please add some NPCs to the game first."
  else:
    print "Rolling a random NPC..."
    print "  %s" % random.choice(gamestate.npcs)
  return False
#@+node:peckj.20130315194435.1414: *4* list npcs
def list_npcs():
  print "NPCs in the current game:"
  if len(gamestate.npcs) > 0:
    for npc in gamestate.npcs:
      print "  %s. %s" % (gamestate.npcs.index(npc) + 1, npc)
  else:
    print "  None! Please add some!"
  return False
#@+node:peckj.20130315194435.1405: *3* threads
#@+node:peckj.20130315194435.1398: *4* create a thread
def add_thread():
  name = raw_input("What should the thread be called? ")
  gamestate.add_thread(name)
#@+node:peckj.20130315194435.1411: *4* close a thread
def close_thread():
  if len(gamestate.threads) < 1:
    print "Please add some threads to the game first."
  else:
    list_threads()
    print "  0. Cancel this action"
    choice = raw_input("Which thread would you like to close? ")
    try:
      choice = int(choice)
    except ValueError:
      return invalid_choice()
    if choice == 0:
      return False
    elif choice > 0 and choice <= len(gamestate.threads):
      gamestate.threads.pop(choice - 1)
    else:
      return invalid_choice()
  return False
#@+node:peckj.20130315194435.1413: *4* roll random thread
def random_thread():
  if len(gamestate.threads) < 1:
    print "Please add some threads to the game first."
  else:
    print "Rolling a random thread..."
    print "  %s" % random.choice(gamestate.threads)
  return False
#@+node:peckj.20130315194435.1415: *4* list threads
def list_threads():
  print "Threads in the current game:"
  if len(gamestate.threads) > 0:
    for thread in gamestate.threads:
      print "  %s. %s" % (gamestate.threads.index(thread) + 1, thread)
  else:
    print "  None! Please add some!"
  return False
#@+node:peckj.20130315194435.1416: *3* adventure
#@+node:peckj.20130315194435.1399: *4* end adventure
def end_adventure():
  return True
#@+node:peckj.20130315194435.1417: *4* roll fate
def roll_fate():
  print "How likely is your question to be true?"
  for key in range(len(fatetable.name_to_rank)):
    print "  %s. %s" % (key + 1, fatetable.name_to_rank[key])
  print "  0. Cancel this action"
  choice = raw_input("What is your choice? ")
  try:
    choice = int(choice)
  except ValueError:
    return invalid_choice()
  if choice <= len(fatetable.name_to_rank):
    if choice == 0:
      return False
    else:
      choice -= 1
      # get a tuple of (answer, roll, event)
      answer, event, roll = fatetable.roll_fate(gamestate, choice)
      print "Your answer: %s (roll of %s)" % (answer, roll)
      if event is not None:
        focus, action, subject = event
        print "Random event!"
        print "  Focus:   %s" % focus
        print "  Action:  %s" % action
        print "  Subject: %s" % subject
    return False
  else:
    return invalid_choice()
#@+node:peckj.20130325102011.1544: *4* complex question
def complex_question():
  action, subject = fatetable.roll_complex_question()
  print "  Action:  %s" % action
  print "  Subject: %s" % subject
  return False
#@+node:peckj.20130315194435.1418: *4* print game stats
def print_game_stats():
  print "Your game stats:"
  list_pcs()
  list_npcs()
  list_threads()
  list_scenes()
  print "Current chaos factor: %s" % gamestate.chaos
  return False
#@+node:peckj.20130315194435.1400: *3* invalid choice
def invalid_choice():
  print "Sorry, that was not a valid choice."
  return False
#@+node:peckj.20130315194435.1393: ** main
def initialize():
  global gamestate, fatetable
  gamestate = Gamestate()
  fatetable = FateTable()

def print_greeting():
  print "Welcome to Mythical Pie, the GM Emulator!"
  
def print_goodbye():
  print "Goodbye! Hope you enjoyed your adventure!"

if __name__ == "__main__":
  initialize()
  print_greeting()
  menu()
  print_goodbye()
#@-others
#@-leo

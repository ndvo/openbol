import kivy
kivy.require('1.8.0')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.config import Config
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.scatter import Scatter
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import *
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.textinput import TextInput
from math import sqrt
from kivy.uix.screenmanager import *#ScreenManager, Screen, FadeTransition, SwapTransition
from kivy.animation import *
from kivy.clock import Clock

import os
import cPickle as Pickle
from random import shuffle

import g

# ---------------------------------------------------------------------------------
## General Code ----------------
# ---------------------------------------------------------------------------------

class smallCard(ButtonBehavior,Image):
	def __init__(self, card_type, card_name, **kwargs):
		super(smallCard, self).__init__(**kwargs)
		if card_type == 'formation': card_type = 'sf'
		elif card_type == 'tactic': card_type = 't'

		elif card_type == 'defender': card_type = 'pd'
		elif card_type == 'midfielder': card_type = 'pm'
		elif card_type == 'attacker': card_type = 'pa'

		self.source='./data/images/card-'+card_type+'-'+card_name+'.png'
		self.size_hint = (None,None)
		self.size = (58,100)
		self.bind(on_release = self.card_release)

	def card_release(self, marker_object):
		print "clicked card"
		

class cardHand(ScrollView):
	def __init__(self,**kwargs):
		super(cardHand, self).__init__(**kwargs)
		#self.do_scroll_y = False
		self.size_hint = (None,None)
		self.size = (360,100)
		self.pos = (0,123)

		self.box_layout = BoxLayout(orientation = 'horizontal')
		self.box_layout.size_hint = (None,1)
		#self.box_layout.width = len(g.team['hand'])*58

		#Add mock cards
		list_of_formations = ['343','352','433','442','4231','kami','libero','metodo','pyr','wm']
		list_of_tactics = ['ball','col','count','direct','for','indiv','long','man','offside','runs','set','zone']
		list_of_defenders = ['fast','leader','talent','util']
		list_of_midfielders = ['fast','leader','opport','talent','util']
		list_of_attackers = ['fast','leader','opport']

		self.box_layout.width = (len(list_of_formations)+len(list_of_tactics)+len(list_of_defenders)+len(list_of_midfielders)+len(list_of_attackers))*58

		for card in list_of_formations:
			self.box_layout.add_widget(smallCard('formation',card))
		for card in list_of_tactics:
			self.box_layout.add_widget(smallCard('tactic',card))

		for card in list_of_defenders:
			self.box_layout.add_widget(smallCard('defender',card))
		for card in list_of_midfielders:
			self.box_layout.add_widget(smallCard('midfielder',card))
		for card in list_of_attackers:
			self.box_layout.add_widget(smallCard('attacker',card))

		self.add_widget(self.box_layout)

		print 'sizes:/n scroll =',self.size,'   box =',self.box_layout.size

	def get_selected(self):
		selected = []
		return selected

class gameSave():
	"""This class holds information about the user, team, statistics, etc. When the game is saved, this fie is pickled and written into the 'save' file. The game will auto-save at a number of crcunstances, including every time the profile is changed, every time the card hand is selected, after every play in the game, after the game or tournament is over and every time the player gets fans."""
	def __init__(self, team_name = '', team_crest = '', fans = 0, level = 1, available_cards = [], selected_cards = [], current_tournament = {'id': 'none', 'team1': 'none', 'team2': 'none', 'team3': 'none', 'team4': 'none','results':['none','none','none','none'],'match': None}, history ={'win':0,'tie':0,'lose':0,'3rd':0,'2nd':0,'1st':0,'premiere':0,'world':0} , milestones = {'profile': False, 'tutorial': False, '3rd': False, '2nd': False, '1st': False, 'premiere': False}, crests = ['flamengo', 'botafogo', 'santos'], tutorial = 1):



		#The name entered in the profile screen. Can be changed at will.
		self.team_name = team_name

		#The id of the crest selected in the profile screen. Can be changed at will.
		self.team_crest = team_crest

		#The number of team's supporters. They are sort of experience points.
		self.fans = fans

		#The team level is directly defined by the number of fans
		self.level = level

		#The ids of the cards that have been unlocked in the tournament.
		self.available_cards = available_cards

		#The ids of cards that were previously selected by the player.
		self.selected_cards = selected_cards

		#Information about the tournament being played.
		#The id can be '3rd', '2nd', '1st' and 'premiere'. The teams are the ids of teams and the
		#results can be 'none', 'win', 'lose' or 'tie'.
		self.current_tournament =current_tournament

		#A historical count of wins, defeats and ties
		self.history = history

		#The milestones mark a series of achievements available. The milestones id is the key,
		#holding a boolean that tells us if it is accomplished (True) or not (False).
		self.milestones = milestones

		#The crests available to the user.
		self.crests = crests

		#How many tutorial chapters are available for the user
		self.tutorial = tutorial


		
def write_to_save():
	print 'write_to_save function called'
	Pickle.dump(g.save,open('save','wb'))

def load_from_save():
	print 'load_from_save function called'
	g.save = Pickle.load(open('save','rb'))


# ---------------------------------------------------------------------------------
## Splash Screen ----------------
# ---------------------------------------------------------------------------------

class splashScreen(Screen):
	def __init__(self,name,**kwargs):
		super(splashScreen,self).__init__(**kwargs)
		self.name = name

		background_image = Image(source='./data/images/background-splash.png')
		self.add_widget(background_image)

		self.background_label = Image(source='./data/images/label-ocastudios.png')
		self.background_label.pos = (0,-180)
		self.background_label.opacity = 0.0
		self.add_widget(self.background_label)


		Clock.schedule_once(self.fade_in_company_name,1)
		Clock.schedule_once(self.switch_to_title_screen,2.7)

	def fade_in_company_name(self,time_elapsed):
		animation_fadein = Animation(opacity = 1.0, duration = 0.6)
		animation_fadein.start(self.background_label)
		
	def switch_to_title_screen(self,time_elapsed):
		g.manager.transition = SlideTransition(direction = 'down', duration = 1.3)
		g.screens['title'].on_called()
		g.manager.current = g.screens['title'].name

# ---------------------------------------------------------------------------------
## Title Screen -------------------------------------------------------------------
# ---------------------------------------------------------------------------------

class titleButton(Button):
	def __init__(self,btn_id,**kwargs):
		super(titleButton,self).__init__(**kwargs)
		self.name = btn_id
		self.background_normal = './data/images/btn-title-'+btn_id+'.png'
		self.background_down = './data/images/btn-title-'+btn_id+'-hover.png'
		self.bind(on_release = self.button_pressed)
		self.border = (0,0,0,0)

	def button_pressed(self, btn_object):
		if self.name == 'profile':
			g.manager.transition = SlideTransition(direction = 'right', duration = 0.6)
			g.screens['profile'].on_called()
			g.manager.current = g.screens['profile'].name
		elif self.name == '3rd-div':
			g.manager.transition = SlideTransition(direction = 'left', duration = 0.6) 
			#When calling the tournament screen, we need to inform it about the specifics of
			#tournament. If left blank, it will start a new 3rd division championship.
			#We'll pass the argument anyway
			g.screens['tournament'].request = []
			g.screens['tournament'].on_called('3rd-div')
			g.manager.current = g.screens['tournament'].name
		elif self.name == 'tutorial':
			g.manager.transition = SlideTransition(direction = 'down', duration = 1.3)
			g.screens['tutorial'].on_called()
			g.manager.current = g.screens['tutorial'].name
		else:
			print 'pressed button',self.name


class titleScreen(Screen):
	"""As the name suggests, this is the title screen. It is basically a loaded background image, with scrollable buttons at the bottom. These buttons have to change during the execution of the program and, thus, are not coded in the __init__ (loaded at the start of the program) but at the on_called (updated every time the screen is showed)."""
	def __init__(self,name,**kwargs):
		super(titleScreen,self).__init__(**kwargs)

		#vital information for changing screens
		self.name = name

		#loads background image
		background_image = Image(source='./data/images/background-title.png')
		self.add_widget(background_image)

		#creates a scrollable widget
		self.box_scroll = ScrollView()
		self.box_scroll.do_scroll_y = False
		self.box_scroll.size_hint = (None,None)
		self.box_scroll.bar_color = (1,1,1,0)

		#creates a box to hold the buttons
		self.btn_box = BoxLayout(orientation = 'horizontal')
		self.btn_box.size_hint = (None,None)

		#And add those widgets to the screen
		self.box_scroll.add_widget(self.btn_box)
		self.add_widget(self.box_scroll)


	def on_called(self):
		"""This function does two important things. First it checks if the player deservers the 'profile' milestone, giving or taking it depending on the completeness of the player's profile. It then creates the buttons that are available to the player."""
		if g.save.team_name == '' or g.save.team_crest == '':
			g.save.milestones['profile'] = False
		else:
			g.save.milestones['profile'] = True

		#Before we create the buttons, we need to erase previous buttons
		self.btn_box.clear_widgets()

		#These are all possible buttons
		btn_profile = titleButton('profile')
		btn_3rd_div = titleButton('3rd-div')
		btn_2nd_div = titleButton('2nd-div')
		btn_1st_div = titleButton('1st-div')
		btn_premiere = titleButton('premiere')
		btn_world = titleButton('world')
		btn_tutorial = titleButton('tutorial')

		#We now select all buttons that are actually available
		list_of_buttons = []
		##Profile is always present
		list_of_buttons.append(btn_profile)
		##To play the 3rd division, it is necessary to have the profile and tutorial milestones
		if g.save.milestones['profile'] and g.save.milestones['tutorial']:
			list_of_buttons.append(btn_3rd_div)
		##To play the 2nd division, it is necessary to have the profile and 3rd division milestones
		if g.save.milestones['profile'] and g.save.milestones['3rd']:
			list_of_buttons.append(btn_2nd_div)
		##To play the 1st division, it is necessary to have the profile and 2nd division milestones
		if g.save.milestones['profile'] and g.save.milestones['2nd']:
			list_of_buttons.append(btn_1st_div)
		##To play the premiere, it is necessary to have the profile and 1st division milestones
		if g.save.milestones['profile'] and g.save.milestones['1st']:
			list_of_buttons.append(btn_premiere)
		##To play the world league, it is necessary to have the profile and premiere milestones
		if g.save.milestones['profile'] and g.save.milestones['premiere']:
			list_of_buttons.append(btn_world)
		##To access the tutorial, it is necessary to have a profile
		if g.save.milestones['profile'] :
			list_of_buttons.append(btn_tutorial)

		#Depending of the number of buttons, it is necessary to reposition the widgets
		if len(list_of_buttons) == 1:
			self.box_scroll.size = (100,90)
			self.box_scroll.pos = (130,20) #was 50
			self.btn_box.size = (100,90)
		elif len(list_of_buttons) == 2:
			self.box_scroll.size = (200,90)
			self.box_scroll.pos = (80,20) #was 50
			self.btn_box.size = (200,90)
		elif len(list_of_buttons) == 3:
			self.box_scroll.size = (300,90)
			self.box_scroll.pos = (30,20) #was 50
			self.btn_box.size = (300,90)
		else:
			self.box_scroll.size = (360,90)
			self.box_scroll.pos = (0,20) #was 50
			self.btn_box.size = (100*len(list_of_buttons),90)


		#Now we add the available buttons to the box
		for btn in list_of_buttons:
			self.btn_box.add_widget(btn)



# ---------------------------------------------------------------------------------
## Profile Screen ---------------
# ---------------------------------------------------------------------------------

class nameInput(TextInput):
	"""A custom TextInput that does a little extra. It forces upper case, limits the text to 12 characters or less and aligns the text horizontally in the center both when typing and when backspacing."""

	def insert_text(self, substring, from_undo=False):
		"""This will force uppercase, limit to 12 characters and center when typing."""
		s = substring.upper()
		if len(self.text) > 11:
			s = ""

		#There's no center align in TextInput. To make up for it, we discover the
		#size of the text and use it to calculte a padding compensation.
		full_text = self.text+s
		text_width = self._get_text_width(self.text+s,self.tab_width,self._label_cached)
		desired_pos_x = (310-text_width)/2
		#Now we add the left padding
		self.padding = [desired_pos_x,-6,0,-6]

		return super(nameInput, self).insert_text(s, from_undo=from_undo)

	def force_center_alignment(self):
		#There's no center align in TextInput. To make up for it, we discover the
		#size of the text and use it to calculte a padding compensation.
		full_text = self.text
		text_width = self._get_text_width(self.text,self.tab_width,self._label_cached)
		desired_pos_x = (310-text_width)/2
		#Now we add the left padding
		self.padding = [desired_pos_x,-6,0,-6]

	def do_backspace(self, from_undo=False, mode='bkspc'):
		'''Do backspace operation from the current cursor position.
		This action might do several things:

			- removing the current selection if available.
			- removing the previous char and move the cursor back.
			- do nothing, if we are at the start.

		'''
		if self.readonly:
			return
		cc, cr = self.cursor
		_lines = self._lines
		text = _lines[cr]
		cursor_index = self.cursor_index()
		text_last_line = _lines[cr - 1]

		if cc == 0 and cr == 0:
			return
		_lines_flags = self._lines_flags
		start = cr
		if cc == 0:
			substring = u'\n' if _lines_flags[cr] else u' '
			new_text = text_last_line + text
			self._set_line_text(cr - 1, new_text)
			self._delete_line(cr)
			start = cr - 1
		else:
			#ch = text[cc-1]
			substring = text[cc - 1]
			new_text = text[:cc - 1] + text[cc:]
			self._set_line_text(cr, new_text)

		# refresh just the current line instead of the whole text
		start, finish, lines, lineflags, len_lines =\
			self._get_line_from_cursor(start, new_text)
		# avoid trigger refresh, leads to issue with
		# keys/text send rapidly through code.
		self._refresh_text_from_property('del', start, finish, lines,
                                         lineflags, len_lines)

		self.cursor = self.get_cursor_from_index(cursor_index - 1)
		# handle undo and redo
		self._set_undo_redo_bkspc(
			cursor_index,
			cursor_index - 1,
			substring, from_undo)

		self.force_center_alignment()
		##There's no center align in TextInput. To make up for it, we discover the
		##size of the text and use it to calculte a padding compensation.
		#full_text = self.text
		#text_width = self._get_text_width(self.text,self.tab_width,self._label_cached)
		#desired_pos_x = (310-text_width)/2
		##Now we add the left padding
		#self.padding = [desired_pos_x,-6,0,-6]

class crestChooser(Image):
	def __init__(self,position,**kwargs):
		super(crestChooser,self).__init__(**kwargs)
		self.source = './data/images/interface-choose-crest.png'
		self.size_hint = (None, None)
		self.size = (310,90)
		self.pos = position
		
		self.scroller = ScrollView(do_scroll_y = False, bar_color = [.0,.0,.0,.0])
		self.scroller.size_hint = (None,None)
		self.scroller.size = (310,90)
		self.scroller.pos = position

		self.crest_box = BoxLayout(orientation = 'horizontal')
		self.crest_box.size_hint = (None,None)

		self.available_crests=[] #A stub. Will be filled when the screen is called.

		self.scroller.add_widget(self.crest_box)
		self.add_widget(self.scroller)

	def get_selected(self):
		"""Returns the selected crest object. It has a 'name' property."""
		selected = 'none'
		for button in self.available_crests:
			if button.state == 'down':
				selected = button
		if selected == 'none':
			return None
		else:
			return selected

	def fill_crests(self):
		"""Places the correct crests. Loaded when the screen is called."""
		#First we erase the crests that are there already
		self.crest_box.clear_widgets()
		self.available_crests=[]
		#We read the save in search of the new available crests
		list_of_crest_names = g.save.crests
		#Then add them to the box and to a parallel list that guard the btn objects
		for name in list_of_crest_names:
			btn = ToggleButton(group = 'crests')
			btn.name = name
			btn.background_normal = './data/images/crest_'+name+'_no.png'
			btn.background_down = './data/images/crest_'+name+'.png'
			self.crest_box.add_widget(btn)
			self.available_crests.append(btn)
		#Then we align everything right
		self.crest_box.size = (len(list_of_crest_names)*90,90)
		if len(list_of_crest_names) == 3:
			self.scroller.pos = (45,self.pos[1])



class profileScreen(Screen):
	def __init__(self,name,**kwargs):
		super(profileScreen,self).__init__(**kwargs)
		self.name = name

		self.background_image = Image(source='./data/images/background-profile.png')
		self.add_widget(self.background_image)

		self.label_choose_name = Label(text="ENTER YOUR TEAM'S NAME", font_size='20sp', font_name='./data/fonts/H.H. Samuel-font-defharo.ttf', color=(1,1,1,1))
		self.label_choose_name.pos = (0,300)

		self.input_name = nameInput(height = 34, font_size=36, font_name='./data/fonts/H.H. Samuel-font-defharo.ttf', foreground_color=(0.43,0.57,0.71,1), multiline = False, padding = [155,-6,0,-6])#[80,-6,0,-6])
		self.input_name.h_align = 'center'
		self.input_name.pos = (25,566)
		self.input_name.size_hint = (None,None)
		self.input_name.size = (310,36)
		self.input_name.background_normal ='./data/images/interface-input-name.png'
		self.input_name.background_active ='./data/images/interface-input-name.png'

		self.label_choose_crest = Label(text="CHOOSE YOUR TEAM'S CREST", font_size='20sp', font_name='./data/fonts/H.H. Samuel-font-defharo.ttf', color=(1,1,1,1))
		self.label_choose_crest.pos = (0,228)

		self.crest_chooser = crestChooser(position = (25,440))

		brown = (0.22,0.46,0.03,1.0)
		dark_gray = (0.4,0.4,0.4,1.0)

		self.label_fans = Label(text="17.812 FANS (LV 3)", font_size='20sp', font_name='./data/fonts/H.H. Samuel-font-defharo.ttf', color= dark_gray, pos = (0,10))
		self.label_big_brag = Label(text="37% WINS", font_size='38sp', font_name='./data/fonts/H.H. Samuel-font-defharo.ttf', color= dark_gray, pos = (0,-29))
		self.label_small_brag = Label(text="OUT OF A TOTAL OF 21 MATCHES", font_size='20sp', font_name='./data/fonts/H.H. Samuel-font-defharo.ttf', color= dark_gray, pos = (0,-63))

		self.label_3rd_count = Label(text="x0", font_size='20sp', font_name='./data/fonts/H.H. Samuel-font-defharo.ttf', color= dark_gray, pos = (-108,-158))
		self.label_2nd_count = Label(text="x0", font_size='20sp', font_name='./data/fonts/H.H. Samuel-font-defharo.ttf', color= dark_gray, pos = (-55,-158))
		self.label_1st_count = Label(text="x0", font_size='20sp', font_name='./data/fonts/H.H. Samuel-font-defharo.ttf', color= dark_gray, pos = (0,-158))
		self.label_premiere_count = Label(text="x0", font_size='20sp', font_name='./data/fonts/H.H. Samuel-font-defharo.ttf', color= dark_gray, pos = (55,-158))
		self.label_world_count = Label(text="x0", font_size='20sp', font_name='./data/fonts/H.H. Samuel-font-defharo.ttf', color= dark_gray, pos = (108,-158))

		self.commit_button = Button(size_hint = (None,None),size = (90,90), pos = (180-45,20))
		self.commit_button.background_normal = './data/images/btn-profile-return.png'
		self.commit_button.background_down = './data/images/btn-profile-return-press.png'
		self.commit_button.bind(on_release = self.return_to_title)


		self.add_widget(self.label_choose_name)
		self.add_widget(self.input_name)
		self.add_widget(self.label_choose_crest)
		self.add_widget(self.crest_chooser)
		self.add_widget(self.label_fans)
		self.add_widget(self.label_big_brag)
		self.add_widget(self.label_small_brag)
		self.add_widget(self.label_3rd_count)
		self.add_widget(self.label_2nd_count)
		self.add_widget(self.label_1st_count)
		self.add_widget(self.label_premiere_count)
		self.add_widget(self.label_world_count)
		self.add_widget(self.commit_button)

	def on_called(self):
		"""Always called when the screen is called, preparing the screen for view. It will update the information according to the save file and give focus to the input text."""
		""" This allows us to prepare it for view."""
		#Focus input text
		self.input_name.focus = True
		#Recalling the name
		self.input_name.text = g.save.team_name
		self.input_name.force_center_alignment()
		#Placing the available crests
		self.crest_chooser.fill_crests()
		#Recalling the selected crest
		for crest in self.crest_chooser.available_crests:
			if crest.name == g.save.team_crest:
				crest.state = 'down'
			else:
				crest.state = 'normal'
		#Upadte fans information
		fans_text = '{0:,}'.format(g.save.fans)+' FANS (LV'+str(g.save.level)+')'
		self.label_fans.text = fans_text
		#Upadte big_brag information
		wins = g.save.history['win']
		ties = g.save.history['tie']
		losses = g.save.history['lose']
		if wins+ties+losses==0:
			big_brag_text = "0 MATCHES SO FAR"
		elif wins+ties+losses==1:
			big_brag_text = 'YOU PLAYED 1 MATCH'
		else:
			percentage =wins/(wins+ties+losses)
			big_brag_text = str(percentage)+'% WINS'
		self.label_big_brag.text = big_brag_text
		#Upadte small_brag information
		if wins+ties+losses==0:
			small_brag_text = 'what are you waiting for?'
		elif wins+ties+losses==1:
			if g.save.history['win']:
				small_brag_text = 'and it was an amazing victory!'
			elif g.save.history['tie']:
				small_brag_text = 'and it was... decent'
			else:
				small_brag_text = 'and it was a shameful defeat'
		else:
			small_brag_text = 'OUT OF A TOTAL OF '+str(wins+ties+losses)+' MATCHES'
		self.label_small_brag.text = small_brag_text
		#Update trophies won
		self.label_3rd_count.text = 'x'+str(g.save.history['3rd'])
		self.label_2nd_count.text = 'x'+str(g.save.history['2nd'])
		self.label_1st_count.text = 'x'+str(g.save.history['1st'])
		self.label_premiere_count.text = 'x'+str(g.save.history['premiere'])
		self.label_world_count.text = 'x'+str(g.save.history['world'])


	def return_to_title(self, button_object):
		"""Returns to title screen, commiting the changes made. It will also take the focus out of the input field."""
		self.input_name.focus = False

		g.save.team_name = self.input_name.text
		selected_crest = self.crest_chooser.get_selected()
		if selected_crest == None:
			g.save.team_crest = ''
		else:
			g.save.team_crest = selected_crest.name
		write_to_save()

		g.manager.transition = SlideTransition(direction = 'left', duration = 0.6)
		g.screens['title'].on_called()
		g.manager.current = g.screens['title'].name


# ---------------------------------------------------------------------------------
## Tutorial Screen --------------
# ---------------------------------------------------------------------------------
class tutorialButton(Button):
	def __init__(self,btn_id,**kwargs):
		super(tutorialButton,self).__init__(**kwargs)
		self.name = btn_id
		self.background_normal = './data/images/btn-tutorial-'+btn_id+'.png'
		self.background_down = './data/images/btn-tutorial-'+btn_id+'-hover.png'
		self.bind(on_release = self.button_pressed)
		self.border = (0,0,0,0)

	def button_pressed(self, btn_object):
		if self.name == 'title':
			g.manager.transition = SlideTransition(direction = 'up', duration = 1.3)
			g.screens['title'].on_called()
			g.manager.current = g.screens['title'].name
			# When leaving, you must save the game, to be sure milestones and history are kept
			write_to_save()

class tutorialScreen(Screen):
	"""The tutorial screen."""

	def __init__(self,name,**kwargs):
		super(tutorialScreen,self).__init__(**kwargs)
		self.name = name

		self.background_image = Image(source='./data/images/background-tutorial.png')
		self.add_widget(self.background_image)

		#creates a scrollable widget
		self.box_scroll = ScrollView()
		self.box_scroll.do_scroll_y = False
		self.box_scroll.size_hint = (None,None)
		self.box_scroll.bar_color = (1,1,1,0)

		#creates a box to hold the buttons
		self.btn_box = BoxLayout(orientation = 'horizontal')
		self.btn_box.size_hint = (None,None)

		#And add those widgets to the screen
		self.box_scroll.add_widget(self.btn_box)
		self.add_widget(self.box_scroll)


	def on_called(self):
		"""Always called when the screen is called, preparing the screen for view. Just by entering it once will warrant the tutorial milestone."""

		#Give tutorial milestone (hey, at least the player KNOWS there's a tutorial...)
		g.save.milestones['tutorial'] = True

		#Before we create the buttons, we need to erase previous buttons
		self.btn_box.clear_widgets()

		#These are all possible buttons
		btn_title = tutorialButton('title')

		#We now select all buttons that are actually available
		list_of_buttons = []
		##Back to title is always present
		list_of_buttons.append(btn_title)

		#Depending of the number of buttons, it is necessary to reposition the widgets
		if len(list_of_buttons) == 1:
			self.box_scroll.size = (100,90)
			self.box_scroll.pos = (130,20) #was 50
			self.btn_box.size = (100,90)
		elif len(list_of_buttons) == 2:
			self.box_scroll.size = (200,90)
			self.box_scroll.pos = (80,20) #was 50
			self.btn_box.size = (200,90)
		elif len(list_of_buttons) == 3:
			self.box_scroll.size = (300,90)
			self.box_scroll.pos = (30,20) #was 50
			self.btn_box.size = (300,90)
		else:
			self.box_scroll.size = (360,90)
			self.box_scroll.pos = (0,20) #was 50
			self.btn_box.size = (100*len(list_of_buttons),90)

		#Now we add the available buttons to the box
		for btn in list_of_buttons:
			self.btn_box.add_widget(btn)



# ---------------------------------------------------------------------------------
## Tournament Screen ------------
# ---------------------------------------------------------------------------------

class tournamentScreen(Screen):
	def __init__(self,name,**kwargs):
		super(tournamentScreen,self).__init__(**kwargs)
		self.name = name

		background_image = Image(source='./data/images/background-tournament.png')
		self.add_widget(background_image)

		# List containing widgets that must be erased, so they cam get updated.
		self.temporary_widgets = []


	def next_screen(self, button_object):
		if button_object.name == 'to_title':
			g.manager.transition = SlideTransition(direction = 'right', duration = 0.6)
			g.screens['title'].on_called()
			g.manager.current = g.screens['title'].name
		elif button_object.name == 'to_match':
			g.manager.transition = SlideTransition(direction = 'left', duration = 0.6)
			g.screens['main'].on_called()
			g.manager.current = g.screens['main'].name


	def on_called(self, details = '3rd-div'):
		"""This function runs when the tournament screen is called, so as to place the right widget according to the circunstances. The screen can be summoned in two situations: either the player has an ongoing match doesn't or he doesn't. This will change some of the widgets available.
		The detailed argument will inform if it is a new tournament, and of what division (available arguments are '3rd-div', '2nd-div', '1st-div' and 'premiere').
		If the player is resuming a tournament, then we must pass g.save.tournament."""
		brown = (0.22,0.46,0.03,1.0)
		dark_gray = (0.4,0.4,0.4,1.0)

		for widget in self.temporary_widgets:
			print 'widget', widget
			self.remove_widget(widget)

		# Sorting out main label
		division = ''
		if isinstance(details,str):
			#Then it is a new tournament
			division = details
		else:
			#Then we're loading saved data
			division = g.save.tournament['id']
		if division == '3rd-div': division = '3rd division'
		elif division == '2nd-div': division = '2nd division'
		elif division == '1st-div': division = '1st division'
		elif division == 'premiere': division = 'premiere'

		# Creating and adding main label
		self.label_division = Label(text=division, font_size='44sp', font_name='./data/fonts/MANDINGO.TTF', color= brown, pos = (0,250))
		self.add_widget(self.label_division)
		self.temporary_widgets.append(self.label_division)

		# Sorting out the teams to beat
		list_of_opponents = []
		## If it's a new tournament, we shuffle the opponents
		if isinstance(details,str):
			if division == '3rd division': list_of_opponents = ['flamengo', 'santos', 'botafogo', 'bayernmunich']
			elif division == '2nd division': list_of_opponents = ['flamengo', 'santos', 'botafogo', 'bayernmunich']
			elif division == '1st division': list_of_opponents = ['flamengo', 'santos', 'botafogo', 'bayernmunich']
			elif division == 'premiere': list_of_opponents = ['flamengo', 'santos', 'botafogo', 'bayernmunich']
			shuffle(list_of_opponents)
			print 'shuffling'
		else:
			list_of_opponents = [g.save.tournament['team1'], g.save.tournament['team2'], g.save.tournament['team3'], g.save.tournament['team4']] 
		
		#Now we blit the crests
		for team in list_of_opponents:
			crest = Image(source='./data/images/crest_'+team+'.png')
			positions = [(-48,150),(48,150), (-48,56), (48,56)]
			crest.pos = positions[list_of_opponents.index(team)]
			self.add_widget(crest)
			self.temporary_widgets.append(crest)

		#Now we blit some extra labels IF WE DID NOT LOAD A SAVE IN THE MIDDLE OF A MATCH
		is_new_game = False
		if isinstance(details,str): is_new_game = True
		elif details.match == None: is_new_game = True

		if is_new_game:
			self.button_to_title = Button(size_hint = (None,None),size = (90,90), pos = (85,20))
			self.button_to_title.name = 'to_title'
			self.button_to_title.background_normal = './data/images/btn-tournament-to-title.png'
			self.button_to_title.background_down = './data/images/btn-tournament-to-title-press.png'
			self.button_to_title.bind(on_release = self.next_screen)

			self.button_to_match = Button(size_hint = (None,None),size = (90,90), pos = (185,20))
			self.button_to_match.name = 'to_match'
			self.button_to_match.background_normal = './data/images/btn-tournament-to-match.png'
			self.button_to_match.background_down = './data/images/btn-tournament-to-match-press.png'
			self.button_to_match.bind(on_release = self.next_screen)

			self.add_widget(self.button_to_title)
			self.add_widget(self.button_to_match)
			self.temporary_widgets.append(self.button_to_title)
			self.temporary_widgets.append(self.button_to_match)

		#If we are not in midgame, we also plance the hand of cards, so the player can take his pick.
		if is_new_game:
			self.card_hand = cardHand()
			self.add_widget(self.card_hand)
			self.temporary_widgets.append(self.card_hand)
		
		#Now we print the amount of cards available to the player
		if is_new_game:
			total_cards = len(g.save.available_cards)
			if total_cards == 0: total_cards = 5 #At least five cards are available at all times
			card_number = total_cards - len(self.card_hand.get_selected())

			self.label_cards = Label(text=str(total_cards), font_size='70sp', font_name='./data/fonts/MANDINGO.TTF', color= brown, pos = (0,-60))

			self.add_widget(self.label_cards)
			self.temporary_widgets.append(self.label_cards)



# ---------------------------------------------------------------------------------
## Main Screen --------------------------------------------------------------------
# ---------------------------------------------------------------------------------


class circleButton(ButtonBehavior,Image):
	def __init__(self,**kwargs):
		super(circleButton, self).__init__(**kwargs)
		self.source='./data/images/interface-circle-black.png'
		self.size_hint = (None,None)
		self.size = (160,140)
		self.bind(on_release = self.btn_release)
		self.pos = (100,0)

		font_path = './data/fonts/MANDINGO.TTF'
		small_text = 'none'
		if g.match['play'] == 0:
			small_text = 'preparation'
		elif g.match['play'] == 1:
			small_text = 'first play'
		elif g.match['play'] == 2:
			small_text = 'second play'
		elif g.match['play'] == 3:
			small_text = 'third play'
		elif g.match['play'] == 4:
			small_text = 'fourth play'
		elif g.match['play'] == 5:
			small_text = 'fifth play'
		elif g.match['play'] == -1:
			small_text = 'finished'
		white = (1,1,1,1)
		self.small_label = Label(text=small_text,font_size='18sp',font_name=font_path, color=white)
		self.small_label.halign = 'center'
		self.small_label.valign = 'middle'
		self.small_label.pos = [self.pos[0],self.pos[1]+60]
		self.small_label.size_hint = (None,None)
		self.small_label.size = (160,100)

		#big_text = str(g.match['score_player'])+' '+str(g.match['score_opponent'])

		#self.big_label = Label(text=big_text,font_size='80sp',font_name=font_path, color=white)
		#self.big_label.halign = 'center'
		#self.big_label.valign = 'middle'
		#self.big_label.pos = [self.pos[0],self.pos[1]+4]
		#self.big_label.size_hint = (None,None)
		#self.big_label.size = (160,100)


		self.score_player = Label(text=str(g.match['score_player']), font_size='65sp', font_name=font_path, color=white)
		self.score_player.halign = 'center'
		self.score_player.valign = 'middle'
		self.score_player.pos = [self.pos[0]-43,self.pos[1]+7]
		self.score_player.size_hint = (None,None)
		self.score_player.size = (160,100)

		self.score_opponent = Label(text=str(g.match['score_opponent']), font_size='65sp', font_name=font_path, color=white)
		self.score_opponent.halign = 'center'
		self.score_opponent.valign = 'middle'
		self.score_opponent.pos = [self.pos[0]+43,self.pos[1]+7]
		self.score_opponent.size_hint = (None,None)
		self.score_opponent.size = (160,100)


		self.add_widget(self.score_player)
		self.add_widget(self.score_opponent)
		self.add_widget(self.small_label)

	def btn_release(self, marker_object):
		print "clicked button"
		g.manager.transition = SlideTransition(direction = 'up')
		g.manager.current = g.screens['title'].name


#was



class zoneMarker(ButtonBehavior,Image):
	"""There are 6 zoneMarkers in the game, indicating the strenght of the Defense, Midfield and Attack zones of each team. Besides informing how strong the zones are, they are clickable buttons that bring about popups informing about the cards attached to the zone and their effects."""
	def __init__(self,position,zone,**kwargs):
		super(zoneMarker, self).__init__(**kwargs)
		self.pos = position#(-150,215)
		self.size_hint = (None,None)
		self.size = (60,120)
		font_path = './data/fonts/MANDINGO.TTF'
		black = (0,0,0,1)
		self.zone = zone
		
		self.source='none'
		if zone == 'attack':
			self.source='./data/images/zone-attack-left-normal.png'
			self.label = Label(text=str(g.team['zone_attack']),font_size='40sp',font_name=font_path, color=black)
		elif zone == 'midfield':
			self.source='./data/images/zone-midfield-left-normal.png'
			self.label = Label(text=str(g.team['zone_midfield']),font_size='40sp',font_name=font_path, color=black)
		elif zone == 'defense':
			self.source='./data/images/zone-defense-left-normal.png'
			self.label = Label(text=str(g.team['zone_defense']),font_size='40sp',font_name=font_path, color=black)


		self.label.pos = (self.pos[0]-25,self.pos[1]+8)
		self.add_widget(self.label)
		#self.pos = (0,0)
		#self.source='./data/images/zone-attack-left-normal.png'
		#self.add_widget(image)

		self.bind(on_release = self.btn_release)

	def btn_release(self, marker_object):
		print "clicked",self.zone,"zone"
		

class job:
	"""This class represent the position slots players pins may occupy during a match. There are 23 jobs in the game, representing 13 different positions, which are divided in three Zones. The jobs are referred to by a two letter code, such as ST for strikers and CB for center-backs. The jobs are a packet of data with no visual representation (the background images are other widgets entirely)."""

	def __init__(self, position, code):
		self.is_taken = False
		self.position = position
		self.code = code
		self.zone = 'none'
		if self.code in ['st','lw','fw','rw']:
			self.zone = 'attack'
		elif self.code in ['am','lf','cm','rf','hm']:
			self.zone = 'midfield'
		else:
			self.zone = 'defense'

class player_pin(Scatter):
	"""This class represent the players in the field (which may also be called 'men' or 'pins'). There are ten of those. Their visual representation is part of this class."""
	def __init__(self,job, status_game = 'tie',status_health = 'healthy'):#job = 'st', position = (0,0)):
		#Scatter.__init__(self)

		super(player_pin, self).__init__()#**kwargs)


		self.status_game = status_game
		self.status_health = status_health
		self.job_code = job.code
		self.job_object = job
		self.do_rotation = False
		self.do_scale = False
		self.size_hint = (None,None)
		self.size = (36,36)
		self.pos = job.position[0]+180-18,job.position[1]+320-18
		self.bind(on_touch_up = self.on_release)
		
		self.reload_image()



	def reload_image(self):
		new_image = Image(source='./data/images/player-'+self.status_game+'-'+self.status_health+'.png')
		new_image.pos = (0,0)
		new_image.size = (36,36)
		self.add_widget(new_image)


	def on_release(self, player_pin, touch):
		#When you release a scatter, the mouse-up event is fired twice! This is because it fires for being
		#both 'unclicked' and 'ungrabbed'. We only place the code on one of the fired event and leave the
		#other as a stub.

		if touch.grab_current is self:
			# I receive my grabbed touch, I must ungrab it!
			#We place the code here.
			touch.ungrab(self)
	
			pos_pin = touch.pos#self.pos[:]

			closest_distance = 1000 #A mock distance, for ease of discovering a shorter one
			chosen_job = 'none' #It HAS to find a job, or the game WILL crash!

			i = 0

			#We release the player's own job, so he can find his way back, if needed
			self.job_object.is_taken = False

			for job in g.job_list:
				#print 'job pos',job.position
				i+=1

				#Job positions have a different 0,0 standard, so they must be converted. Ugly little kivy :/
				corrected_position = [job.position[0]+180-18, job.position[1] + 320-18]

				#Basic greek math to find the distance from the job to the touch up
				distance = sqrt( (corrected_position[0]-pos_pin[0]+18)**2 + (corrected_position[1]-pos_pin[1]+18)**2 )

				#If the distance is less than the current, we select this new job
				if distance < closest_distance:
					if job.is_taken == False: #Two players cannot be placed in the same job
	
						#During most times, players can't be told to move to different zones.
						if g.enforce_zones:
							if self.job_object.zone == job.zone:
								chosen_job = job
								chosen_position = corrected_position
								closest_distance = distance

						else:
							chosen_job = job
							chosen_position = corrected_position
							closest_distance = distance

			self.pos = chosen_position

			#Take the new job. First we get the job, then the code, and finally flag new job as taken.
			self.job_object = chosen_job
			self.job_code = self.job_object.code
			self.job_object.is_taken = True

		else:
			# it's a normal touch
			#This is left as a stub. This will fire no matter which pin is being moved. Be cautious with it.
			pass



class mainScreen(Screen):
	def __init__(self,name,**kwargs):
		super(mainScreen,self).__init__(**kwargs)
		self.name = name
#		if name == 'main_screen':
#			self.add_widget(layout_main())
#		
#class layout_main(FloatLayout):
#	def __init__(self,**kwargs):
#		super(layout_main,self).__init__(**kwargs)

		img_soccer_pitch = Image(source='./data/images/background-field.png')
		self.add_widget(img_soccer_pitch)

		img_bottom_bar = Image(source='./data/images/interface-lowpanel-plain.png', pos=(0, -260))
		self.add_widget(img_bottom_bar)

		with self.canvas: Rectangle(pos=(0, 120), size=(360, 3))

		img_mid_bar = Image(source='./data/images/interface-midpanel-logo.png',pos=(0, -147))
		self.add_widget(img_mid_bar)

		with self.canvas: Rectangle(pos=(0, 223), size=(360, 12))

		white_bar_label = Label(text='THESE ACTIONS ARE CURRENTLY AVAILABLE TO YOU', color = (0.67,0.67,0.67,1), font_size = 10, pos= (-100,-92), font_name = './data/fonts/H.H. Samuel-font-defharo.ttf')
		self.add_widget(white_bar_label)

		self.create_position_buttons() #Creates the positions (jobs) for the player pins
		self.deploy_players() #Automatically deploys players according to formation

		self.create_zone_markers()

		#Create card-box to receive player's cards
		self.add_widget(cardHand())

		#Add interface button (lower black circle)
		self.add_widget(circleButton())


	def create_zone_markers(self):
		self.add_widget(zoneMarker(zone = 'attack', position = (0,475)))
		self.add_widget(zoneMarker(zone = 'midfield',source='./data/images/zone-midfield-left-normal.png', position = (0,355)))
		self.add_widget(zoneMarker(zone = 'defense',source='./data/images/zone-defense-left-normal.png', position = (0,235)))


	def create_position_buttons(self):
		"""Creates the player positions, called 'jobs'. It creates both the background images for them and the job obscts, which holds the data but have no visual rendering."""

		#The background images representing the positions (jobs) and independent from the job objects, which
		#have no graphic representation. This functions creates both.
		job_list = [ ['st',(-22,250)], ['st',(22,250)], ['lw',(-86,230)], ['fw',(-42,208)], ['fw',(0,208)], ['fw',(42,208)], ['rw',(86,230)], ['am',(0,140)], ['lf',(-108,119)], ['cm',(-66,100)], ['cm',(-22,100)], ['cm',(22,100)], ['cm',(66,100)], ['rf',(108,119)], ['hm',(-22,57)], ['hm',(22,57)], ['lb',(-108,5)], ['cb',(-66,-18)], ['cb',(-22,-18)], ['cb',(22,-18)], ['cb',(66,-18)], ['rb',(108,5)], ['sw',(0,-60)] ]

		for item in job_list:
			self.add_widget(Image(source='./data/images/position-'+item[0]+'.png', pos = item[1]))			
			g.job_list.append(job(position = item[1], code = item[0]))

	def deploy_players(self):
		"""This function will assign automatic positions for the player pins, according to the formation recquirements."""
		#Each Zone has a number of players assigned to it. It also has a list of preferred positions in which the players will be assigned.

		j = g.job_list
		preferred_attack_positions = [ j[4],j[1],j[5],j[2],j[6],j[0],j[3] ]
		preferred_midfield_positions = [ j[10],j[11],j[14],j[7],j[9],j[12],j[15],j[8],j[13] ]
		preferred_defense_positions = [ j[18],j[19],j[16],j[21],j[17],j[20],j[22] ]


		#Creating attacking players
		count = 0
		for position in range(0,g.team['formation'][2]):
			self.add_widget(player_pin(job = preferred_attack_positions[count]))
			preferred_attack_positions[count].is_taken = True
			count += 1

		#Creating midfield players
		count = 0
		for position in range(0,g.team['formation'][1]):
			self.add_widget(player_pin(job = preferred_midfield_positions[count]))
			preferred_midfield_positions[count].is_taken = True
			count += 1

		count = 0
		#Creating defense players
		for position in range(0,g.team['formation'][0]):
			self.add_widget(player_pin(job = preferred_defense_positions[count]))
			preferred_defense_positions[count].is_taken = True
			count += 1


		count = 0
		for job in g.job_list:
			if job.is_taken:
				count += 1
		print 'jobs taken',count

	def on_called(self):
		pass


# ---------------------------------------------------------------------------------
## Opponent Screen ----------------------------------------------------------------
# ---------------------------------------------------------------------------------



# ---------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------


class oleApp(App):
	"""This is the main class. It sets basic parameters when initializing, and calls the main layout."""
#	icon='logo.png'
#	title='AtT Tournament'

	def build(self):
		"""Setting initial parameters and calls for creation of main layout."""
#		g.current_phase = 'main'
#		g.player_list =[]
#		g.selected_players = []
#		g.pairing = []
#		g.player_buttons = []
#		g.active_popup = None
#		g.current_round = 0
#		Clock.max_iteration = 100

		#Generate screens (runs their __init__)
		self.generate_screens()

		if g.debug_mode:
			#Load fake save
			g.save = gameSave(team_name = 'debug team', team_crest = 'bayernmunich', fans = 536628, level = 6, available_cards = [], selected_cards = [], current_tournament = {'id': 'none', 'team1': 'none', 'team2': 'none', 'team3': 'none', 'team4': 'none','results':['none','none','none','none'],'match' : None}, history ={'win':13,'tie':42,'lose':2,'3rd':12,'2nd':8,'1st':3,'premiere':1,'world':33} , milestones = {'profile': True, 'tutorial': True, '3rd': True, '2nd': False, '1st': False, 'premiere': False}, crests = ['bayernmunich', 'botafogo','flamengo','juventus','realmadrid', 'santos'], tutorial = 1000)
		elif g.debug_newbie:
			g.save = gameSave(team_name = '', team_crest = '', fans = 0, level = 1, available_cards = [], selected_cards = [], current_tournament = {'id': 'none', 'team1': 'none', 'team2': 'none', 'team3': 'none', 'team4': 'none','results':['none','none','none','none'],'match' : None}, history ={'win':0,'tie':0,'lose':0,'3rd':0,'2nd':0,'1st':0,'premiere':0,'world':0} , milestones = {'profile': False, 'tutorial': False, '3rd': False, '2nd': False, '1st': False, 'premiere': False}, crests = ['botafogo', 'flamengo', 'santos'], tutorial = 1)
		else:
			#Try to read save file. If it fails, then create a new save file.
			try:
				print 'initial called load_from_save'
				load_from_save()
			except:
				print 'initial called write_to_save'
				g.save = gameSave()
				write_to_save()

		return g.manager#layout_main()

	def on_pause(self):
		return True

	def on_resume(self):
		pass

	def generate_screens(self):
		"""Screens are generated here, in the start of the program. Initializing them will run __init__ as usual, then added to g.screen. As it happens, some things cannot be made in advance, because they depend on user input during the program (e.g. adding option buttons). These are handled in the function 'on_called', present in every screen."""

		g.manager = ScreenManager(transition = FadeTransition())
		g.screens['splash'] = splashScreen(name = 'splash_screen')
		g.screens['main'] = mainScreen(name = 'main_screen')
		g.screens['title'] = titleScreen(name = 'title_screen')
		g.screens['profile'] = profileScreen(name = 'profile_screen')
		g.screens['tournament'] = tournamentScreen(name = 'tournament_screen')
		g.screens['tutorial'] = tutorialScreen(name = 'tutorial_screen')

		g.manager.add_widget(g.screens['splash'])
		g.manager.add_widget(g.screens['title'])
		g.manager.add_widget(g.screens['main'])
		g.manager.add_widget(g.screens['profile'])
		g.manager.add_widget(g.screens['tournament'])
		g.manager.add_widget(g.screens['tutorial'])




thisApp = None

if __name__ == '__android__':
	thisApp = oleApp()
	thisApp.run()
elif __name__ == '__main__':
	Config.set('graphics','width',360)
	Config.set('graphics','height',640)
	Config.set('graphics','resizable',0)
	Config.write()
	thisApp = oleApp()
	thisApp.run()

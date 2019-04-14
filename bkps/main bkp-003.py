import kivy
kivy.require('1.8.0')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.config import Config
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.scatter import Scatter
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.checkbox import CheckBox
from kivy.uix.scrollview import ScrollView
from kivy.uix.stencilview import StencilView
from kivy.uix.modalview import ModalView
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
from random import randint
from random import choice
import random

import g

# ---------------------------------------------------------------------------------
## General Code ----------------
# ---------------------------------------------------------------------------------

#class smallCard(ButtonBehavior,Image):
#	def __init__(self, card_type, card_name, **kwargs):
#		super(smallCard, self).__init__(**kwargs)

class cardDetails(ModalView):
	"""This class will show details of a card, if the player clicked on it with the 'show details' enabled."""
	def __init__(self, card_name, **kwargs):
		super(cardDetails, self).__init__(**kwargs)

		self.background = './data/images/background-blank.png'
		self.background_color = (1,1,1,0.5)

		# First we create a relative layout where to place widgets.
		self.rl = RelativeLayout()
		self.add_widget(self.rl)

		#Then we add the card as a button
		self.card_btn = Button(size_hint = (None,None),size = (0,0), pos = (160,320)) #size = (296,420),pos = (32,110)
		self.card_btn.background_normal = './data/images/card-big-'+card_name+'.png'
		self.card_btn.background_down = './data/images/card-big-'+card_name+'.png'
		self.rl.add_widget(self.card_btn)

		self.show_card()

		self.card_btn.bind(on_release = self.quit_card)


	def show_card(self):
		anim_grow = Animation(size = (296,420), duration = 0.4, t= 'out_back')
		anim_grow &= Animation(pos = (32,110), duration = 0.4, t= 'out_back')
		anim_grow.start(self.card_btn)

	def quit_card(self, arg):
		anim_shrink = Animation(size = (0,0), duration = 0.4)
		anim_shrink &= Animation(pos = (160,320), duration = 0.4)
		anim_shrink.start(self.card_btn)
		self.dismiss()

class smallCard(ToggleButton):
	def __init__(self, card_name, card_mode = 'regular', **kwargs):
		super(smallCard, self).__init__(**kwargs)
		self.background_normal = './data/images/card-'+card_name+'.png'
		self.background_down = './data/images/card-'+card_name+'-off.png'

		self.name = card_name
		self.mode = card_mode # Must either be regular or blocked

		self.size_hint = (None,None)
		self.size = (58,100)


		self.bind(on_release = self.card_release)

	def card_release(self, marker_object):
		"""Clicking a card will have different effects depending on the active screen, and this function will pass on the event to the apropriate screen (which is its parent's parent's parent)."""
		if self.state == 'normal' and g.save.status['details'] == True:
				card_details = cardDetails(marker_object.name)
				card_details.open()
				print self.name

		self.parent.parent.update_selected()
		self.parent.parent.parent.on_card_clicked(self.name, self, self.state)

	def get_type(self):
		"""Returns what type of card self is. Possible answers are formation, tactic, defender, midfielder and attacker."""
		card_type = None
		if self.name in ['sf-343','sf-352','sf-424','sf-433','sf-442','sf-4231','sf-451','sf-kami','sf-libero','sf-metodo','sf-pyr','sf-wm']:
			card_type = 'formation'
		elif self.name in ['t-ball','t-col','t-count','t-direct','t-for','t-indiv','t-long','t-man','t-offside','t-runs','t-set','t-zone']:
			card_type = 'tactic'
		elif self.name in ['pd-fast','pd-leader','pd-talent','pd-util']:
			card_type = 'defender'
		elif self.name in ['pm-fast','pm-leader','pm-opport','pm-talent','pm-util']:
			card_type = 'midfielder'
		elif self.name in ['pa-talent','pa-leader','pa-opport']:
			card_type = 'attacker'

		return card_type

	def switch_mode(self, mode = 'switch'):
		"""This function allows us to switch the card mode from regular (selectable) to blocked (unselectable). It also affects the card appearance."""
		
		if mode == 'switch':
			if self.mode == 'regular':
				target_mode = 'blocked'
			elif self.mode == 'blocked':
				target_mode = regular
		else:
			target_mode = mode

		self.mode = target_mode
		if target_mode == 'regular':
			self.background_normal = './data/images/card-'+self.name+'.png'
			self.background_down = './data/images/card-'+self.name+'-off.png'
		elif target_mode == 'blocked':
			self.background_normal = './data/images/card-blocked-'+self.name+'.png'
			self.background_down = './data/images/card-blocked-'+self.name+'-off.png'
		

class cardHand(ScrollView):
	def __init__(self,list_of_cards = [], list_of_selected_cards = [],**kwargs):
		super(cardHand, self).__init__(**kwargs)
		#self.do_scroll_y = False
		self.size_hint = (None,None)
		self.size = (360,100)
		self.pos = (0,123)

		self.box_layout = BoxLayout(orientation = 'horizontal')
		self.box_layout.size_hint = (None,1)
		self.box_layout.width = len(list_of_cards)*58

		self.cards_available = []
		self.cards_selected = []

		#Separate cards by type
		all_formations = ['sf-343','sf-352','sf-424','sf-433','sf-442','sf-4231','sf-451','sf-kami','sf-libero','sf-metodo','sf-pyr','sf-wm']
		all_tactics = ['t-ball','t-col','t-count','t-direct','t-for','t-indiv','t-long','t-man','t-offside','t-runs','t-set','t-zone']
		all_defenders = ['pd-fast','pd-leader','pd-talent','pd-util']
		all_midfielders = ['pm-fast','pm-leader','pm-opport','pm-talent','pm-util']
		all_attackers = ['pa-talent','pa-leader','pa-opport']

		cards_formation = []
		cards_tactics = []
		cards_defenders = []
		cards_midfielders = []
		cards_attackers = []

		for card in list_of_cards:
			if card in all_formations: cards_formation.append(card)
			elif card in all_tactics: cards_tactics.append(card)
			elif card in all_defenders: cards_defenders.append(card)
			elif card in all_midfielders: cards_midfielders.append(card)
			elif card in all_attackers: cards_attackers.append(card)

		for card in cards_formation:
			card_object = smallCard(card)
			self.box_layout.add_widget(card_object)
			self.cards_available.append(card_object)

		for card in cards_tactics:
			card_object = smallCard(card)
			self.box_layout.add_widget(card_object)
			self.cards_available.append(card_object)

		for card in cards_defenders:
			card_object = smallCard(card)
			self.box_layout.add_widget(card_object)
			self.cards_available.append(card_object)
		for card in cards_midfielders:
			card_object = smallCard(card)
			self.box_layout.add_widget(card_object)
			self.cards_available.append(card_object)
		for card in cards_attackers:
			card_object = smallCard(card)
			self.box_layout.add_widget(card_object)
			self.cards_available.append(card_object)

		self.add_widget(self.box_layout)

		#Now we have to preselect some cards, to make it smoother for the player
		#Keep in mind that the selected card is 'normal', and unselected is 'down'
		for card in self.cards_available:
			if card.name in list_of_selected_cards:
				list_of_selected_cards.remove(card.name)
				card.state = 'normal'
			else:
				card.state = 'down'
		self.update_selected()
			
	def update_selected(self):
		self.cards_selected = []
		for card in self.get_available():
			if card.state == 'normal':
				self.cards_selected.append(card)
		#print 'updated cards selected',len(selected_list)
		return self.cards_selected
			
	def get_available(self):
		return self.cards_available

	def get_selected(self):
		#self.update_selected()
		self.cards_selected = []
		available_cards = self.get_available()
		for card in available_cards:
			if card.state == 'normal':
				self.cards_selected.append(card)
		return self.cards_selected

	def get_cards_by_type(self, card_type, card_state = 'all'):
		"""This functions return the list of cards of a determined card type. Possible cards types are formation, tactic, attacker, midfielder, defender or skill (which includes attacker, midfielder and defender). By default, it returns all cards available, but it can filter the results by altering the card_state to 'selected' or to 'unselected'."""
		list_of_card_objects = []
		list_of_matching_cards = []

		if card_state == 'selected':
			for card in self.get_selected():
				list_of_card_objects.append(card)
		elif card_state == 'unselected':
			for card in self.get_available():
				if card not in self.get_selected():
					list_of_card_objects.append(card)
		else:
			for card in self.get_available():
				list_of_card_objects.append(card)


		if card_type == 'skill':
			for card in list_of_card_objects:
				if card.get_type() in ['defender', 'midfielder', 'attacker']:
					list_of_matching_cards.append(card)
		else:
			for card in list_of_card_objects:
				if card.get_type() == card_type:
					list_of_matching_cards.append(card)

		return list_of_matching_cards
				
		

class gameSave():
	"""This class holds information about the user, team, statistics, etc. When the game is saved, this fie is pickled and written into the 'save' file. The game will auto-save at a number of crcunstances, including every time the profile is changed, every time the card hand is selected, after every play in the game, after the game or tournament is over and every time the player gets fans."""
	def __init__(self, status = {'name': '', 'crest': '', 'fans': 0, 'level': 1,'available_crests':['snts', 'rlmd', 'bmnc'],'laurels':{'win':0,'tie':0,'lose':0,'3rd':0,'2nd':0,'1st':0,'premiere':0,'world':0}, 'milestones':{'profile': False, 'tutorial': False, '3rd': False, '2nd': False, '1st': False, 'premiere': False}, 'details': True}, tournament = {'id': '', 'tries': 2, 'hand_size': 3, 'available_cards': [], 'selected_cards': [], 'teams': [{'name':'','result':''},{'name':'','result':''},{'name':'','result':''},{'name':'','result':''}] }, match = {'opponent': '', 'play':0, 'action': 'strategy', 'score': [0,0], 'players': [{'position':'','status':'healthy'}, {'position':'','status':'healthy'}, {'position':'','status':'healthy'}, {'position':'','status':'healthy'}, {'position':'','status':'healthy'}, {'position':'','status':'healthy'}, {'position':'','status':'healthy'}, {'position':'','status':'healthy'}, {'position':'','status':'healthy'}, {'position':'','status':'healthy'}] }):

		self.status = status
		self.tournament = tournament
		self.match = match
		
def write_to_save():#argument = None):
	#print 'saved with argument',argument
	print 'write_to_save function called'
	Pickle.dump(g.save,open('save','wb'), protocol=-1)

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

class confirmOverride(ModalView):
	def __init__(self, ref_button, **kwargs):
		super(confirmOverride,self).__init__(**kwargs)
		self.background = './data/images/background-confirm-override-tournament.png'
		self.background_color = (0,0,0,.5)

		# To give easy access to its functions
		self.ref_button = ref_button

		# We need a relative layout to be able to organize everything on screen
		self.rl = RelativeLayout()
		self.add_widget(self.rl)

		#Now we place a second background image to help us with the animation
		self.second_image = Image(source='./data/images/background-confirm-override-tournament-2.png')
		self.second_image.pos = (0,-640)
		self.rl.add_widget(self.second_image)

		# Create and add proceed button
		self.button_proceed = Button(size_hint = (None,None),size = (90,90), pos = (230,20))
		self.button_proceed.name = 'proceed'
		self.button_proceed.background_normal = './data/images/btn-confirm-override-proceed.png'
		self.button_proceed.background_down = './data/images/btn-confirm-override-proceed.png'
		self.button_proceed.bind(on_release = self.continue_to_tournament)
		self.rl.add_widget(self.button_proceed)

		# Create and add load button
		self.button_proceed = Button(size_hint = (None,None),size = (90,90), pos = (130,20))
		self.button_proceed.name = 'proceed'
		self.button_proceed.background_normal = './data/images/btn-confirm-override-load.png'
		self.button_proceed.background_down = './data/images/btn-confirm-override-load.png'
		self.button_proceed.bind(on_release = self.load_saved_tournament)
		self.rl.add_widget(self.button_proceed)

		# Create and add back button
		self.button_proceed = Button(size_hint = (None,None),size = (90,90), pos = (30,20))
		self.button_proceed.name = 'proceed'
		self.button_proceed.background_normal = './data/images/btn-confirm-override-back.png'
		self.button_proceed.background_down = './data/images/btn-confirm-override-back.png'
		self.button_proceed.bind(on_release = self.return_to_title)
		self.rl.add_widget(self.button_proceed)

		self.animation_enter()

	def animation_enter(self):
		enter_animation = Animation(pos = (0,0))
		enter_animation.start(self.second_image)

	def animation_leave(self):
		leave_animation = Animation(pos = (0,-640))
		leave_animation.start(self.second_image)

	def return_to_title(self, arg):
		self.animation_leave()
		self.dismiss()

	def load_saved_tournament(self, arg):
		self.ref_button.call_tournament(self.ref_button.name, load = True)
		self.animation_leave()
		Clock.schedule_once(self.dismiss,1)
		self.dismiss()

	def continue_to_tournament(self, arg):
		self.ref_button.call_tournament(self.ref_button.name)
		self.animation_leave()
		self.dismiss()

class titleButton(Button):
	def __init__(self,btn_id,**kwargs):
		super(titleButton,self).__init__(**kwargs)
		self.name = btn_id
		self.background_normal = './data/images/btn-title-'+btn_id+'.png'
		self.background_down = './data/images/btn-title-'+btn_id+'-hover.png'
		self.bind(on_release = self.button_pressed)
		self.border = (0,0,0,0)

	def call_tournament(self, league, load = False):

		# Teams and dealt cards are defined by league
		if league == '3rd-div':
			teams = ['sloth', 'tapir', 'paca', 'capybara']
			dealt_cards = self.deal_cards(available = 5, selected = 3)
			hand_size = 3
		elif league == '2nd-div':
			teams = ['turtle', 'opossum', 'lizard', 'wren']
			dealt_cards = self.deal_cards(available = 6, selected = 3)
			hand_size = 3
		elif league == '1st-div':
			teams = ['toucan', 'dolphin', 'wolf', 'condor']
			dealt_cards = self.deal_cards(available = 6, selected = 4)
			hand_size = 4
		elif league == 'premiere':
			teams = ['otter', 'crocodile', 'jaguar', 'penguin']
			dealt_cards = self.deal_cards(available = 7, selected = 4)
			hand_size = 4

		# Now we prepare the tournament and switch screens
		##When calling the tournament screen, we need to fill out the tournament specifics. When creating a
		##new tournament, the details will define it. (When loading, the details come from g.save.tournament.
		shuffle(teams)
		tournament_parameters = {'id': league, 'tries':2, 'hand_size': hand_size, 'available_cards': dealt_cards[0], 'selected_cards': dealt_cards[1], 'teams': [{'name':teams[0],'result':''},{'name':teams[1],'result':''},{'name':teams[2],'result':''},{'name':teams[3],'result':''}]}


		# When loading a tournament, the loading data overrides whatever button was clicked.
		if load == True:
			tournament_parameters = g.save.tournament

		g.save.tournament = tournament_parameters

		g.screens['tournament'].on_called(new_tournament = True, details = tournament_parameters)
		g.manager.transition = SlideTransition(direction = 'left', duration = 0.6) 
		g.manager.current = g.screens['tournament'].name


	def button_pressed(self, btn_object):

		#If the button pressed was profile.
		if self.name == 'profile':
			g.manager.transition = SlideTransition(direction = 'right', duration = 0.6)
			g.screens['profile'].on_called()
			g.manager.current = g.screens['profile'].name

		#If the button pressed was resume saved tournament.
		elif self.name == 'resume':
			g.manager.transition = SlideTransition(direction = 'left', duration = 0.6)
			tournament_parameters = g.save.tournament
			g.screens['tournament'].on_called(new_tournament = True, details = tournament_parameters)
			g.manager.current = g.screens['tournament'].name

		#If the button pressed was 3rd division.
		elif self.name == '3rd-div':
			if self.check_for_saved_tournament() == False:
				self.call_tournament('3rd-div')
		#If the button pressed was 2nd division.
		elif self.name == '2nd-div':
			if self.check_for_saved_tournament() == False:
				self.call_tournament('2nd-div')
		#If the button pressed was 1st division.
		elif self.name == '1st-div':
			if self.check_for_saved_tournament() == False:
				self.call_tournament('1st-div')
		#If the button pressed was 1st division.
		elif self.name == 'premiere':
			if self.check_for_saved_tournament() == False:
				self.call_tournament('premiere')
		
		#If the button pressed was tutorial.
		elif self.name == 'tutorial':
			g.manager.transition = SlideTransition(direction = 'down', duration = 0.9)#1.3)
			g.screens['tutorial'].on_called()
			g.manager.current = g.screens['tutorial'].name
		else:
			print 'pressed button',self.name

	def check_for_saved_tournament(self):
		"""This function checks if there is an ongoing tournament before another is initiated. If there is a tournament, it makes sure at least one match has actually been started. If so, it opens the confirmation modal view. If all is clear it lets the player proceed to his tournament."""
		ongoing_tournament = False

		if g.save.tournament['id'] != '':
			print 'There is a saved file'
			
			for team in g.save.tournament['teams']:
				if team['result'] != '':
					print 'team result',team['result']
					ongoing_tournament = True

		if ongoing_tournament:
			override_modal = confirmOverride(self)
			override_modal.open()


		return ongoing_tournament



	def deal_cards(self, available = 6, selected = 4, previous_available = [], previous_selected = []):
		"""This function does two things: it randomly chooses a number of cards to be 'available' for the championship, and it also choses which default set of these cards will be 'preselected'. When choosing available cards, it never repeats formation or tactics. If previous lists are provided, it will add or trim it (still not available) to conform to the number of available and selected cards requested. Also keep in mind that player cards are twice as common as the others."""

		possible_formations = ['sf-343','sf-352','sf-433','sf-442','sf-4231','sf-kami','sf-libero','sf-metodo','sf-pyr','sf-wm']
		possible_tactics = ['t-ball','t-col','t-count','t-direct','t-for','t-indiv','t-long','t-man','t-offside','t-runs','t-set','t-zone']
		possible_men = ['pa-fast','pa-leader','pa-opport','pd-fast','pd-leader','pd-talent','pd-util','pm-fast','pm-leader','pm-opport','pm-talent','pm-util']

		# Add available
		new_available = []
		dif_available = available-len(previous_available)

		print 'previous available cards:', previous_available, 'previous selected cards:', previous_selected

		if dif_available<0:
			pass
		elif dif_available>0:
			while dif_available:
				chance = random.randint(1,4)

				#Adds a player card to the available list
				if chance <3:
					card = random.choice(possible_men)
					new_available.append(card)
					dif_available -= 1

				#Tries to add a tactic card to the available list. It cannot be repeated.
				elif chance ==3:
					card = random.choice(possible_tactics)
					if card in previous_available or card in new_available:
						pass
					else:
						new_available.append(card)
						dif_available -= 1

				#Tries to add a formation card to the available list. It cannot be repeated.
				else:
					#selected formation
					card = random.choice(possible_formations)
					if card in previous_available or card in new_available:
						pass
					else:
						new_available.append(card)
						dif_available -= 1

		all_available = previous_available+new_available



		# Now we must choose some cards to be pre-selected, to make the game smoother, specially to new players.
		# The rules are, only one formation and one tactic, and preferably there must be both of them.

		#We create these lists in order to separate the cards into types, since we can't repeat tactics and formations.
		available_formations = []
		available_tactics = []
		available_men = []

		
		new_selected = []

		# This tells us how many cards to pick. Also, for each card we lack, we loop once.
		dif_selected = selected-len(previous_selected)

		print 'card_ difference',dif_selected

		if dif_selected<0: #If we have more selected than what's allowed
			pass

		elif dif_selected==0: #If we have exactly as many selected as it is allowed
			pass

		elif dif_selected>0: #Now, let us pick some cards...

			#This will fill the lists, separating available the cards into types
			for card in all_available:
				if card in possible_formations:
					available_formations.append(card)
				elif card in possible_tactics:
					available_tactics.append(card)
				elif card in possible_men:
					available_men.append(card)
			
			# To keep track if a formation and a tactic have been selected.
			has_selected_formation = False
			has_selected_tactic = 0
			men_count = 0 #Will prevent endless loop in the future
			for card in previous_selected:
				if card in possible_formations:
					has_formation = True
				if card in possible_tactics:
					has_tactics = True

			# Now we loop, seeking for the desired cards.
			while dif_selected:
				if has_selected_formation == False and len(available_formations)>0:
					card = random.choice(available_formations)
					new_selected.append(card)
					available_formations.remove(card)
					has_selected_formation = True
					dif_selected -= 1
					print 'selected card'
				elif has_selected_tactic == False and len(available_tactics)>0:
					card = random.choice(available_tactics)
					new_selected.append(card)
					available_tactics.remove(card)
					has_selected_tactic = True
					dif_selected -= 1
					print 'selected card'
				elif len(available_men)>0: # men_count<dif_selected and 
					card = random.choice(available_men)
					new_selected.append(card)
					available_men.remove(card)
					men_count += 1
					dif_selected -= 1
					print 'selected card'
				else:
					dif_selected -= 1 #Escape possible infinite loop
					print 'select loop out', 'count:',dif_selected, 'cards to select', selected, 'previously selected',len(previous_selected), 'available men',available_men

			all_selected = previous_selected + new_selected
			
			return [all_available, all_selected]
	

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

		#Check if the profile is complete. If not, remove profile milestone.
		if g.save.status['name'] == '' or g.save.status['crest'] == '':
			g.save.status['milestones']['profile'] = False
		else:
			g.save.status['milestones']['profile'] = True

		#Before we create the buttons, we need to erase previous buttons
		self.btn_box.clear_widgets()

		#These are all possible buttons
		btn_profile = titleButton('profile')
		btn_resume = titleButton('resume')
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
		##But all others require the profile milestone
		if g.save.status['milestones']['profile']:
			##To load a saved tournament, there must be a saved tournament available
			##On the saved tournament, also at least one game ust have been initiatied
			if g.save.tournament['id'] is not '':
				tournament_began = False
				for team in g.save.tournament['teams']:
					if team['result'] is not '':
						tournament_began = True
				if tournament_began == True:
					list_of_buttons.append(btn_resume)
			##To play the 3rd division, it is necessary to have the profile and tutorial milestones
			if g.save.status['milestones']['tutorial']:
				list_of_buttons.append(btn_3rd_div)
			##To play the 2nd division, it is necessary to have the profile and 3rd division milestones
			if g.save.status['milestones']['3rd']:
				list_of_buttons.append(btn_2nd_div)
			##To play the 1st division, it is necessary to have the profile and 2nd division milestones
			if g.save.status['milestones']['2nd']:
				list_of_buttons.append(btn_1st_div)
			##To play the premiere, it is necessary to have the profile and 1st division milestones
			if g.save.status['milestones']['1st']:
				list_of_buttons.append(btn_premiere)
			##To play the world league, it is necessary to have the profile and premiere milestones
			if g.save.status['milestones']['premiere']:
				list_of_buttons.append(btn_world)
			##To access the tutorial, it is necessary to have a profile
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

	def fill_crests(self, list_of_crest_names):
		"""Places the correct crests. Loaded when the screen is called."""
		#First we erase the crests that are there already
		self.crest_box.clear_widgets()
		self.available_crests=[]
		##We read the save in search of the new available crests
		#list_of_crest_names = g.save.crests
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
		self.input_name.text = g.save.status['name']
		self.input_name.force_center_alignment()
		#Placing the available crests
		self.crest_chooser.fill_crests(g.save.status['available_crests'])
		#Recalling the selected crest
		for crest in self.crest_chooser.available_crests:
			if crest.name == g.save.status['crest']:
				crest.state = 'down'
			else:
				crest.state = 'normal'
		#Upadte fans information
		fans_text = '{0:,}'.format(g.save.status['fans'])+' FANS (LV'+str(g.save.status['level'])+')'
		self.label_fans.text = fans_text
		#Upadte big_brag information
		wins = g.save.status['laurels']['win']
		ties = g.save.status['laurels']['tie']
		losses = g.save.status['laurels']['lose']
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
			if g.save.status['laurels']['win']:
				small_brag_text = 'and it was an amazing victory!'
			elif g.save.status['laurels']['tie']:
				small_brag_text = 'and it was... decent'
			else:
				small_brag_text = 'and it was a shameful defeat'
		else:
			small_brag_text = 'OUT OF A TOTAL OF '+str(wins+ties+losses)+' MATCHES'
		self.label_small_brag.text = small_brag_text
		#Update trophies won
		self.label_3rd_count.text = 'x'+str(g.save.status['laurels']['3rd'])
		self.label_2nd_count.text = 'x'+str(g.save.status['laurels']['2nd'])
		self.label_1st_count.text = 'x'+str(g.save.status['laurels']['1st'])
		self.label_premiere_count.text = 'x'+str(g.save.status['laurels']['premiere'])
		self.label_world_count.text = 'x'+str(g.save.status['laurels']['world'])


	def return_to_title(self, button_object):
		"""Returns to title screen, commiting the changes made. It will also take the focus out of the input field."""
		self.input_name.focus = False

		g.save.status['name'] = self.input_name.text
		selected_crest = self.crest_chooser.get_selected()
		if selected_crest == None:
			g.save.status['crest'] = ''
		else:
			g.save.status['crest'] = selected_crest.name
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
			g.manager.transition = SlideTransition(direction = 'up', duration = 0.9)#1.3)
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
		g.save.status['milestones']['tutorial'] = True

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

class crestButton(Button):
	def __init__(self, team, next = False, **kwargs):
		super(crestButton,self).__init__(**kwargs)

		self.team = team
		self.size_hint = (None,None)
		self.size = (90,90)

		if next == True:
			self.background_normal = './data/images/crest_'+team['name']+'.png'
			self.background_down = './data/images/crest_'+team['name']+'.png'
		else:
			self.background_normal = './data/images/crest_'+team['name']+'_no.png'
			self.background_down = './data/images/crest_'+team['name']+'_no.png'

		position_list = [(-48+180-45,150+320-45),(48+180-45,150+320-45), (-48+180-45,56+320-45), (48+180-45,56+320-45)]
		self.pos = position_list[g.save.tournament['teams'].index(team)]

		if team['result'] is not '':
			sign = Image(source='./data/images/crest-marker-'+team['result']+'.png')
			sign.size_hint = (None,None)
			sign.size = (90,90)
			sign.pos = position_list[g.save.tournament['teams'].index(team)]
			self.add_widget(sign)

		self.bind(on_release = self.crest_click)

	def crest_click(self, btn_object):
		card_details = cardDetails('team-'+self.team['name'])
		card_details.open()


class tournamentScreen(Screen):
	def __init__(self,name,**kwargs):
		super(tournamentScreen,self).__init__(**kwargs)
		self.name = name

		background_image = Image(source='./data/images/background-tournament.png')
		self.add_widget(background_image)

		self.card_details_btn = ToggleButton(size_hint = (None,None), size = (110,20))
		self.card_details_btn.background_normal = './data/images/btn-tutorial-details-long.png'
		self.card_details_btn.background_down = './data/images/btn-tutorial-details-long-down.png'
		self.card_details_btn.pos = (4,2)
		self.card_details_btn.bind(on_release = self.clicked_card_details_btn)
		self.add_widget(self.card_details_btn)

		# List containing widgets that must be erased, so they cam get updated.
		self.temporary_widgets = []




	def on_called(self, new_tournament = False, details = '3rd-div'):
		"""This function runs when the tournament screen is called, so as to place the right widget according to the circunstances. The screen can be summoned in two situations: either the player has an ongoing match doesn't or he doesn't. This will change some of the widgets available.
		The detailed argument will inform if it is a new tournament, and of what division (available arguments are '3rd-div', '2nd-div', '1st-div' and 'premiere').
		If the player is resuming a tournament, then we must pass g.save.tournament."""
		brown = (0.22,0.46,0.03,1.0)
		brown_transparent = (0.22,0.46,0.03,0.5)
		dark_gray = (0.4,0.4,0.4,1.0)

		is_new_tournament = new_tournament
		tournament = None

		if is_new_tournament:
			g.save.tournament = details
		tournament = g.save.tournament

		self.league = tournament['id']

		if g.save.status['details'] == True:
			self.card_details_btn.state = 'down'
		else:
			self.card_details_btn.state = 'normal'

		#Remove temporary widgets, so we can replace them
		for widget in self.temporary_widgets:
			self.remove_widget(widget)


		# Creating and adding main label
		division = tournament['id']
		if division == '3rd-div': division = '3rd division'
		elif division == '2nd-div': division = '2nd division'
		elif division == '1st-div': division = '1st division'
		elif division == 'premiere': division = 'premiere'
		self.label_division = Label(text=division, font_size='44sp', font_name='./data/fonts/MANDINGO.TTF', color= brown, pos = (0,250))
		self.add_widget(self.label_division)
		self.temporary_widgets.append(self.label_division)

		# Creating and adding tries counter
		tries = tournament['tries']
		self.label_tries_counter = Label(text='THIS IS THE TRY COUNTER', font_size='20sp', font_name='./data/fonts/H.H. Samuel-font-defharo.ttf', color= brown_transparent, pos = (0,-6))
		self.add_widget(self.label_tries_counter)
		self.temporary_widgets.append(self.label_tries_counter)
		self.update_tries_counter()
	

		# Blitting opponent's crests
		#We have to figure the next opponent. The one that haven't been played is the first choice.
		g.next_team = None
		for team in tournament['teams']:
			if team['result'] == '' and g.next_team == None:
				g.next_team = team
		#Then we check for teams against the player tied or lost.
		if g.next_team == None:
			for team in tournament['teams']:
				if team['result'] is not 'win' and g.next_team == None:
					g.next_team = team

		#Now we blit the crests and result signs
		for team in tournament['teams']:
			if team == g.next_team:
				crest = crestButton(team, next = True)
			else:
				crest = crestButton(team, next = False)
			self.add_widget(crest)
			self.temporary_widgets.append(crest)


		#Now we blit some extra labels IF WE DID NOT LOAD A SAVE IN THE MIDDLE OF A MATCH
		is_new_match = False

		if is_new_tournament:
			is_new_match = True
		#elif details.match == None:
		#	is_new_game = True
		else:
			is_new_match = True

		if is_new_match:
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

		#If we are not in midgame, we also place the hand of cards, so the player can take his pick.
		if is_new_match:
			self.card_hand = cardHand(tournament['available_cards'], tournament['selected_cards'])
			self.add_widget(self.card_hand)
			self.temporary_widgets.append(self.card_hand)
		
		#Now we print the amount of cards available to the player
		if is_new_match:
			total_cards = tournament['hand_size']
			##At least five cards are available at all times
			#if total_cards == 0:
			#	total_cards = 5
			card_number = total_cards - len(self.card_hand.get_selected())

			self.label_hand_size = Label(text=str(card_number), font_size='70sp', font_name='./data/fonts/MANDINGO.TTF', color= brown, pos = (0,-60))
			self.add_widget(self.label_hand_size)
			self.temporary_widgets.append(self.label_hand_size)

			#Ugly kivy. To animate the font, we need to keep a static refrence. Calling from the widget itself
			#could permanently overwrite its size with one of mid animation. But, alas, the animation function
			#does not accept "sp", so we must leave another reference. Not cool...
			self.HAND_SIZE_FONT_SIZE = self.label_hand_size.font_size


	def clicked_card_details_btn(self, arg):
		if self.card_details_btn.state == 'normal':
			g.save.status['details'] = False
			print 'detail btn normal',g.save.status['details']
		else:
			g.save.status['details'] = True
			print 'detail btn down',g.save.status['details']
		write_to_save()


	def next_screen(self, button_object):
		if button_object.name == 'to_title':
			g.manager.transition = SlideTransition(direction = 'right', duration = 0.6)
			g.screens['title'].on_called()
			g.manager.current = g.screens['title'].name
		elif button_object.name == 'to_match':
			card_list = []
			for card in self.card_hand.get_selected():
				card_list.append(card.name)
			g.save.tournament['id'] = self.league
			g.save.tournament['available_cards'] = card_list

			g.save.match['play'] = 0
			g.save.match['score'] = [0,0]
			g.save.match['players'] = [{'position':'','status':'healthy'}, {'position':'','status':'healthy'}, {'position':'','status':'healthy'}, {'position':'','status':'healthy'}, {'position':'','status':'healthy'}, {'position':'','status':'healthy'}, {'position':'','status':'healthy'}, {'position':'','status':'healthy'}, {'position':'','status':'healthy'}, {'position':'','status':'healthy'}]

			print g.save.status
			print g.save.tournament
			print g.save.match
			write_to_save()

			g.manager.transition = SlideTransition(direction = 'left', duration = 0.6)
			g.screens['transition'].on_called()
			g.manager.current = g.screens['transition'].name


	def on_card_clicked(self, card_name, card_object, card_state):
		"""This functions will run every time a card is clicked. When it happens, we have to update the card display."""

		#If we have more selected cards than our card size, we must force unclick the new card
		card_limit = g.save.tournament['hand_size']
		current_hand_size = len(self.card_hand.get_selected())
		if card_object.state == 'normal' and current_hand_size > card_limit:
			card_object.state = 'down'
			card_object.card_release(card_object)
		self.update_hand_size()

	def update_hand_size(self):
		cards_selected = self.card_hand.get_selected()
		remaining_cards = g.save.tournament['hand_size'] - len(cards_selected)

		full_size = self.HAND_SIZE_FONT_SIZE
		
		pop = Animation(font_size = full_size, duration = 0.2, t= 'out_back')#'in_out_elastic')
		self.label_hand_size.text = str(remaining_cards)

		self.label_hand_size.font_size = 0
		pop.start(self.label_hand_size)

	def update_tries_counter(self):
		tries = g.save.tournament['tries']
		if tries == 0:
			self.label_tries_counter.text = 'THIS IS YOUR LAST CHANCE'
		elif tries == 1:
			self.label_tries_counter.text = 'YOU MAY ONLY LOSE ONCE'
		elif tries == 2:
			self.label_tries_counter.text = 'YOU MAY LOSE TWICE'
		elif tries >= 3:
			self.label_tries_counter.text = 'YOU HAVE '+str(tries)+' MORE TRIES'
		

# ---------------------------------------------------------------------------------
## Transition Screen --------------------------------------------------------------------
# ---------------------------------------------------------------------------------

class transitionScreen(Screen):
	def __init__(self, name, **kwargs):
		super(transitionScreen,self).__init__(**kwargs)
		self.name = name
		self.opponent = None

		background_image = Image(source='./data/images/background-transition.png')
		self.add_widget(background_image)
		self.temporary_widgets = []

	def on_called(self):
		gray = (0,0,0,.4)
		brown = (0.22,0.46,0.03,1.0)
		mandingo = './data/fonts/MANDINGO.TTF'
		hhs = './data/fonts/H.H. Samuel-font-defharo.ttf'

		# Let us clear the new g.save.match
		g.save.match['opponent'] = g.next_team['name']
		print 'transition',g.next_team
		g.save.match['play'] = 0
		g.save.match['score'] = [0,0]

		# And get the opponent's info
		self.opponent = g.opponents[g.next_team['name']]

		self.game_label_warn = Label(text='YOUR OPPONENTS ARE', font_size='20sp', font_name=hhs, color= gray, pos = (0,80))
		self.game_label_origin = Label(text='THE '+self.opponent['origin'].upper(), font_size='20sp', font_name=hhs, color= gray, pos = (0,55))
		self.game_label_name = Label(text=self.opponent['name'], font_size='50sp', font_name=mandingo, color= brown, pos = (0,12))
		self.game_label_score = Label(text=str(g.save.match['score'][0])+'-'+str(g.save.match['score'][1]), font_size='40sp', font_name=hhs, color= gray, pos = (0,-40))
		self.game_label_play = Label(text=str(g.save.match['play'])+' play', font_size='20sp', font_name=hhs, color= gray, pos = (0,-70))

		for label in [self.game_label_warn, self.game_label_origin, self.game_label_name, self.game_label_score, self.game_label_play]:
			self.temporary_widgets.append(label)
			self.add_widget(label)

		Clock.schedule_once(self.proceed_to_match,2.5)



	def proceed_to_match(self, time_elapsed):
		g.manager.transition = SlideTransition(direction = 'left', duration = 0.6)#1.3)
		g.screens['main'].on_called()
		g.manager.current = g.screens['main'].name
		

# ---------------------------------------------------------------------------------
## Main Screen --------------------------------------------------------------------
# ---------------------------------------------------------------------------------
class checkRoll(ModalView):
	def __init__(self, **kwargs):
		super(checkRoll,self).__init__(**kwargs)

		self.mandingo_font = './data/fonts/MANDINGO.TTF'
		self.brown = (0.56,0.64,0.35,1.0)#(0.22,0.46,0.03,1.0)
		self.dark_brown = (0.24,0.31,0.16,1.0)
		self.dark_gray = (0.4,0.4,0.4,1.0)
		self.purple = (0.56,0.29,0.65,1.0)

		self.main_screen = g.screens['main']

		try:
		#This has being causing weird behavior in the hard code.
			# Ugly kivy. We MUST give a static background, so we use this fake one.
			self.background = './data/images/background-black.png'
			#self.background = './data/images/background-blank.png'
			self.background_color = (0,0,0,.5)
		except Exception, error_code:
			print error_code, '\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n'


#--------------------------------------------------------------


		print 'a'
		# Ugly kivy. To have the proer animation we need to have a base relative layout...
		self.relative_layout_base = RelativeLayout()
		self.add_widget(self.relative_layout_base)
		print 'b'

		# ...and then another relative layout to actually animate.
		self.rl = RelativeLayout(size_hint = (None,None),size = (360,640),pos = (0,640))
		self.relative_layout_base.add_widget(self.rl)

		print 'c'

		#Now we the widgets into the background image
		self.animated_bg = Image( source='./data/images/interface-check-background.png', pos = (0,0) )

		print 'd'

		if g.save.match['action'] == 'preparation':
			title_text = 'midfield check'
			str_friend = self.main_screen.zone_str['friend']['mid']
			str_foe = self.main_screen.zone_str['foe']['mid']
		elif g.save.match['action'] == 'defense':
			title_text = 'defense check'
			check_type = 'defense'
			str_friend = self.main_screen.zone_str['friend']['def']
			str_foe = self.main_screen.zone_str['foe']['atk']
		elif g.save.match['action'] == 'attack':
			title_text = 'attack check'
			check_type = 'attack'
			str_friend = self.main_screen.zone_str['friend']['atk']
			str_foe = self.main_screen.zone_str['foe']['def']
		else:
			title_text = 'error'
			str_friend = 0
			str_foe = 0
		print 'e'

		dice_result = [random.randint(0,5),random.randint(0,5),random.randint(0,5),random.randint(0,5)]

		total_friend = str_friend+dice_result[0]+dice_result[1]
		total_foe = str_foe+dice_result[2]+dice_result[3]
		print 'f'

		if total_friend>total_foe:
			if g.save.match['action'] == 'preparation':
				conclusion_text = 'you get to attack'
			if g.save.match['action'] == 'defense':
				conclusion_text = 'your defense won'
			if g.save.match['action'] == 'attack':
				conclusion_text = 'gooooal!'
		elif total_friend<total_foe:
			if g.save.match['action'] == 'preparation':
				conclusion_text = 'you must defend'
			if g.save.match['action'] == 'defense':
				conclusion_text = 'shucks! they scored'
			if g.save.match['action'] == 'attack':
				conclusion_text = 'the attack failed'
		elif total_friend==total_foe:
			if g.save.match['action'] == 'preparation':
				conclusion_text = 'no one attacks'
			if g.save.match['action'] == 'defense':
				conclusion_text = 'you dodged a bullet'
			if g.save.match['action'] == 'attack':
				conclusion_text = 'oh! that was close'
		print 'g'

		self.title_label = Label(text=title_text,font_size='40sp',font_name=self.mandingo_font, color=self.brown, pos = (0,282))

		self.zone_marker_friend = Image( source='./data/images/interface-check-str-mid.png', pos=(-74,196) )
		self.zone_marker_foe = Image( source='./data/images/interface-check-str-mid.png', pos=(74,196) )
		print 'h'

		
		self.str_friend = Label(text=str(str_friend),font_size='40sp',font_name=self.mandingo_font, color=self.dark_brown, pos = (-75,194))
		self.str_foe = Label(text=str(str_foe),font_size='40sp',font_name=self.mandingo_font, color=self.dark_brown, pos = (75,194))
		print 'i'

		self.die1_friend = Image( source='./data/images/interface-die-'+str(dice_result[0])+'.png', pos=(-74,102) )
		self.die1_foe = Image( source='./data/images/interface-die-'+str(dice_result[2])+'.png', pos=(74,102) )
		self.die2_friend = Image( source='./data/images/interface-die-'+str(dice_result[1])+'.png', pos=(-74,38) )
		self.die2_foe = Image( source='./data/images/interface-die-'+str(dice_result[3])+'.png', pos=(74,38) )
		print 'j'

		self.result_label_friend = Label(text=str(str_friend+dice_result[0]+dice_result[1]),font_size='60sp',font_name=self.mandingo_font, color=self.dark_brown, pos = (-73,-56))
		self.result_label_foe = Label(text=str(str_foe+dice_result[2]+dice_result[3]),font_size='60sp',font_name=self.mandingo_font, color=self.dark_brown, pos = (73,-56))
		print 'k'

		self.sign_plus_friend = Image( source='./data/images/interface-sign-plus.png', pos=(-24,37) )
		self.sign_plus_foe = Image( source='./data/images/interface-sign-plus.png', pos=(134,37) )
		self.sign_equal_friend = Image( source='./data/images/interface-sign-equal.png', pos=(-73,-9) )
		self.sign_equal_foe = Image( source='./data/images/interface-sign-equal.png', pos=(78,-9) )
		print 'l'

		self.label_result = Label(text=conclusion_text,font_size='40sp',font_name=self.mandingo_font, color=self.brown, pos = (0,-122))
		self.label_click = Label(text='click to continue',font_size='20sp',font_name=self.mandingo_font, color=self.purple, pos = (0,-167))
		print 'm'

		self.sign_arrow = Image( source='./data/images/interface-check-arrow-down.png', pos=(-103,-217) )

		self.rl.add_widget(self.animated_bg)
		self.rl.add_widget(self.title_label)
		self.rl.add_widget(self.zone_marker_friend)
		self.rl.add_widget(self.zone_marker_foe)
		self.rl.add_widget(self.str_friend)
		self.rl.add_widget(self.str_foe)
		self.rl.add_widget(self.die1_friend)
		self.rl.add_widget(self.die1_foe)
		self.rl.add_widget(self.die2_friend)
		self.rl.add_widget(self.die2_foe)
		self.rl.add_widget(self.result_label_friend)
		self.rl.add_widget(self.result_label_foe)
		self.rl.add_widget(self.sign_plus_friend)
		self.rl.add_widget(self.sign_plus_foe)
		self.rl.add_widget(self.sign_equal_friend)
		self.rl.add_widget(self.sign_equal_foe)
		self.rl.add_widget(self.label_result)
		self.rl.add_widget(self.label_click)
		self.rl.add_widget(self.sign_arrow)
		print 'n'

		self.pop_list = [self.zone_marker_friend, self.str_friend, self.zone_marker_foe, self.str_foe, self.die1_friend, self.die1_foe, self.die2_friend, self.die2_foe, self.sign_plus_friend, self.sign_plus_foe, self.sign_equal_friend, self.sign_equal_foe, self.result_label_friend, self.result_label_foe, self.label_result, self.label_click, self.sign_arrow]
		print 'o'
		for widget in self.pop_list:
			if widget.__class__ == Label:
				widget.final_font_size = widget.font_size
				widget.font_size = 0
			else:
				widget.final_size = widget.size[:]
				widget.final_pos = [ widget.pos[0]+180-widget.final_size[0]/2,widget.pos[1]+320-widget.final_size[1]/2 ]
				widget.size_hint = (None,None)
				widget.size = (0,0)
				widget.pos = [ widget.pos[0]+180,widget.pos[1]+320 ]


		print 'p'

		#Now we add the title label to the animated_bg, so it animates with it.
		#The other widgets will pop afterwards.


		#Add the confirm button
		self.confirm_button = Button( background_normal='./data/images/interface-circle-ball.png', background_down='./data/images/interface-circle-ball.png' )#, pos = (100,-320) )
		self.confirm_button.size_hint = (None,None)
		self.confirm_button.size = (160,140)
		self.confirm_button.pos = (180-80,0)

		print 'q'


		self.confirm_button.bind(on_release = self.confirm_release)
		self.relative_layout_base.add_widget(self.confirm_button)
		print 'r'

		self.animation_enter()
		print 's'

#--------------------------------------------------------------
		self.count = 0

		#self.animation_pop()
		#Clock.schedule_once(self.animation_pop, 1.2)
		self.animation_pop()

		print 'list of widgets to animate',self.pop_list, len(self.pop_list)

	def confirm_release(self, btn_object):
		print 'button clicked'

	def animation_pop(self, lapsed_time = 0.0):
		print 'self.count',self.count
		self.count +=1
		if len(self.pop_list) > 0:
			print 'stuff is bigger than 0'
			widget = self.pop_list[0]
			#print 'animate widget',widget
			if widget.__class__ == Label:
				print 'this stuff is label'
				pop = Animation(font_size = widget.final_font_size, duration = 0.6, transition = 'out_back')
			else:
				print 'this stuff is not label'
				pop = Animation(size = widget.final_size, pos = widget.final_pos, duration = 0.6, transition = 'out_back')
			pop.start(widget)
			self.pop_list.remove(widget)
			#self.animation_pop()
			Clock.schedule_once(self.animation_pop, 0.12)
		else:
			print 'abracadabra'

	def animation_enter(self):
		enter_animation = Animation(pos = (0,0), duration = 4.0)
		enter_animation.start(self.rl)

	def animation_leave(self):
		leave_animation = Animation(pos = (0,-640))
		leave_animation.start(self.animated_bg)

class circleButton(Button):#(ButtonBehavior,Image):
	def __init__(self,**kwargs):
		super(circleButton, self).__init__(**kwargs)
		#self.source='./data/images/interface-circle-ball.png'#-black.png
		self.background_normal='./data/images/interface-circle-ball.png'#-black.png
		self.background_down='./data/images/interface-circle-ball.png'#-pressed.png'#-black.png
		self.size_hint = (None,None)
		self.size = (160,140)
		self.bind(on_release = self.btn_release)
		self.pos = (100,0)

	def btn_release(self, marker_object):
		""" When the main button is clickes, it changes the stage (action) of the game, which will certainly change the widgets. This functions deal with what happens when the button is clicked, depending on what the current stage is."""
		print "clicked button"

		#message = labelMessage()
		action = g.save.match['action']
		game_play = g.save.match['play']

		if action == 'strategy':
			# Only once per match may the button be pressed during the strategy stage.
			#When it happens, we must blit the approppriate lacking widgets, and update the game play and action.
			action = 'preparation'
			match_play = 1
			g.save.match['action'] = 'preparation'
			g.save.match['play'] = 1
			#self.parent.prepare_layout()#load_widgets_preparation()

			print 'turned action from', g.save.match['action'],'to',action


			write_to_save()


		elif action == 'preparation':
			#self.parent.interrupt_messages = True
			print 'STEP1'
			self.midfield_check_modal = checkRoll()
			print 'STEP2'
			self.parent.add_widget(self.midfield_check_modal)
			print 'STEP3'
			
			action = 'midfield'


		elif action == 'midfield':
			action = 'defense'
		elif action == 'defense':
			action = 'attack'
		elif action == 'attack':
			action = 'counterattack_against'
		elif action == 'counterattack_against':
			action = 'counterattack_for'
		elif action == 'counterattack_for':
			action = 'rebound_against'
		elif action == 'rebound_against':
			action = 'free_kick'
		elif action == 'free_kick':
			action = 'strategy'

		#print 'turned action from', g.save.match['action'],'to',action


		#write_to_save()


			


		stages = []


#		if message.abort == False:
#			self.add_widget(message)
#		#g.manager.transition = SlideTransition(direction = 'up')
#		#g.manager.current = g.screens['title'].name



class zoneMarker(ButtonBehavior,Image):
	"""There are 6 zoneMarkers in the game, indicating the strength of the Defense, Midfield and Attack zones of each team. Besides informing how strong the zones are, they are clickable buttons that bring about popups informing about the cards attached to the zone and their effects."""
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
		

class Job:
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


class labelMessage(Label):
	"""This massages will be displayed throughout the game."""
	def __init__(self,message = 'THIS IS A TEXT MESSAGE', relevance = 'comment',**kwargs):
		super(labelMessage,self).__init__(**kwargs)
		self.text = message
		self.relevance = relevance # Can be 'primary', 'secondary', 'tutorial' or 'comment'.
		self.end_color = (0,0,1,1)


		#print 'message',message,'relevance',relevance
		if self.relevance == 'primary':
			self.color = (1,1,1,1)
			self.end_color = (0,0,0,.6)
		elif self.relevance == 'secondary':
			self.color = (1,1,1,1)
			self.end_color = (1,1,1,0)
		elif self.relevance == 'tutorial':
			self.color = (.91,0.93,0.82,1)
			self.end_color = (.91,0.93,0.82,0)
		elif self.relevance == 'comment':
			self.color = (0.71,0.73,0.62,1)
			self.end_color = (0.71,0.73,0.62,0)
		else:
			self.color = (0,0,1,1)
			self.end_color = (0,0,1,1)
			print 'wrong relevance tag'

		self.create_message()

	def create_message(self):

		self.font_size = 0
		self.font_name = './data/fonts/H.H. Samuel-font-defharo.ttf'
		#self.padding = (0,0)

		self.size = (0,0)

		##Ugly Kivy! We can't animate the label aligned by the left. As a workaround,
		##we need to know the positions and sizes of the label at different points of the animation...
		fake_label1 = Label(text = self.text, font_size = 32, font_name = self.font_name, pos = (180,100))
		fake_label1.texture_update()
		fake_label1.size = fake_label1.texture_size
		self.big_size = fake_label1.texture_size[0]

		fake_label2 = Label(text = self.text, font_size = 22, font_name = self.font_name, pos = (180,300))
		fake_label2.texture_update()
		fake_label2.size = fake_label2.texture_size
		self.small_size = fake_label2.texture_size[0]

		#self.pos = (self.big_size/2-180+20, 240-320+10)
		#self.final_pos = (self.small_size/2-180+20, 610-320+10)
		self.pos = (0, 240-320+10-7)
		self.final_pos = (0, 610-320+10-3)
		self.size = fake_label1.size
		self.final_size = fake_label2.size


		self.appear_animation()

	def appear_animation(self):
		self.texture_update()

		appear_duration = 0.3
		lasting_duration = 1.7

		animation = Animation(font_size = 32, duration = appear_duration, t='out_back')
		animation.start(self)
		Clock.schedule_once(self.float_animation, lasting_duration)

	def float_animation(self, time_elapsed):
		self.texture_update()

		float_duration = 15.0
		fade_duration = 3.0
		animation = Animation(pos = self.final_pos, duration = float_duration)
		animation &= Animation(size = self.final_size, duration = float_duration)
		animation &= Animation(font_size = 22, duration = float_duration/3, t = 'out_cubic')
		animation &= Animation(color = self.end_color, duration = fade_duration)
		animation.start(self)
		Clock.schedule_once(self.check_permanence, float_duration)

	def check_permanence(self, time_elapsed):
		self.texture_update()

		if self.relevance == 'primary':
			if self.parent.active_message != None:
				self.parent.remove_widget(self.parent.active_message)
			self.parent.active_message = self
		else:
			try:
				self.parent.remove_widget(self)
			except:
				print "IMPORTANT ERROR: non primary labels can't be removed from parent (is there a parent?)."
				print self
				print self.relevance
				print self.message


class teamButton(Button):
	"""Creates a semi tranparent utton with the team's crest, that will provide data from the team in question. It must either be called with the argument 'friend' or 'foe'."""

	def __init__(self,team_sides,**kwargs):
		super(teamButton,self).__init__(**kwargs)
		self.size_hint = (None,None)
		self.size = (120,120)
		self.image = None
		self.allow_stretch = False
		self.color = (1,1,1,0)
		self.background_normal = './data/images/btn_team_background.png'
		self.background_down = './data/images/btn_team_background_down.png'

		if team_sides == 'friend':
			self.pos = (0,0)
			self.image = Image(source='./data/images/crest_capybara_big.png', size_hint=(None,None), size = (200,200), pos = [self.pos[0]-50,self.pos[1]-50], color = (1,1,1,0.5) )
			self.stencil_box = StencilView(size_hint=(None,None), size = (120,120), pos = self.pos)
		elif team_sides == 'foe':
			self.pos = (240,0)
			self.image = Image(source='./data/images/crest_jaguar_big.png', size_hint=(None,None), size = (200,200), pos = [self.pos[0]-50,self.pos[1]-50], color = (1,1,1,0.5) )
			self.stencil_box = StencilView(size_hint=(None,None), size = (120,120), pos = self.pos)
		self.add_widget(self.stencil_box)
		self.stencil_box.add_widget(self.image)

class mainScreen(Screen):
	def __init__(self,name,**kwargs):
		super(mainScreen,self).__init__(**kwargs)
		self.name = name
		self.active_message = None
		self.zone_str = {'friend': {'atk':0,'mid':0,'def':0}, 'foe':{'atk':0,'mid':0,'def':0}}
		self.interrupt_messages = False

		#widgets in this list will be destroyed and remade every time the screen is called
		self.temporary_widgets = []

		# Creating and adding permanent widgets
		img_soccer_pitch = Image(source='./data/images/background-field.png')
		img_bottom_bar = Image(source='./data/images/interface-lowpanel-plain.png', pos=(0, -260))
		img_mid_bar = Image(source='./data/images/interface-midpanel-logo.png',pos=(0, -147))
		black_bar = Image(source='./data/images/interface-message-bar.png',pos=(0, -77))

		self.team_btn_friend = teamButton('friend')
		self.team_btn_foe = teamButton('foe')

		self.add_widget(img_soccer_pitch)
		self.add_widget(img_bottom_bar)
		self.add_widget(img_mid_bar)
		self.add_widget(black_bar)
		self.add_widget(self.team_btn_friend)
		self.add_widget(self.team_btn_foe)

		with self.canvas: Rectangle(pos=(0, 120), size=(360, 3))
		#with self.canvas: Rectangle(pos=(0, 223), size=(360, 12))
		#white_bar_label = Label(text='THESE ACTIONS ARE CURRENTLY AVAILABLE TO YOU', color = (0.67,0.67,0.67,1), font_size = 10, pos= (-100,-92), font_name = './data/fonts/H.H. Samuel-font-defharo.ttf')
		#self.add_widget(white_bar_label)


	def on_called(self):
		"""Runs when the screen is called for view. It will replace temporary widgets."""

		# First we update some data.
		opponent_data = g.opponents[g.save.match['opponent']]
		self.zone_str['foe']['atk'] = opponent_data['atk']
		self.zone_str['foe']['mid'] = opponent_data['mid']
		self.zone_str['foe']['def'] = opponent_data['def']


		# Now destroy old temporary widgets
		for widget in self.temporary_widgets:
			self.remove_widget(widget)
		self.temporary_widgets = []

		# Create and add temporary widgets

		# Then we update the permanent widgets that needs updating
		#self.team_score.text = str(g.save.match['score'][0])
		#self.opponent_score.text = str(g.save.match['score'][0])
		self.team_btn_friend.image.source = './data/images/crest_'+g.save.status['crest']+'_big.png'
		self.team_btn_foe.image.source =  './data/images/crest_'+g.save.match['opponent']+'_big.png'
	
		#self.stage = 'match_preparation'
		self.msg_count = 0

		g.save.match['action'] = 'strategy'
		self.prepare_layout()
		Clock.schedule_once(self.load_messages)

		#self.deploy_players() #Automatically deploys players according to formation
		#Create card-box to receive player's cards
		#print 'cards in hand',g.save.tournament['selected_cards']
		#card_hand = cardHand(list_of_cards=g.save.tournament['selected_cards'])
		#self.add_widget(card_hand)

	def pop_into_existance(self, widget, make_child = True, add_to_temp_list = True):
		"""This funtions will animate widgets poping into existance, and will also add them to parent self and to the temporary widget list, unless told otherwise."""
		final_size = widget.size[:]
		widget.size = (0,0)
		pop_duration = 1.0
		pop = Animation(size = final_size, duration = pop_duration, t = 'out_back')
		pop.start(widget)

		self.temporary_widgets.append(widget)
		self.add_widget(widget)

	def load_widgets_strategy(self):
		"""This function will load the widgets necessary for the strategy phase, in which the player will select the formation and tactics for the game."""
		font_path = './data/fonts/MANDINGO.TTF'
		black = (0,0,0,1)

		self.card_hand = cardHand(list_of_cards=g.save.tournament['available_cards'])
		zone_marker_friend = Image(source='./data/images/interface-zone-markers-friend.png',pos=(-180+25, -40+180-8))
		circle_button = circleButton()
		#Add interface button (lower black circle). A permanent widget that must stay above all other widgets, except the men.

		self.str_atk_own = Label(text=str(self.zone_str['friend']['atk']),font_size='40sp',font_name=font_path, color=black, pos = (-155,260))
		self.str_mid_own = Label(text=str(self.zone_str['friend']['mid']),font_size='40sp',font_name=font_path, color=black, pos = (-155,135))
		self.str_def_own = Label(text=str(self.zone_str['friend']['def']),font_size='40sp',font_name=font_path, color=black, pos = (-155,9))

		self.temporary_widgets.append(self.card_hand)
		self.temporary_widgets.append(zone_marker_friend)
		self.temporary_widgets.append(circle_button)
		self.temporary_widgets.append(self.str_atk_own)
		self.temporary_widgets.append(self.str_mid_own)
		self.temporary_widgets.append(self.str_def_own)

		self.add_widget(self.card_hand)
		self.add_widget(zone_marker_friend)
		#self.pop_into_existance(circle_button)
		self.add_widget(circle_button)
		self.add_widget(self.str_atk_own)
		self.add_widget(self.str_mid_own)
		self.add_widget(self.str_def_own)

		self.calculate_zone_strength()

	def calculate_zone_strength(self):
		"""This function will recalculate the zone strengths of the player's team, taking into account formation, tactics, skills, counterattacks and rebounds. It will also print the new results on screen."""

		possible_formations = ['sf-343','sf-352','sf-433','sf-442','sf-4231','sf-kami','sf-libero','sf-metodo','sf-pyr','sf-wm']
		possible_tactics = ['t-ball','t-col','t-count','t-direct','t-for','t-indiv','t-long','t-man','t-offside','t-runs','t-set','t-zone']
		possible_men = ['pa-talent','pa-leader','pa-opport','pd-fast','pd-leader','pd-talent','pd-util','pm-fast','pm-leader','pm-opport','pm-talent','pm-util']

		equiped_formation = None
		equiped_tactic = None
		equiped_skills = []
		zone_values = [0,0,0]

		for card in self.card_hand.get_selected():
			if card.name in possible_formations:
				equiped_formation = card.name
			elif card.name in possible_tactics:
				equiped_tactic = card.name
			elif card.name in possible_men:
				equiped_skills.append(card.name)


		#print 'zone values before formation', zone_values
		if equiped_formation == 'sf-pyr':
			zone_values = [10,6,8]
			print 'formation equiped sf-pyr'
		elif equiped_formation == 'sf-4231':
			zone_values = [8,7,9]
			print 'formation equiped sf-4231'
		elif equiped_formation == 'sf-433':
			zone_values = [10,7,7]
			print 'formation equiped sf-433'
		elif equiped_formation == 'sf-libero':
			zone_values = [12,7,5]
			print 'formation equiped sf-libero'
		elif equiped_formation == 'sf-metodo':
			zone_values = [8,8,8]
			print 'formation equiped sf-metodo'
		elif equiped_formation == 'sf-442':
			zone_values = [10,8,6]
			print 'formation equiped sf-442'
		elif equiped_formation == 'sf-343':
			zone_values = [7,8,9]
			print 'formation equiped sf-343'
		elif equiped_formation == 'sf-wm':
			zone_values = [9,9,6]
			print 'formation equiped sf-wm'
		elif equiped_formation == 'sf-352':
			zone_values = [10,9,5]
			print 'formation equiped sf-352'
		elif equiped_formation == 'sf-kami':
			zone_values = [4,10,10]
			print 'formation equiped sf-kami'
		elif equiped_formation == 'sf-424':
			zone_values = [9,4,11]
			print 'formation equiped sf-424'
		elif equiped_formation == 'sf-451':
			zone_values = [9,12,3]
			print 'formation equiped sf-451'

		#print 'zone values between formation and tactics', zone_values

		if equiped_tactic == 't-ball':
			zone_values[1] +=2
			print 'tactic equiped t-ball'
		elif equiped_tactic == 't-count':
			print 'tactic equiped t-count'
			pass
		elif equiped_tactic == 't-long':
			print 'tactic equiped t-blong inactive'
			if g.save.match['action'] == 'counterattack':
				zone_values[2] +=4
				print 'tactic equiped t-blong active'
		elif equiped_tactic == 't-indiv':
			print 'tactic equiped t-indiv inactive'
			if 'pa-talent' in equiped_skills:
				zone_values[2] +=1
				print 'tactic equiped t-indiv active for attack'
			if 'pm-talent' in equiped_skills:
				zone_values[1] +=1
				print 'tactic equiped t-indiv active for midfield'
			if 'pd-talent' in equiped_skills:
				zone_values[0] +=1
				print 'tactic equiped t-indiv active for defense'
		elif equiped_tactic == 't-set':
			zone_values[2] +=2
			print 'tactic equiped t-set'
		elif equiped_tactic == 't-zone':
			zone_values[0] +=2
			print 'tactic equiped t-zone'
		elif equiped_tactic == 't-man':
			print 'tactic equiped t-man inactive'
			#fix later for actual number of players
			if equiped_formation in ['sf-4231', 'sf-433', 'sf-libero', 'sf-442', 'sf-424', 'sf-451']:
				zone_values[0] +=3
				print 'tactic equiped t-man acive'
		elif equiped_tactic == 't-for':
			print 'tactic equiped t-for'
			pass
		elif equiped_tactic == 't-col':
			print 'tactic equiped t-col'
			zone_values[0] +=4
			zone_values[1] -=1
			zone_values[2] -=1
		elif equiped_tactic == 't-runs':
			print 'tactic equiped t-runs'
			zone_values[1] +=1
			zone_values[2] +=1
		elif equiped_tactic == 't-direct':
			print 'tactic equiped t-direct'
			zone_values[0] -=2
			zone_values[1] +=2
			zone_values[2] +=2
		elif equiped_tactic == 't-offside':
			print 'tactic equiped t-offside'
			# fix for die roll
			pass
			
		#print 'zone values between tactic and players',zone_values

		skill_bonus = 0
		skill_bonus = equiped_skills.count('pa-talent')
		zone_values[2]+=skill_bonus
		skill_bonus = equiped_skills.count('pm-talent')
		zone_values[1]+=skill_bonus
		skill_bonus = equiped_skills.count('pd-talent')
		zone_values[0]+=skill_bonus
		skill_bonus = equiped_skills.count('pa-opport')
		skill_bonus += equiped_skills.count('pm-opport')
		if g.save.match['action'] == 'rebound':
			zone_values[0] += skill_bonus
		skill_bonus = equiped_skills.count('pm-fast')
		skill_bonus += equiped_skills.count('pd-fast')
		if g.save.match['action'] == 'counterattack':
			zone_values[2] += skill_bonus
		#print 'zone values after players',zone_values
		

		#print "calculating strength", equiped_formation, equiped_tactic, equiped_skills

		
		self.str_atk_own.text = str(zone_values[2])
		self.str_mid_own.text = str(zone_values[1])
		self.str_def_own.text = str(zone_values[0])

		self.zone_str['friend']['atk']=zone_values[2]
		self.zone_str['friend']['mid']=zone_values[1]
		self.zone_str['friend']['def']=zone_values[0]

			
			


	def load_widgets_preparation(self):
		"""This function will load the widgets necessary for the preparation phase, in which the player will position their players in the field and activate positions."""
		#Now we create the positions markers (jobs) for the players. These are also permanent widgets
		font_path = './data/fonts/MANDINGO.TTF'
		black = (0,0,0,1)

		self.create_position_buttons() #Creates the positions (jobs) for the player pins

		self.team_score = Label( text=str(0), font_size='85sp', font_name='./data/fonts/MANDINGO.TTF', color=(1,1,1,1), pos = (-130,-260) ) #65sp
		self.opponent_score = Label( text=str(0), font_size='85sp', font_name='./data/fonts/MANDINGO.TTF', color=(1,1,1,1), pos = (130,-260) )

		zone_marker_foe = Image(source='./data/images/interface-zone-markers-foe.png',pos=(130+25, -40+180-8))
		self.str_atk_opp = Label(text=str(self.zone_str['foe']['atk']),font_size='40sp',font_name=font_path, color=black, pos = (155,260))
		self.str_mid_opp = Label(text=str(self.zone_str['foe']['mid']),font_size='40sp',font_name=font_path, color=black, pos = (155,135))
		self.str_def_opp = Label(text=str(self.zone_str['foe']['def']),font_size='40sp',font_name=font_path, color=black, pos = (155,9))


		self.temporary_widgets.append(self.team_score)
		self.temporary_widgets.append(self.opponent_score)
		self.temporary_widgets.append(zone_marker_foe)
		self.temporary_widgets.append(self.str_atk_opp)
		self.temporary_widgets.append(self.str_mid_opp)
		self.temporary_widgets.append(self.str_def_opp)

		self.add_widget(self.team_score)
		self.add_widget(self.opponent_score)
		self.add_widget(zone_marker_foe)
		self.add_widget(self.str_atk_opp)
		self.add_widget(self.str_mid_opp)
		self.add_widget(self.str_def_opp)

		self.deploy_players() #Automatically deploys players according to formation


	def prepare_layout(self):
		"""Unlike other screens, the main screen will change some aspects of its layout while it is still visible to the user. These changes occur according to g.save.match['action'], that basically defines what currently happening in the game. The possible answers are: strategy (equiping cards at the beginning of the match), preparation (equiping cards between two plays), defense, midfield, attack, counterattack, counterattack_against, rebound and free kick. Each actions also has a list of messages that are played on its startup. Widget placing is made by called outside functions, so they can be all called in sequence at the start of a loaded game."""
		action = g.save.match['action']

		if action == 'strategy':
			print 'prepare layout ran strategy'
			# Widget creation: creates card hand, zone markers and zone labels.
			# Allowed actions: cards can be equiped. 
			self.messages = [['MATCH PREPARATION','primary'],['CLICK THE BALL','secondary'],['WHEN YOU ARE READY','secondary'],['YOU SHOULD CHOOSE','tutorial'],['WHICH CARDS TO EQUIP','tutorial'],['PICK ONE FORMATION','tutorial'],['ONE TACTIC','tutorial'],['AND AS MANY SKILLS','tutorial'],['AS POSSIBLE','tutorial']]
			#Create card-box to receive player's cards
			self.load_widgets_strategy()

		elif action == 'preparation':
			print 'prepare layout ran preparation'
			# Widget creation: creates player positions and players, who are also placed in provisional positions.
			# Allowed actions: tactics and skill cards can be equiped, and players may be relocated.
			self.messages = [ ['PLAY X- PREPARATION','primary'],['CHOOSE POSITIONS','secondary'],['CLICK THE BALL','secondary'],['WHEN YOU ARE READY','secondary'],['YOU CAN REARRANGE THE MEN','tutorial'],['BY DRAGGING THEM','tutorial'],['TO NEW POSITIONS','tutorial'] ]
			self.load_widgets_preparation()
			#self.card_hand.get_available
			for card in self.card_hand.get_cards_by_type(card_state = 'all', card_type = 'formation'):
				card.switch_mode('blocked')

		elif action == 'defense':
			# Widget creation: none.
			# Allowed actions: positions may be activated.
			self.messages = [ ['PLAY X- DEFENSE','primary'],['YOU MAY TRY TO ACTIVATE POSITIONS','secondary'],['BY DRAGGING THE MEN','secondary'],['INTO THEIR OWN POSITIONS','secondary'], ['YOU ARE NOW UNDER ATTACK', 'tutorial'],  ['YOUR OPPONENT WILL SCORE UNLESS', 'tutorial'], ['YOU BEAT HIM IN A DEFENSE CHECK', 'tutorial'], ['AGAINST HIS ATTACK', 'tutorial'], ['TO HELP YOU OUT, YOU COULD', 'tutorial'], ['ACTIVATE DEFENSIVE POSITIONS', 'tutorial'], ['ESPECIALLY THE CENTER-BACKS (CB)', 'tutorial']]
	
		elif action == 'midfield':
			# Widget creation: none.
			# Allowed actions: positions may be activated.
			self.messages = [ ['PLAY X- MIDFIELD','primary'],['YOU MAY TRY TO ACTIVATE POSITIONS','secondary'],['BY DRAGGING THE MEN','secondary'],['INTO THEIR OWN POSITIONS','secondary'], ['ONCE PER PLAY YOU MUST TEST', 'tutorial'],  ['YOUR MIDFIELD ZONE', 'tutorial'], ['IF YOU WIN YOU MUST ATTACK', 'tutorial'], ['IF YOU LOSE YOU MUST DEFEND', 'tutorial'], ['BUT YOU CAN IMPROVE', 'tutorial'], ['YOUR CHANCES BY ACTIVATING', 'tutorial'], ['MIDFIELD POSITIONS, SUCH AS', 'tutorial'], ['CENTER-MIDFIELDERS (CM)', 'tutorial']]

		elif action == 'attack':
			# Widget creation: none.
			# Allowed actions: positions may be activated.
			self.messages = [ ['PLAY X- ATTACK','primary'],['YOU MAY TRY TO ACTIVATE POSITIONS','secondary'],['BY DRAGGING THE MEN','secondary'],['INTO THEIR OWN POSITIONS','secondary'],['GREAT! NOW YOU GET TO ATTACK','secondary'], ['YOU WILL MAKE AN ATTACK CHECK', 'tutorial'],  ["AGAINST YOUR OPPONENT'S DEFENSE", 'tutorial'], ['IF YOU WIN, YOU SCORE A GOAL', 'tutorial'] ]




	def load_messages(self, time_elapsed = 0):
		"""This function will sort out which messages are relevant and call them through recursive calling."""

		if self.interrupt_messages == True:
			#This allows us to shut the messages when needed.
			self.messages = []
			self.interrupt_messages = False

		if len(self.messages) >0:
			#We can only load messages if there are messages to load.

			message = self.messages[0]
			if message[1] == 'tutorial' and g.save.tournament['id'] != '3rd-div':
				# Message irrelevant. Ignore it and load the next one.
				self.messages.remove(message)
				self.load_messages()
			else:
				#Message relevant. Print it on screen and load the next one in 2 seconds.
				self.messages.remove(message)
				message_label = labelMessage(message = message[0], relevance = message[1])
				self.add_widget(message_label)
				Clock.schedule_once(self.load_messages,2)

#		relevant_messages = []
#		for message in self.messages[self.stage]:
#			if message[1] == 'tutorial' and g.save.tournament['id'] != '3rd-div':
#				pass
#			else:
#				relevant_messages.append(message)
#
#		if self.msg_count < len(relevant_messages):
#			message = labelMessage(message = relevant_messages[self.msg_count][0], relevance = relevant_messages[self.msg_count][1])
#			self.add_widget(message)
#			self.msg_count += 1
#			Clock.schedule_once(self.load_messages,2)
#		else:
#			print 'end of messages' #from here


		

	def create_zone_markers(self):
		self.add_widget(zoneMarker(zone = 'attack', position = (0,475)))
		self.add_widget(zoneMarker(zone = 'midfield',source='./data/images/zone-midfield-left-normal.png', position = (0,355)))
		self.add_widget(zoneMarker(zone = 'defense',source='./data/images/zone-defense-left-normal.png', position = (0,235)))


	def create_position_buttons(self):
		"""Creates the player positions, called 'jobs'. It creates both the background images for them and the job obscts, which holds the data but have no visual rendering."""

		#The background images representing the positions (jobs) and independent from the job objects, which
		#have no graphic representation. This functions creates both.
		attackers_list = [ ['st',(-22,250)], ['st',(22,250)], ['lw',(-86,230)], ['fw',(-42,208)], ['fw',(0,208)], ['fw',(42,208)], ['rw',(86,230)] ]
		midfielders_list = [ ['am',(0,140)], ['lf',(-108,119)], ['cm',(-66,100)], ['cm',(-22,100)], ['cm',(22,100)], ['cm',(66,100)], ['rf',(108,119)], ['hm',(-22,57)], ['hm',(22,57)] ]
		defenders_list = [ ['lb',(-108,5)], ['cb',(-66,-18)], ['cb',(-22,-18)], ['cb',(22,-18)], ['cb',(66,-18)], ['rb',(108,5)], ['sw',(0,-60)] ]
		
		atk_pos_mod = (0,8)
		mid_pos_mod = (0,18)
		def_pos_mod = (0,28)

		for job in attackers_list:
			job_pos = (job[1][0]+atk_pos_mod[0], job[1][1]+atk_pos_mod[1])
			self.add_widget(Image(source='./data/images/position-'+job[0]+'.png', pos = job_pos ))			
			g.job_list.append(Job(position = job_pos, code = job[0]))

		for job in midfielders_list:
			job_pos = (job[1][0]+mid_pos_mod[0], job[1][1]+mid_pos_mod[1])
			self.add_widget(Image(source='./data/images/position-'+job[0]+'.png', pos = job_pos ))			
			g.job_list.append(Job(position = job_pos, code = job[0]))

		for job in defenders_list:
			job_pos = (job[1][0]+def_pos_mod[0], job[1][1]+def_pos_mod[1])
			self.add_widget(Image(source='./data/images/position-'+job[0]+'.png', pos = job_pos ))			
			g.job_list.append(Job(position = job_pos, code = job[0]))


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

	def on_card_clicked(self, card_id, card_object, card_state):
		"""This function determines what happens whe a card is clicked in the main screen. There are a couple of options. If it is not the strategy stage, formations cannot be equiped. If it is the preparation stage, the formation can be unequiped, tactics can be changed, and so can players. During other stages, cards can't be changed at all.
		Also, at any give, time, only one formation and one tactic can be equipped. Selecting another will automatically deselect the previous."""

		# First possiblity: the card is blocked. Then we reverse selection
		if card_object.mode == 'blocked':
			if card_object.state == 'normal': card_object.state = 'down'
			elif card_object.state == 'down': card_object.state = 'normal'

		# Second possibility: the card is not blocked. Then we must decide what to do with it.
		else:

			clicked_card_type = card_object.get_type()
			recalculate_zones = True
	
			# In the Strategy Stage, all cards are clickable, but only 
			# one formation and one tactic can be active at any point.
	
	
			# First, let's deal with what happened when a card was seleted.
	
			if card_state == 'normal': #The card has just been selected, rather than diselected.
				if clicked_card_type == 'formation':
					#If the card was a formation, we first have to prevent the player from having two formations equiped.
					selected_formations = self.card_hand.get_cards_by_type(card_state = 'selected', card_type = 'formation')
					if len(selected_formations)>1:
						# Multiple formations selected. The old one must be unselected
						# so the new one becomes the only.
						for card in selected_formations:
							if card != card_object:
								card.state = 'down'
						self.reevaluate_skills()
								#recalculate_zones = False
	
				elif clicked_card_type == 'tactic':
					selected_tactics = self.card_hand.get_cards_by_type(card_state = 'selected', card_type = 'tactic')
					print 'selected tactics',selected_tactics
					if len(selected_tactics)>1:
						# Multiple formations selected. The old one must be unselected
						# so the new one becomes the only.
						for card in selected_tactics:
							if card != card_object:
								card.state = 'down'
						self.reevaluate_skills()
	
			# Also, one can only have as many skills equiped in a zone as the number of players alotted to tha zone
			# by his formation.
				if clicked_card_type in ['attacker','defender','midfielder']:
					list_of_formations = self.card_hand.get_cards_by_type(card_state = 'selected', card_type = 'formation')
					if list_of_formations == []:
						#There are no equiped formation and, thus, the player cannot equip skills
						card_object.state = 'down'
						recalculate_zones = False
						print "In the strategy stage, you may not equip skills without a formation. Wait for a preparation phase."
	
					else:
						# There is an equiped formation and, thus, he can equip some skills
						formation = list_of_formations[0]
						skill_limit = None
					
		
						zone_index = 0 # defender
						if clicked_card_type == 'midfielder': zone_index =1
						elif clicked_card_type == 'attaker': zone_index = 2
	
						skill_limit = g.formations[formation.name]['men'][zone_index]
	
						if len(self.card_hand.get_cards_by_type(card_state = 'selected', card_type = clicked_card_type)) > skill_limit:
							card_object.state = 'down'
							print "You have exceeded the limit of skills in this zone."
							recalculate_zones = False
	
	
					
			# Now let's deal with what happens when a card is diselected.
	
			elif card_state == 'down': #The card has just been selected, rather than diselected.
	
				if clicked_card_type == 'formation':
					# If a formation is removed, all equiped skills are unequiped, since one cannot have
					# skills without a formation in the strategy stage.
					equiped_skills = self.card_hand.get_cards_by_type(card_state = 'selected', card_type = 'skill')
					print 'equiped skill list', equiped_skills
					for card in equiped_skills:
						card.state = 'down'
	
	
			if recalculate_zones:
				self.calculate_zone_strength()


	def reevaluate_skills(self):
		"""This function will check how many skills may de alotted to each zone, according to the selected formation or lack of it."""
		formation = self.card_hand.get_cards_by_type(card_state = 'selected', card_type = 'formation')[0]
		def_limit = g.formations[formation.name]['men'][0]
		mid_limit = g.formations[formation.name]['men'][1]
		atk_limit = g.formations[formation.name]['men'][2]

		def_list = self.card_hand.get_cards_by_type(card_state = 'selected', card_type = 'defender')
		mid_list = self.card_hand.get_cards_by_type(card_state = 'selected', card_type = 'midfielder')
		atk_list = self.card_hand.get_cards_by_type(card_state = 'selected', card_type = 'attacker')

		def_remove = -( def_limit - len(def_list) )
		mid_remove = -( mid_limit - len(mid_list) )
		atk_remove = -( atk_limit - len(atk_list) )

		for card in def_list:
			if def_remove >0:
				card.state = 'down'
				def_remove -= 1

		for card in mid_list:
			if mid_remove >0:
				card.state = 'down'
				mid_remove -= 1

		for card in atk_list:
			if atk_remove >0:
				card.state = 'down'
				atk_remove -= 1

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

		if g.debug_player == 'pro':
			#Load fake save
			print 'LOAD PRO PLAYER'
			g.save = gameSave(status = {'name': 'debug team', 'crest': 'jaguar', 'fans': 536628, 'level': 6,'available_crests':['btfg', 'snts', 'rlmd', 'bmnc', 'sloth', 'tapir', 'paca', 'turtle', 'opossum', 'toucan', 'dolphin', 'wolf', 'jaguar', 'penguin'],'laurels':{'win':37,'tie':12,'lose':6,'3rd':12,'2nd':8,'1st':6,'premiere':4,'world':2}, 'milestones':{'profile': True, 'tutorial': True, '3rd': True, '2nd': True, '1st': True, 'premiere': True}, 'details': False}, tournament = {'id': 'premiere', 'tries': 4, 'hand_size': 12, 'available_cards': ['pa-fast','pd-fast','sf-352','sf-kami','t-ball','t-runs','sf-wm','pm-opport','pm-opport','pm-opport','pm-opport','pm-opport','pm-opport','pm-opport','pm-opport','pm-leader'], 'selected_cards': [], 'teams': [{'name':'penguin','result':'win'},{'name':'jaguar','result':'lose'},{'name':'condor','result':'win'},{'name':'sloth','result':''}] }, match = {'opponent': '', 'play':0, 'action': 'strategy', 'score': [0,0], 'players': [{'position':'','status':'healthy'}, {'position':'','status':'healthy'}, {'position':'','status':'healthy'}, {'position':'','status':'healthy'}, {'position':'','status':'healthy'}, {'position':'','status':'healthy'}, {'position':'','status':'healthy'}, {'position':'','status':'healthy'}, {'position':'','status':'healthy'}, {'position':'','status':'healthy'}] })
			print 'LOAD PRO PLAYER', g.save.status['name']

		elif g.debug_player == 'newbie':
			g.save = gameSave(status = {'name': '', 'crest': '', 'fans': 0, 'level': 1,'available_crests':['snts', 'rlmd', 'bmnc'],'laurels':{'win':0,'tie':0,'lose':0,'3rd':0,'2nd':0,'1st':0,'premiere':0,'world':0}, 'milestones':{'profile': False, 'tutorial': False, '3rd': False, '2nd': False, '1st': False, 'premiere': False}, 'details': True}, tournament = {'id': '', 'tries': 2, 'hand_size': 3, 'available_cards': [], 'selected_cards': [], 'teams': [{'name':'','result':''},{'name':'','result':''},{'name':'','result':''},{'name':'','result':''}] }, match = {'opponent': '', 'play':0, 'action': 'strategy', 'score': [0,0], 'players': [{'position':'','status':'healthy'}, {'position':'','status':'healthy'}, {'position':'','status':'healthy'}, {'position':'','status':'healthy'}, {'position':'','status':'healthy'}, {'position':'','status':'healthy'}, {'position':'','status':'healthy'}, {'position':'','status':'healthy'}, {'position':'','status':'healthy'}, {'position':'','status':'healthy'}] })
			print 'LOAD NEWBIE PLAYER', g.save.status['name']
		else:
			#Try to read save file. If it fails, then create a new save file.
			try:
				load_from_save()
				g.save.status['name']
				print 'LOAD OLD PLAYER'
				print '---> save file found\n loading file'
			except:
				g.save = gameSave()
				write_to_save()
				g.save.status['name']
				print 'CREATE NEW PLAYER'
				print '---> cant find save file\n create new save'

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
		g.screens['transition'] = transitionScreen(name = 'transition_screen')

		g.manager.add_widget(g.screens['splash'])
		g.manager.add_widget(g.screens['title'])
		g.manager.add_widget(g.screens['main'])
		g.manager.add_widget(g.screens['profile'])
		g.manager.add_widget(g.screens['tournament'])
		g.manager.add_widget(g.screens['tutorial'])
		g.manager.add_widget(g.screens['transition'])




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

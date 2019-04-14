import kivy
kivy.require('1.8.0')

from kivy.uix.screenmanager import *
from kivy.uix.modalview import ModalView
from kivy.uix.relativelayout import RelativeLayout
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.animation import *

import random
from random import shuffle

import g

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
	



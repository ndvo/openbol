import kivy
kivy.require('1.8.0')

from kivy.uix.modalview import ModalView
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.button import Button
from kivy.animation import *
from kivy.uix.scrollview import ScrollView
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.boxlayout import BoxLayout

import cPickle as Pickle

import g

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



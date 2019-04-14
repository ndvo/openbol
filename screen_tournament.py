import kivy
kivy.require('1.8.0')

from kivy.uix.screenmanager import *
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.label import Label

import g
from basic_widgets import *



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

			g.save.match['play'] = 1
			g.save.match['action'] = 'strategy'
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



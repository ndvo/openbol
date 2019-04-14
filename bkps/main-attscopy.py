import kivy
kivy.require('1.8.0')
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.label import Label
from kivy.config import Config
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.modalview import ModalView
from kivy.uix.actionbar import ActionBar
from kivy.uix.carousel import Carousel
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.metrics import *
from kivy.uix.progressbar import ProgressBar
from kivy.animation import Animation
from kivy.animation import AnimationTransition


#from kivy.core.image import *#mage
from kivy.graphics import *#Rectangle
from kivy.core.window import Window

import g
import random
import os
import urllib
import urllib2
from kivy.network.urlrequest import UrlRequest
import socket
import cPickle as pickle
import datetime


def popup_dismiss(args = None):
	"""Simple function to kill popup panels. Only 1 popup is ever registered in g at any one time."""
	print 'active popup',g.active_popup
	g.active_popup.dismiss()
	g.active_popup = None
	g.pairing = []
	g.player_buttons = []
	g.reevaluate_players()

def get_random_image(att_icon = True, oca_icon = True, army_icons = True, troop_images = True, extra_troops = True):
	possibilities = []
	if att_icon == True: possibilities.append('images/logo.png')
	if oca_icon == True: possibilities.append('oca_logo.png')

	if army_icons == True:
		for army in ['alien', 'arcane', 'bandit', 'east', 'fae', 'goblin', 'levant', 'north', 'robot', 'south', 'undead', 'west']:
			possibilities.append('images/icon_'+army+'.png')

	if troop_images == True:
		for troop in os.listdir('images/troops'):
			possibilities.append('images/troops/'+troop)

	if extra_troops == True:
		for troop in os.listdir('images/troops_extra'):
			possibilities.append('images/troops_extra/'+troop)

	return random.choice(possibilities)


class myToggleButton(ToggleButton):
	"""This class acts as a holder so their appearance can be defined in mytest.kv."""
	pass

class armyToggle(ToggleButton):
	"""This class acts as a holder so their appearance can be defined in mytest.kv."""

	def __init__(self, **kwargs):
		super(armyToggle, self).__init__(**kwargs)
		self.current_color = 'normal'
		self.normal_color = (1,1,1,0.8)
		self.pressed_color = (1,1,1,0.2)
		self.background_color = self.normal_color

	def on_press(self):
		if self.current_color == 'normal':
			self.background_color = self.pressed_color
			self.current_color = 'pressed'
		elif self.current_color == 'pressed':
			self.background_color = self.normal_color
			self.current_color = 'normal'

class myButton(Button):
	"""This class acts as a holder so their appearance can be defined in mytest.kv."""
	pass


class Combination():
	"""This class holds a series of pairs of players, which indicate the following round of battles. It also carries a 'bad' property, which indicates how good a combination it is."""
	def __init__(self, bad = 0, pairs = []):
		self.bad = bad
		self.pairs = pairs






class confirm_Me(Popup):
	"""An all-around confirmation panel."""
	
	def __init__(self, title = 'Are you sure?', text = 'Please cofirm', btn_text = 'OK', command='none',**kwargs):
		super(confirm_Me, self).__init__(**kwargs)
		self.title = title
		self.ids.panel_text.text = text
		self.ids.panel_button.text = btn_text
		#self.parent = parent
		self.command = command
		self.ids.panel_button.bind(on_press=self.execute_btn)

	
	def execute_btn(self,value):
		self.dismiss()
		if self.command != 'none':
			self.command()







class battleScreenToggle(ToggleButton):
	def __init__(self, **kwargs):
		super(battleScreenToggle, self).__init__(**kwargs)

	def on_state(self,first,second):
		if self.player.name == 'Bye':
			self.state.set('normal')
			self.toggled = False





class Battle_Panel(Popup):
	"""Probably the most important window, it shows the players paired as a series of grouped toggle buttons. The user should press the winner's toggle button and once all games are finished, confirm the end of the round."""
	def __init__(self, **kwargs):
		super(Battle_Panel, self).__init__(**kwargs)
		self.button_height = 0
		#g.pairing = self.pairing()
		self.btn_height = sp(120)
		content_list = self.create_battle_btns()
		#content_list.append(Widget(size_hint=(1,None),height=20))

		self.title = "Round "+str(g.current_round+1)


		for item in content_list:
			self.ids.battle_box.add_widget(item,len(self.ids))
			self.ids.outter_box.height+=self.button_height

		self.ids.battle_box.add_widget(Widget(size_hint=(1,None),height=sp(10)))
		self.ids.outter_box.height+=sp(90)

		g.active_popup = self


#	def pairing(self):
#		"""This is an important function! It will find the most suitable pairing for a round of games. It does so by analysing a number of possible combinations (the exact number is defined by g.pairing_iterations, but it should be kept between 100 and 1000). The difference in victories for each pair is added as a 'bad', and 5 more 'bads' are added for each time the pair has met before. The combination with the least amount of bads is picked (0 bads being a perfect pairing). This will return a combination object."""
#		combinations = []
#		count = g.pairing_iterations
#		
#		if len(g.selected_players)%2!=0: #When there's an odd number of players
#			g.selected_players.append(g.bye_player)	#Add bye to the list
#			g.bye_player.victories = g.current_round+1 #And make it so the leading players get a better chance of a bye
#
#		while count>0:
#			temp_list = g.selected_players[:]#g.player_list[:]
#			this_combination = Combination(0,[])
#			while len(temp_list)>0:
#				player1 = random.choice(temp_list)
#				temp_list.remove(player1)
#				player2 = random.choice(temp_list)
#				temp_list.remove(player2)
#				this_combination.pairs.append((player1,player2))
#			bad = 0 #Bad measures the quality of a round of battles
#			bad_rank =0 #Bad rank is the penalty for pairing players of different skill levels
#			bad_repetition=0 #Bad repetitions is the penalty for repeating duels
#			for paired in this_combination.pairs:
#				bad_rank = paired[0].victories-paired[1].victories
#				if bad_rank < 0: bad_rank = -bad_rank
#				if paired[0] in paired[1].history: bad_repetition += 5
#				bad = bad+bad_rank+bad_repetition
#			this_combination.bad+=bad
#		
#			combinations.append(this_combination)
#			count-=1
#			if this_combination.bad == 0:
#				combinations = [this_combination]
#				break
#		
#		chosen_combination = None
#		least_bad = combinations[0].bad+1
#		for item in combinations:
#			if item.bad<least_bad:
#				chosen_combination = item
#				least_bad = item.bad
#	
#		return chosen_combination


	def create_battle_btns(self):
		"""Generates the player buttons in the battle window. They are returned as a list of widgets, which are horizontal boxes with buttons."""
		group_count = 0
		battle_pairs =[]
		#button_height = sp(200)
		for pair in g.pairing.pairs:
			innerBox = BoxLayout(orientation='horizontal',padding=4,size_hint = (1,None))

			first_toggle = None
			if pair[0].name == 'Bye':
				first_toggle = Widget()
				first_toggle.state = 'normal'
				first_toggle.color = (1,1,1,0.5)
			else:
				first_toggle = battleScreenToggle(group="group"+str(group_count))
			first_toggle.background_color = (1,1,1,0.8)
			first_toggle.background_color_down = (1,1,1,0.2)
			first_toggle.color = (1,1,1,1)
			first_toggle.halign = 'center'
			first_toggle.player = pair[0]
			first_toggle.size_hint = (1,None)
			first_toggle.height = self.btn_height #first_toggle.width
			self.button_height = self.btn_height #first_toggle.width
			first_icon = Image(source=self.get_icon_path(pair[0]), pos=first_toggle.pos, size=(first_toggle.size[0],self.btn_height), color = [1,1,1,1])
			first_name = Label(text=pair[0].name, color = (1,1,1,1), font_size = sp(20))
			text_label_wins = str(pair[0].victories)
			for enemy in pair[0].history:
				if enemy.name == 'Bye':
					text_label_wins +="*"
			first_wins = None
			if pair[0].name == 'Bye':
				first_wins = Label(text="", color = (1,1,1,1), font_size = sp(14))
			else:
				first_wins = Label(text=text_label_wins+" wins", color = (1,1,1,1), font_size = sp(14))
			first_name.pos = (first_name.pos[0],first_name.pos[1])
			first_wins.pos = (first_wins.pos[0],first_wins.pos[1]-sp(20))

			first_layout = RelativeLayout(size_hint = first_toggle.size_hint, size = (first_toggle.size[0],self.btn_height))
			first_layout.add_widget(first_icon)
			first_layout.add_widget(first_toggle)
			first_layout.add_widget(first_name)
			first_layout.add_widget(first_wins)

			innerBox.add_widget(first_layout)
			g.player_buttons.append(first_toggle)


			second_toggle = None
			if pair[1].name == 'Bye':
				second_toggle = Widget()
				second_toggle.state = 'normal'
				second_toggle.color = (1,1,1,0.5)
			else:
				second_toggle = battleScreenToggle(group="group"+str(group_count))
			second_toggle.background_color = (1,1,1,0.8)
			second_toggle.background_color_down = (1,1,1,0.2)
			second_toggle.color = (1,1,1,1)
			second_toggle.halign = 'center'
			second_toggle.player = pair[1]
			second_toggle.size_hint = (1,None)
			second_toggle.height = self.btn_height#first_toggle.width
			second_icon = Image(source=self.get_icon_path(pair[1]), pos=second_toggle.pos, size=(second_toggle.size[0],self.btn_height), color = [1,1,1,1])
			second_name = Label(text=pair[1].name, color = (1,1,1,1), font_size = sp(20))
			text_label_wins = str(pair[1].victories)
			for enemy in pair[1].history:
				if enemy.name == 'Bye':
					text_label_wins +="*"
			if pair[1].name == 'Bye': text_label_wins = ""
			second_wins = None
			if pair[1].name == 'Bye':
				second_wins = Label(text="", color = (1,1,1,1), font_size = sp(14))
			else:
				second_wins = Label(text=text_label_wins+" wins", color = (1,1,1,1), font_size = sp(14))
			second_name.pos = (second_name.pos[0],second_name.pos[1])
			second_wins.pos = (second_wins.pos[0],second_wins.pos[1]-sp(20))

			second_layout = RelativeLayout(size_hint = second_toggle.size_hint, size = (second_toggle.size[0], self.btn_height))
			second_layout.add_widget(second_icon)
			second_layout.add_widget(second_toggle)
			second_layout.add_widget(second_name)
			second_layout.add_widget(second_wins)

			innerBox.add_widget(second_layout)
			g.player_buttons.append(second_toggle)

			battle_pairs.append(innerBox)
			group_count += 1

			innerBox.size_hint = (1,None)
			innerBox.height = self.btn_height
	
			#innerBox.height = first_player.height

			#innerBox.height = first_toggle.height#width

		return battle_pairs

	def get_icon_path(self,player):
		if player.army == 'West': return './images/icon_west.png'
		elif player.army == 'Undead': return './images/icon_undead.png'
		elif player.army == 'Fae': return './images/icon_fae.png'
		elif player.army == 'Alien': return './images/icon_alien.png'
		elif player.army == 'East': return './images/icon_east.png'
		elif player.army == 'Robot': return './images/icon_robot.png'
		elif player.army == 'Bandit': return './images/icon_bandit.png'
		elif player.army == 'South': return './images/icon_south.png'
		elif player.army == 'North': return './images/icon_north.png'
		elif player.army == 'Goblin': return './images/icon_goblin.png'
		elif player.army == 'Levant': return './images/icon_levant.png'
		elif player.army == 'Arcane': return './images/icon_arcane.png'
		else: return './images/logo.png'

		

	def complete_round(self):
		confirmation = confirm_Me(title = 'Confirm Results', text = 'Are you sure?', btn_text = 'Yes', command=self.complete_round_confirmed)
		confirmation.open()


	def complete_round_confirmed(self):
		"""After the round of battles is over, it is necessary to update data held in g. First we update the round number, then each player's history and finally their victories."""
		#First, the round number.
		g.current_round+=1
	
		#Then, players' histories.
		for pair in g.pairing.pairs:
			pair[0].history.append(pair[1])
			pair[1].history.append(pair[0])

		#And finally, players' victories.
		for player_btn in g.player_buttons:
			if player_btn.state == 'down':
				player_btn.player.victories+=1
		popup_dismiss()


	def popup_dismiss(self):
		confirmation = confirm_Me(title = 'Cancel', text = 'Are you sure you want to cancel this round?', btn_text = 'Cancel it', command=self.popup_dismiss_confirmed)
		confirmation.open()

	def popup_dismiss_confirmed(self):
		print 'dismiss called'
		popup_dismiss()









class confirm_pairing_panel(Popup):
	"""When the generate round button is clicked, it will open a pop-up window asking for confirmation. But only if there's more than 2 players selected."""
	def __init__(self,**kwargs):
		super(confirm_pairing_panel, self).__init__(**kwargs) #Without this, kv ids aren't accessible
		if len(g.selected_players)<2:
			self.title = "Oops"
			self.ids.pairing_message.text = "Not enough players."
			self.ids.confirm_button.text = "Okay"
			self.ids.confirm_button.bind(on_press=popup_dismiss)
		else:
			self.title = "New Round of Duels"
			self.ids.pairing_message.text = "Are you sure\nyou want to generate\na new round of duels?"
			self.ids.confirm_button.text = "Start Pairing"
			self.ids.confirm_button.bind(on_press=self.initiate_battle)
		g.active_popup = self

	def initiate_battle(self,value=None):
		"""This will dismiss the confirmation panel and create a new panel, called a battle panel."""
		popup_dismiss()
		#battle_panel = Battle_Panel()
		#battle_panel.open()

		pairing_screen = Pairing_Screen()
		pairing_screen.open()











class player_panel(Popup):
	"""This is the popup window that allow for the creation of a new player."""
	def __init__(self,parent,**kwargs): #
		super(player_panel, self).__init__(**kwargs)
		self.main_window = parent

		g.active_popup = self



	def btn_add_player(self):#,value):
		"""When a player is added, the software checks if there's a name (no prob having no region or army). Also, the software checks if there isn't already a player with the same name. If it is clear, an intance of the Player class is created and added to g.player_list and to the player grid."""
		player_names = []
		army_name = 'empty'
		player_region = 'empty'
		creation = True
		army_list = [self.ids.btn_wes, self.ids.btn_und, self.ids.btn_fae, self.ids.btn_ali, self.ids.btn_eas, self.ids.btn_rob, self.ids.btn_ban, self.ids.btn_sou, self.ids.btn_nor]
		for player in g.player_list:
			player_names.append(player.name)
		if len(self.ids.player_name.text) == 0:
			creation = False
		elif self.ids.player_name.text in player_names:
			creation = False
		elif self.ids.player_name.text == 'Bye':
			creation = False
		for army_btn in army_list:
			if army_btn.state =='down':
				army_name = army_btn.text
		if creation:
			player = g.Player (name=self.ids.player_name.text, army=army_name, region=self.ids.region_name.text)
			g.player_list.append(player)

			#self.main_window.reload_player_grid()
			popup_dismiss()








		
class layout_main(BoxLayout):
	"""This is the layout of the main screen. It holds the action buttons (which add and remove players and generate round), as well as the main player buttons."""
	def __init__(self,**kwargs):
		super(layout_main,self).__init__(**kwargs)


		self.list_of_player_btn = []
		g.reevaluate_players = self.reload_player_grid #Sets reload_player_grid as global.
		g.main_window = self

		with self.canvas.before: #Draw top bar.			
			Color(1,1,1,.2)
			#self.rect = Rectangle(size= (Window.width, self.ids.add_player_btn.width/3+6), pos= (0, Window.height-self.ids.add_player_btn.width/3-6))
			self.rect = Rectangle(size= (Window.width, sp(40)), pos= (0, Window.height-sp(40)))


		#self.first_screen = First_Screen()
		#Clock.schedule_once(self.first_screen.open)

		splash_screen = Splash_Screen(parent = self)
		Clock.schedule_once(splash_screen.open)




	def test_size_of_buttons(self):
		self.ids.btn_options.size_hint = (None,None)
		self.ids.btn_options.size = (80,80)


	def reload_player_grid(self,new_data='none'):
		"""This method strips all player buttons in the playergrid and recreate players based on the player list, but ordering them according to victories. It is called either when adding and when subtracting players."""
		if new_data != 'none':
		#This will reload saved data, if needed.
			g.player_list = new_data[0]
			g.current_round = new_data[1]
			g.bye_player = new_data[2]
			g.tournament_name = new_data[3]

		self.ids.main_player_grid.clear_widgets()	#Remove all buttons from grid

		#This will create a player list, inversely ordered by victories.
		sorted_list = sorted(g.player_list, key=lambda player: player.victories)[::-1]

		self.list_of_player_btn = []
		for player in sorted_list:
			btn_text = player.name+"\n"+str(player.victories)+"/"+str(len(player.history))+" wins"

			btn = armyToggle()#text=btn_text)#myToggleButton(text=btn_text)
			btn.background_color = (1,1,1,0.8)
			btn.background_color_down = (1,1,1,0.2)
			btn.color = (1,1,1,1)
			btn.halign = 'center'


			btn.player_ref = player
			btn.size_hint = (None,None)
			btn.size=(self.ids.add_player_btn.width,self.ids.add_player_btn.width) #So that the icons are squares, we take the automatically generated width and apply to width/height


			army_source = 'empty'
			if player.army == 'empty': army_source = './images/logo.png'
			if player.army == 'West': army_source = './images/icon_west.png'
			if player.army == 'Undead': army_source = './images/icon_undead.png'
			if player.army == 'Fae': army_source = './images/icon_fae.png'
			if player.army == 'Alien': army_source = './images/icon_alien.png'
			if player.army == 'East': army_source = './images/icon_east.png'
			if player.army == 'Robot': army_source = './images/icon_robot.png'
			if player.army == 'Bandit': army_source = './images/icon_bandit.png'
			if player.army == 'South': army_source = './images/icon_south.png'
			if player.army == 'North': army_source = './images/icon_north.png'
			if player.army == 'Goblin': army_source = './images/icon_goblin.png'
			if player.army == 'Levant': army_source = './images/icon_levant.png'
			if player.army == 'Arcane': army_source = './images/icon_arcane.png'

			icon_image = Image(source=army_source, pos=btn.pos, size=btn.size, color = [1,1,1,1])
			label_name = Label(text=player.name, color = (1,1,1,1), font_size = sp(20))
			text_label_wins = str(player.victories)
			for enemy in player.history:
				if enemy.name == 'Bye':
					text_label_wins +="*"
			label_wins = Label(text=text_label_wins+" wins", color = (1,1,1,1), font_size = sp(14))
			label_name.pos = (label_name.pos[0],label_name.pos[1])
			label_wins.pos = (label_wins.pos[0],label_wins.pos[1]-sp(20))

			btn_layout = RelativeLayout(size_hint = btn.size_hint,size = btn.size)
			btn_layout.add_widget(icon_image)
			btn_layout.add_widget(btn)

			btn_layout.add_widget(label_name)
			btn_layout.add_widget(label_wins)

			self.ids.main_player_grid.add_widget(btn_layout)
			self.list_of_player_btn.append(btn)



		if g.current_round == 0:
			self.ids.round_text.text = "initial setup"
		else:
			self.ids.round_text.text = "round "+str(g.current_round)+" results"

		g.write_log()


	def btn_remove_player(self,value=None):
		self.players_to_remove =[]
		for player_btn in self.list_of_player_btn:
			if player_btn.state == 'down':
				self.players_to_remove.append(player_btn.player_ref)
		confirm_text = "Are you sure you want to remove the following players?\n\n"
		for player in self.players_to_remove:
			confirm_text += player.name+'\n'
		confirmation = confirm_Me(title = 'Remove Players?', text = confirm_text, btn_text = 'Off with their heads!', command=self.btn_remove_player_confirmed)
		confirmation.open()

	def btn_remove_player_confirmed(self):
		"""When the remove button is pressed, all selected players are removed. This is done by deleting them from g.players-list and then running reload_player_grid."""
		for player in self.players_to_remove:
			g.player_list.remove(player)
		self.players_to_remove =[]
		self.reload_player_grid()
		


	def open_player_panel(self,value=None):
		"""The player panel is a popup window that asks for a new player's name, region and army, and lets you add him to the player list."""
		self.player_panel = player_panel(self)
		self.player_panel.open()


	def btn_generate_round(self,value=None):
		"""When the generate round button is clicked, it will open a pop-up window asking for confirmation. But only if there's more than 2 players selected."""
		selected_players = []
		for player_btn in self.list_of_player_btn:
			if player_btn.state=='down':
				selected_players.append(player_btn.player_ref)
		g.selected_players = selected_players
		self.confirm_battle_panel = confirm_pairing_panel()
		self.confirm_battle_panel.open()

	def open_options(self):
		"""Open options popup."""
		self.option_window = Options(self.reload_player_grid)
		self.option_window.open()











class Options(Popup):
	def __init__(self,reloader,**kwargs):
		super(Options, self).__init__(**kwargs)
		self.reloader = reloader
		g.active_popup=self
		

	def return_to_main_screen(self):
		"""This will return all data to default."""
		current_phase = 'main' 
#		g.player_list =[]
#		g.selected_players = []
#		g.pairing = []
#		g.player_buttons = []
#		g.current_round = 0
#		g.bye_player.history = []
#		self.reloader()
		popup_dismiss()
		self.first_screen = First_Screen()
		Clock.schedule_once(self.first_screen.open)

#	def start_new_tournament(self):
#		confirmation_panel = confirm_Me('Title', 'Test', 'Button', self, self.save_results)
#		confirmation_panel.open()

	def confirm_close(self):
		confirmation = confirm_Me(title = 'Confirm Exit', text = "Goodbye, then?", btn_text = 'Yes', command=self.close_the_application)
		confirmation.open()
		
	def close_the_application(self):
		"""This will return all data to default."""
		thisApp.stop(thisApp)

	def reload_data(self):
		self.dismiss()
		g.reload_data()

	def save_results(self):
		confirmation = confirm_Me(title = 'Upload to server?', text = "If you upload, the current tournament may be added to AtT's Ranking.\n\nBefore accepting, please be sure it's a legit and complete tournament.\n\nAlso, be warned the results might be rejected by Ocastudios - if you think your tournament was unfairly ignored, you may contact them at oca@ocastudios.com.", btn_text = 'Upload '+g.tournament_name, command=self.upload_results)
		confirmation.open()


	def upload_results(self):
		"""This function will upload results to ocastudios database. It doesn't actually locally 'save' the current results, though - that is being automatically done every step of the way."""
		self.dismiss()

		site_address = 'http://ocastudios.com/tournment_computer.php'
		player_list = sorted(g.player_list, key=lambda player: player.victories)[::-1]

		post_text = '>>>---------------------------------------------------------------\n'
		post_text += str(datetime.datetime.now())+'\n'
		try:
			ip = urllib2.urlopen('http://ip.42.pl/raw').read()
			post_text += g.tournament_name+' Tounament from '+ip+'\n'
		except:
			post_text += g.tournament_name+' Tounament\n'
		if len(player_list)>=2:
			if player_list[0].victories > player_list[1].victories:
				post_text += 'The champion is '+player_list[0].name+".\n\n"
		for player in player_list:
			byes = 0
			for enemy in player.history:
				if enemy.name == 'Bye':
					byes += 1
			victories = player.victories - byes		
			plays = len(player.history) - byes		
			post_text += player.name+" ("+player.army+") from "+ player.region +" wins "+str(victories)+" out of "+str(plays)+".\n"
		post_text += '>>>---------------------------------------------------------------\n'

		print post_text
		print g.tournament_name

		try:
			values = {'results':post_text}
			data = urllib.urlencode(values)

			request = urllib2.Request(site_address,data)
			response = urllib2.urlopen(request)


			print 'uploaded tournament', g.tournament_name
		except:
			print 'Could not upload results.'

	def tutorial(self):
		t = Tutorial_Panel()
		t.open()







class First_Screen(ModalView):
	def __init__(self,**kwargs):
		super(First_Screen, self).__init__(**kwargs)


		#front_image_list = ['logo.png', 'icon_west.png', 'icon_undead.png', 'icon_fae.png', 'icon_alien.png', 'icon_east.png', 'icon_robot.png', 'icon_bandit.png', 'icon_south.png', 'icon_north.png']
		#self.ids.front_image.source = 'images/'+random.choice(front_image_list)
		#self.parent = parent

		self.ids.front_image.source = get_random_image(att_icon = True, oca_icon = False, army_icons = False, troop_images = False, extra_troops = False)

		self.ids.front_image.reload()


		retrieved = None

		try:
			retrieved = pickle.load(open('log','rb'))			
			print "log ----> ",retrieved
			#player_list = retrieved[0]
			current_round = retrieved[1]
			#bye_player = retrieved[2]
			tournament_name = retrieved[3]
			self.ids.button_resume.text = "Resume "+tournament_name+" ("+str(current_round)+")"
		except:
			print "log ---> failed :)"
			self.ids.button_resume.disabled = True
			self.ids.button_resume.text = "No Previous Tournament"

	def proceed(self):
		g.tournament_name = self.ids.tournament_name.text

		g.player_list =[]
		g.selected_players = []
		g.pairing = []
		g.player_buttons = []
		g.current_round = 0
		g.bye_player.history = []
		g.main_window.reload_player_grid()
		self.dismiss()

	def resume(self):
		self.dismiss()
		g.reload_data()

	def tutorial(self):
		t = Tutorial_Panel()
		t.open()

		




class Tutorial_Panel(Popup):
	def __init__(self,**kwargs):
		super(Tutorial_Panel, self).__init__(**kwargs)
		pass


class Pairing_Screen(ModalView):
	def __init__(self,**kwargs):
		super(Pairing_Screen, self).__init__(**kwargs)

		self.combinations = []
		#self.count = self.ids.progress_bar.value

		if len(g.selected_players)%2!=0: #When there's an odd number of players
			g.selected_players.append(g.bye_player)	#Add bye to the list
			g.bye_player.victories = g.current_round+1 #And make it so the leading players get a better chance of a bye

		self.time_count = Clock.schedule_interval(self.pairing, 0.01)




	def pairing(self,value = 'none'):
		"""This is an important function! It will find the most suitable pairing for a round of games. It does so by analysing a number of possible combinations (the exact number is defined by g.pairing_iterations, but it should be kept between 100 and 1000). The difference in victories for each pair is added as a 'bad', and 5 more 'bads' are added for each time the pair has met before. The combination with the least amount of bads is picked (0 bads being a perfect pairing). This will return a combination object."""
		#print 'progress bar',self.ids.progress_bar.value
		if self.ids.progress_bar.value == self.ids.progress_bar.max:
			#If all combinations have been reached.
			chosen_combination = None
			least_bad = self.combinations[0].bad+1
			for item in self.combinations:
				if item.bad<least_bad:
					chosen_combination = item
					least_bad = item.bad
			g.pairing = chosen_combination#[:]
			print 'unscheduled at',self.ids.progress_bar.value,len(self.combinations)
			print 'chosen combination',chosen_combination.bad

			Clock.unschedule(self.pairing)#self.time_count)

			battle_panel = Battle_Panel()
			battle_panel.open()

			self.dismiss()

		else:
			#If there are still combinations to accomplish.
			iterations = 0
			#for i in range(20):
			while iterations <50:

				temp_list = g.selected_players[:]#g.player_list[:]
				this_combination = Combination(0,[])
				while len(temp_list)>0:
					player1 = random.choice(temp_list)
					temp_list.remove(player1)
					player2 = random.choice(temp_list)
					temp_list.remove(player2)
					this_combination.pairs.append((player1,player2))

				for paired in this_combination.pairs:

					bad = 0 #Bad measures the quality of a round of battles
					bad_rank =0 #Bad rank is the penalty for pairing players of different skill levels
					bad_repetition=0 #Bad repetitions is the penalty for repeating duels

					#print 'pair ->',paired[0].name,paired[0].victories,paired[1].name,paired[1].victories

					win_list = sorted([paired[0].victories, paired[1].victories],reverse=True)
					bad_rank = win_list[0]-win_list[1]
					if g.bye_player in paired: bad_rank -= 1

					#if paired[0] in paired[1].history:
					if paired[0].name == 'Bye' or paired[1].name == 'Bye':
						bad_repetition += paired[1].history.count(paired[0])*10000
					else:
						bad_repetition += paired[1].history.count(paired[0])*100

					bad = bad_rank+bad_repetition
					this_combination.bad+=bad

					#print 'pair',bad

				#print 'combination',this_combination.bad

				if this_combination.bad == 0:
					self.combinations = [this_combination]
					self.ids.progress_bar.value = self.ids.progress_bar.max
					print "Found perfect combination."
					iterations +=50
				else:
					self.combinations.append(this_combination)
					self.ids.progress_bar.value+=1
					iterations +=1

					#break


			


#				if this_combination.bad == 0:
#					combinations = [this_combination]
#					self.count = self.ids.progress_bar.max
#					break
						
	

class Splash_Screen(ModalView):
	def __init__(self,parent,**kwargs):
		super(Splash_Screen, self).__init__(**kwargs)
		self.main_screen = parent

		self.time_count = Clock.schedule_interval(self.waiting, 0.09)
		
		self.fadein = Animation(color = (1,1,1,0.8),duration=0.8)
		self.fadeout = Animation(color = (1,1,1,0),duration=0.8)


	def waiting(self,value='none'):
		times =[5,30,40,45,70]
		#times =[4,15,20,22,35]

		if self.ids.progress_bar.value == times[0]:
			self.fadein.start(self.ids.greet_image)
			self.fadein.start(self.ids.greet_text)

		if self.ids.progress_bar.value == times[1]:
			self.fadeout.start(self.ids.greet_image)
			self.fadeout.start(self.ids.greet_text)

		if self.ids.progress_bar.value == times[2]:
			self.ids.greet_image.source = get_random_image(att_icon = False, oca_icon = False, army_icons = False, troop_images = True, extra_troops = True)
			self.ids.greet_image.reload()
			self.ids.greet_text.text = 'www.ocastudios.com'
			self.ids.greet_text.font_size = sp(22)

		if self.ids.progress_bar.value == times[3]:
			self.fadein.start(self.ids.greet_image)
			self.fadein.start(self.ids.greet_text)

		if self.ids.progress_bar.value == times[4]:
			self.fadeout.start(self.ids.greet_image)
			self.fadeout.start(self.ids.greet_text)


			
		if self.ids.progress_bar.value>=self.ids.progress_bar.max:
			Clock.unschedule(self.waiting)#self.time_count)

			self.main_screen.first_screen = First_Screen()
			Clock.schedule_once(self.main_screen.first_screen.open)

			self.dismiss()
		else:
			self.ids.progress_bar.value+=1




class tournamentApp(App):
	"""This is the main class. It sets basic parameters when initializing, and calls the main layout."""
	icon='logo.png'
	title='AtT Tournament'

	def build(self):
		"""Setting initial parameters and calls for creation of main layout."""
		g.current_phase = 'main'
		g.player_list =[]
		g.selected_players = []
		g.pairing = []
		g.player_buttons = []
		g.active_popup = None
		g.current_round = 0
		Clock.max_iteration = 100

		return layout_main()

	def on_pause(self):
		return True

	def on_resume(self):
		pass




thisApp = None

if __name__ == '__android__':
	thisApp = tournamentApp()
	thisApp.run()
elif __name__ == '__main__':
	Config.set('graphics','width',400)
	Config.set('graphics','height',600)
	Config.set('graphics','resizable',0)
	Config.write()
	thisApp = tournamentApp()
	thisApp.run()

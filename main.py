import kivy
kivy.require('1.8.0')

from kivy.app import App
from kivy.config import Config

#from kivy.uix.widget import Widget
#from kivy.uix.floatlayout import FloatLayout
#from kivy.uix.relativelayout import RelativeLayout
#from kivy.uix.image import Image
#from kivy.uix.label import Label
#from kivy.uix.scatter import Scatter
#from kivy.uix.button import Button
#from kivy.uix.togglebutton import ToggleButton
#from kivy.uix.checkbox import CheckBox
#from kivy.uix.scrollview import ScrollView
#from kivy.uix.stencilview import StencilView
#from kivy.uix.modalview import ModalView
#from kivy.uix.boxlayout import BoxLayout
#from kivy.graphics import *
#from kivy.uix.behaviors import ButtonBehavior
#from kivy.uix.textinput import TextInput
#from math import sqrt
#from kivy.uix.screenmanager import *#ScreenManager, Screen, FadeTransition, SwapTransition
#from kivy.animation import *
#from kivy.clock import Clock

#import os
#import cPickle as Pickle
#from random import shuffle
#from random import randint
#from random import choice
#import random

import g
#import screen_splash
from basic_widgets import *
from screen_splash import *
from screen_title import *
from screen_profile import *
from screen_tutorial import *
from screen_tournament import *
from screen_transition import *
from screen_main import *

class oleApp(App):
	"""This is the main class. It sets basic parameters when initializing, and calls the main layout."""
#	icon='logo.png'
#	title='AtT Tournament'

	def build(self):
		"""Setting initial parameters and calls for creation of main layout."""

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

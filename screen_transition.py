import kivy
kivy.require('1.8.0')

from kivy.uix.screenmanager import *
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.clock import Clock

import g

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
		


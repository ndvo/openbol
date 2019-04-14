import kivy
kivy.require('1.8.0')

from kivy.uix.screenmanager import *
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.animation import *
import g

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

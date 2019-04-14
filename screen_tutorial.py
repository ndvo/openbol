import kivy
kivy.require('1.8.0')

from kivy.uix.screenmanager import *
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout

import g
from basic_widgets import *

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

			



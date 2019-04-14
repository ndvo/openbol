import kivy
kivy.require('1.8.0')

from kivy.uix.screenmanager import *
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton

import g

from basic_widgets import *

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





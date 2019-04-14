import kivy
kivy.require('1.8.0')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.config import Config
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.scatter import Scatter
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import *
from kivy.uix.behaviors import ButtonBehavior
from math import sqrt

import g

class circleButton(ButtonBehavior,Image):
	def __init__(self,**kwargs):
		super(circleButton, self).__init__(**kwargs)
		self.source='./data/images/interface-circle-black.png'
		self.size_hint = (None,None)
		self.size = (160,140)
		self.bind(on_release = self.btn_release)
		self.pos = (100,0)

		font_path = './data/fonts/MANDINGO.TTF'
		small_text = 'none'
		if g.match['play'] == 0:
			small_text = 'preparation'
		elif g.match['play'] == 1:
			small_text = 'first play'
		elif g.match['play'] == 2:
			small_text = 'second play'
		elif g.match['play'] == 3:
			small_text = 'third play'
		elif g.match['play'] == 4:
			small_text = 'fourth play'
		elif g.match['play'] == 5:
			small_text = 'fifth play'
		elif g.match['play'] == -1:
			small_text = 'finished'
		white = (1,1,1,1)
		self.small_label = Label(text=small_text,font_size='18sp',font_name=font_path, color=white)
		self.small_label.halign = 'center'
		self.small_label.valign = 'middle'
		self.small_label.pos = [self.pos[0],self.pos[1]+60]
		self.small_label.size_hint = (None,None)
		self.small_label.size = (160,100)

		#big_text = str(g.match['score_player'])+' '+str(g.match['score_opponent'])

		#self.big_label = Label(text=big_text,font_size='80sp',font_name=font_path, color=white)
		#self.big_label.halign = 'center'
		#self.big_label.valign = 'middle'
		#self.big_label.pos = [self.pos[0],self.pos[1]+4]
		#self.big_label.size_hint = (None,None)
		#self.big_label.size = (160,100)


		self.score_player = Label(text=str(g.match['score_player']), font_size='65sp', font_name=font_path, color=white)
		self.score_player.halign = 'center'
		self.score_player.valign = 'middle'
		self.score_player.pos = [self.pos[0]-43,self.pos[1]+7]
		self.score_player.size_hint = (None,None)
		self.score_player.size = (160,100)

		self.score_opponent = Label(text=str(g.match['score_opponent']), font_size='65sp', font_name=font_path, color=white)
		self.score_opponent.halign = 'center'
		self.score_opponent.valign = 'middle'
		self.score_opponent.pos = [self.pos[0]+43,self.pos[1]+7]
		self.score_opponent.size_hint = (None,None)
		self.score_opponent.size = (160,100)


		self.add_widget(self.score_player)
		self.add_widget(self.score_opponent)
		self.add_widget(self.small_label)

	def btn_release(self, marker_object):
		print "clicked button"


class smallCard(ButtonBehavior,Image):
	def __init__(self, card_type, card_name, **kwargs):
		super(smallCard, self).__init__(**kwargs)
		if card_type == 'formation': card_type = 'sf'
		elif card_type == 'tactic': card_type = 't'

		elif card_type == 'defender': card_type = 'pd'
		elif card_type == 'midfielder': card_type = 'pm'
		elif card_type == 'attacker': card_type = 'pa'

		self.source='./data/images/card-'+card_type+'-'+card_name+'.png'
		self.size_hint = (None,None)
		self.size = (58,100)
		self.bind(on_release = self.card_release)

	def card_release(self, marker_object):
		print "clicked card"
		

class cardHand(ScrollView):
	def __init__(self,**kwargs):
		super(cardHand, self).__init__(**kwargs)
		#self.do_scroll_y = False
		self.size_hint = (None,None)
		self.size = (360,100)
		self.pos = (0,123)

		self.box_layout = BoxLayout(orientation = 'horizontal')
		self.box_layout.size_hint = (None,1)
		#self.box_layout.width = len(g.team['hand'])*58

		#Add mock cards
		list_of_formations = ['343','352','433','442','4231','kami','libero','metodo','pyr','wm']
		list_of_tactics = ['ball','col','count','direct','for','indiv','long','man','offside','runs','set','zone']
		list_of_defenders = ['fast','leader','talent','util']
		list_of_midfielders = ['fast','leader','opport','talent','util']
		list_of_attackers = ['fast','leader','opport']

		self.box_layout.width = (len(list_of_formations)+len(list_of_tactics)+len(list_of_defenders)+len(list_of_midfielders)+len(list_of_attackers))*58

		for card in list_of_formations:
			self.box_layout.add_widget(smallCard('formation',card))
		for card in list_of_tactics:
			self.box_layout.add_widget(smallCard('tactic',card))

		for card in list_of_defenders:
			self.box_layout.add_widget(smallCard('defender',card))
		for card in list_of_midfielders:
			self.box_layout.add_widget(smallCard('midfielder',card))
		for card in list_of_attackers:
			self.box_layout.add_widget(smallCard('attacker',card))


		self.add_widget(self.box_layout)

		print 'sizes:/n scroll =',self.size,'   box =',self.box_layout.size



class zoneMarker(ButtonBehavior,Image):
	"""There are 6 zoneMarkers in the game, indicating the strenght of the Defense, Midfield and Attack zones of each team. Besides informing how strong the zones are, they are clickable buttons that bring about popups informing about the cards attached to the zone and their effects."""
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
		

		
	

class job:
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


		
		
class layout_main(FloatLayout):
	def __init__(self,**kwargs):
		super(layout_main,self).__init__(**kwargs)

		img_soccer_pitch = Image(source='./data/images/background-field.png')
		self.add_widget(img_soccer_pitch)

		img_bottom_bar = Image(source='./data/images/interface-lowpanel-plain.png', pos=(0, -260))
		self.add_widget(img_bottom_bar)

		with self.canvas: Rectangle(pos=(0, 120), size=(360, 3))

		img_mid_bar = Image(source='./data/images/interface-midpanel-logo.png',pos=(0, -147))
		self.add_widget(img_mid_bar)

		with self.canvas: Rectangle(pos=(0, 223), size=(360, 12))

		white_bar_label = Label(text='THESE ACTIONS ARE CURRENTLY AVAILABLE TO YOU', color = (0.67,0.67,0.67,1), font_size = 10, pos= (-100,-92), font_name = './data/fonts/H.H. Samuel-font-defharo.ttf')
		self.add_widget(white_bar_label)

		self.create_position_buttons() #Creates the positions (jobs) for the player pins
		self.deploy_players() #Automatically deploys players according to formation

		self.create_zone_markers()

		#Create card-box to receive player's cards
		self.add_widget(cardHand())

		#Add interface button (lower black circle)
		self.add_widget(circleButton())


	def create_zone_markers(self):
		self.add_widget(zoneMarker(zone = 'attack', position = (0,475)))
		self.add_widget(zoneMarker(zone = 'midfield',source='./data/images/zone-midfield-left-normal.png', position = (0,355)))
		self.add_widget(zoneMarker(zone = 'defense',source='./data/images/zone-defense-left-normal.png', position = (0,235)))





	def create_position_buttons(self):
		"""Creates the player positions, called 'jobs'. It creates both the background images for them and the job obscts, which holds the data but have no visual rendering."""

		#The background images representing the positions (jobs) and independent from the job objects, which
		#have no graphic representation. This functions creates both.
		job_list = [ ['st',(-22,250)], ['st',(22,250)], ['lw',(-86,230)], ['fw',(-42,208)], ['fw',(0,208)], ['fw',(42,208)], ['rw',(86,230)], ['am',(0,140)], ['lf',(-108,119)], ['cm',(-66,100)], ['cm',(-22,100)], ['cm',(22,100)], ['cm',(66,100)], ['rf',(108,119)], ['hm',(-22,57)], ['hm',(22,57)], ['lb',(-108,5)], ['cb',(-66,-18)], ['cb',(-22,-18)], ['cb',(22,-18)], ['cb',(66,-18)], ['rb',(108,5)], ['sw',(0,-60)] ]

		for item in job_list:
			self.add_widget(Image(source='./data/images/position-'+item[0]+'.png', pos = item[1]))			
			g.job_list.append(job(position = item[1], code = item[0]))

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

		return layout_main()

	def on_pause(self):
		return True

	def on_resume(self):
		pass


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

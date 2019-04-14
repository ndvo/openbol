import kivy
kivy.require('1.8.0')

from kivy.uix.screenmanager import *
from kivy.uix.modalview import ModalView
from kivy.uix.button import Button
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.scatter import Scatter
from kivy.uix.label import Label
from kivy.uix.stencilview import StencilView
from kivy.graphics import *
from kivy.clock import Clock

import random
from math import sqrt

import g
from basic_widgets import *


class mainScreen(Screen):
	"""This is the main screen, where the actual game takes place. As all screens it carris a .name attribute. It also carries a .zone_str that has the updated zone values for both players (the g.save doesn't carry update the values due to positions and effects). As all screens, it has an __init__ function that runs when the game is initiated (all screens are created when the game initializes), and an on_called function for when it is shown to the player. Unlike other screens, the main screen must change to different stages of the game, called 'actions'. Every time the action changes, widgets might be destroyed, created or update, and the on_action function is called. It also has a on_leave function to destroy temporary widgets and unnecessary when the screen is left.
		The actions available are 'strategy', when the player is selecting his formation and tactic, and then there are 'midfield', 'defense', 'attack', 'rebound' and 'counterattack', which reflect the next check to be made. They can also be counterattack_foe and rebound_foe, in case the opponent team is performing these special attacks."""

	def __init__(self,name,**kwargs):
		super(mainScreen,self).__init__(**kwargs)

		# A name attribute is a necessity for calling screens
		self.name = name

		# This attribute holds the updated zone strengths.
		self.zone_str = {'friend': {'atk':0,'mid':0,'def':0}, 'foe':{'atk':0,'mid':0,'def':0}}

		# Widgets in this list will be destroyed when the screen is left, and reconstructed when it is called again.
		self.temporary_widgets = []

		# We must create the permanent widgets. These are the background images, and the bottom bars.
		self.create_permanent_widgets()

		# !!!! We must reevaluate these attributes for cleanliness
		self.active_message = None
		self.interrupt_messages = False

	def on_called(self):
		"""This function runs when the screen is called for view. It must update information about the current match, and create the necessary widgets for the match."""

		# !? # We update the opponent team's data, taking it form g database and adding to self.zone_str
		opponent_data = g.opponents[g.save.match['opponent']]
		self.zone_str['foe']['atk'] = opponent_data['atk']
		self.zone_str['foe']['mid'] = opponent_data['mid']
		self.zone_str['foe']['def'] = opponent_data['def']

		# Now we create the  temporary widgets that must be ready as the player enters this screen.
		# What widgets are those vary if it is a new game (primary widgets) or an old game loaded (secondary).
		if g.save.match['action'] == 'strategy':
			# Meaning it is a new game
			self.create_primary_widgets()
			print 'action is',g.save.match['action']
		else:
			# Meaning there were a prior game
			self.create_primary_widgets()
			self.create_secondary_widgets()
			print 'action is rather',g.save.match['action']

		# !!!!! self.stage = 'match_preparation'
		self.msg_count = 0

		# !!!!! stuff to rethink about (were uncommented)
		#g.save.match['action'] = 'strategy'
		#self.prepare_layout()
		#Clock.schedule_once(self.load_messages)


	def on_card_clicked(self, card_id, card_object, card_state):
		"""This function determines what happens when a card is clicked in the main screen. There are a couple of options. If it is not the strategy stage, formations cannot be equiped. If it is another stage, the formation can be unequiped, tactics can be changed, and so can players. During other stages, cards can't be changed at all.
		Also, at any given time, only one formation and one tactic can be equipped. Selecting another will automatically deselect the previous."""

		# First possiblity: the card is blocked. Then we reverse selection
		if card_object.mode == 'blocked':
			if card_object.state == 'normal': card_object.state = 'down'
			elif card_object.state == 'down': card_object.state = 'normal'

		# Second possibility: the card is not blocked. Then we must decide what to do with it.
		else:
			# What will happen depens on the card type and the current action, so we discover them.
			# We also prepare to recalculate zones, which might come to be a necessity.
			clicked_card_type = card_object.get_type()
			current_action = g.save.match['action']
			recalculate_zones = True
	
			# In the Strategy Stage, all cards are clickable, but only 
			# one formation and one tactic can be active at any point.
		
			# First, let's deal with what happened when a card was seleted, rather than diselected.	
			if card_state == 'normal':

				# If a formation was selected, we must prevent two formations from being equiped at the same time.
				if clicked_card_type == 'formation':
					selected_formations = self.card_hand.get_cards_by_type(card_state = 'selected', card_type = 'formation')
					if len(selected_formations)>1:
						# Multiple formations are selected. 
						# The old one must be unselected so the new one becomes the only.
						for card in selected_formations:
							if card != card_object:
								card.state = 'down'
						# This will make sure there are not more skills equiped than allowed.
						self.reevaluate_skills()
								#recalculate_zones = False
	
				# If a tactic was selected, we must prevent two tactics from being equiped at the same time.
				elif clicked_card_type == 'tactic':
					selected_tactics = self.card_hand.get_cards_by_type(card_state = 'selected', card_type = 'tactic')
					if len(selected_tactics)>1:
						# Multiple tactics selected. 
						# The old one must be unselected so the new one becomes the only.
						for card in selected_tactics:
							if card != card_object:
								card.state = 'down'
						#self.reevaluate_skills()
	
			# If a skill was selected, we must prevent that there are more equiped skills than what is allowed
			# by the selected formation.
				if clicked_card_type in ['attacker','defender','midfielder']:
					list_of_formations = self.card_hand.get_cards_by_type(card_state = 'selected', card_type = 'formation')
					if list_of_formations == []:
						#There are no equiped formation and, thus, the player cannot equip skills yet.
						card_object.state = 'down'
						recalculate_zones = False
						print "In the strategy stage, you may not equip skills without a formation. Wait for a preparation phase."
					else:
						# There is an equiped formation and, thus, he can equip some skills
						formation = list_of_formations[0]
						skill_limit = None
						# This wil allow us to target the relevant zone to the selected skill.		
						zone_index = 0 # The selected card was a defender
						if clicked_card_type == 'midfielder': zone_index =1 # The selected card was a midfielder
						elif clicked_card_type == 'attaker': zone_index = 2 # The selected card was an attacker
						# The skill limit tells us how many skills slots are allowed by the formation.
						skill_limit = g.formations[formation.name]['men'][zone_index]
						# Now we check if the limit was exceeded.
						if len(self.card_hand.get_cards_by_type(card_state = 'selected', card_type = clicked_card_type)) > skill_limit:
							# If so, we reverse selection.
							card_object.state = 'down'
							recalculate_zones = False
		
					
			# Now let's deal with what happens when a card is diselected, rather than selected.
			elif card_state == 'down':
				# It depends on the card type.
				if clicked_card_type == 'formation':
					# If a formation is removed, all equiped skills are unequiped, since one cannot have
					# skills without a formation in the strategy stage.
					equiped_skills = self.card_hand.get_cards_by_type(card_state = 'selected', card_type = 'skill')
					for card in equiped_skills:
						card.state = 'down'
		
			# If there was a change that affects the zone strength, then we must recalculate it.
			if recalculate_zones:
				self.calculate_zone_strength()


	def reevaluate_skills(self):
		"""This function will check how many skills may de alotted to each zone, according to the selected formation or lack of it."""
		formation = self.card_hand.get_cards_by_type(card_state = 'selected', card_type = 'formation')[0]
		def_limit = g.formations[formation.name]['men'][0]
		mid_limit = g.formations[formation.name]['men'][1]
		atk_limit = g.formations[formation.name]['men'][2]

		def_list = self.card_hand.get_cards_by_type(card_state = 'selected', card_type = 'defender')
		mid_list = self.card_hand.get_cards_by_type(card_state = 'selected', card_type = 'midfielder')
		atk_list = self.card_hand.get_cards_by_type(card_state = 'selected', card_type = 'attacker')

		def_remove = -( def_limit - len(def_list) )
		mid_remove = -( mid_limit - len(mid_list) )
		atk_remove = -( atk_limit - len(atk_list) )

		for card in def_list:
			if def_remove >0:
				card.state = 'down'
				def_remove -= 1

		for card in mid_list:
			if mid_remove >0:
				card.state = 'down'
				mid_remove -= 1

		for card in atk_list:
			if atk_remove >0:
				card.state = 'down'
				atk_remove -= 1

#---------------------------------------------
# Reviewed functions from main class
#---------------------------------------------

	def on_leave(self):
		"""This function is called when the screen is exited. It will clean the memory of temporary widgets and unnecessary data."""
		
		# Let's go through the temporary widgets removing their vinculum to the main screen, which will allow
		# the automatic garbage collector to take them out.
		for widget in self.temporary_widgets:
			self.remove_widget(widget)

		#Now we clear the data from the job list
		g.job_list = []

	def create_permanent_widgets(self):
		"""This function will create and add the permanent widgets - those that are not added to the temporary list and, thus, remains for the entire life of the app. The permanent widgets are the background, the bottom bar, where the team buttons go, the mid bar, where the card hand goes, and the black bar, that acts as message board. We also and a rectangle bar just for design."""

		img_soccer_pitch = Image(source='./data/images/background-field.png')
		img_bottom_bar = Image(source='./data/images/interface-lowpanel-plain.png', pos=(0, -260))
		img_mid_bar = Image(source='./data/images/interface-midpanel-logo.png',pos=(0, -147))
		black_bar = Image(source='./data/images/interface-message-bar.png',pos=(0, -77))

		self.add_widget(img_soccer_pitch)
		self.add_widget(img_bottom_bar)
		self.add_widget(img_mid_bar)
		self.add_widget(black_bar)

		with self.canvas: Rectangle(pos=(0, 120), size=(360, 3))


	def create_primary_widgets(self):
		"""This function will create the primary temporary widgets, which are the absolute necessary widgets the must be there in a new game, but that will be destroyed when the screen closes. Those are the teams' buttons in the lower part, The card hand, the left zone markers and their labels. These widgets are then added to the temporary widget list and as children of the screen."""

		# Create the zone markers and the zone labels
		zone_marker_friend = Image(source='./data/images/interface-zone-markers-friend.png',pos=(-180+25, -40+180-8))
		self.str_atk_own = Label(text=str(self.zone_str['friend']['atk']),font_size='40sp',font_name= g.FONT_MANDINGO, color= g.COLOR_BLACK, pos = (-155,260))
		self.str_mid_own = Label(text=str(self.zone_str['friend']['mid']),font_size='40sp',font_name= g.FONT_MANDINGO, color= g.COLOR_BLACK, pos = (-155,135))
		self.str_def_own = Label(text=str(self.zone_str['friend']['def']),font_size='40sp',font_name= g.FONT_MANDINGO, color= g.COLOR_BLACK, pos = (-155,9))

		# Create the team buttons
		self.team_btn_friend = teamButton('friend')
		self.team_btn_foe = teamButton('foe')

		#Create the card hand
		self.card_hand = cardHand(list_of_cards=g.save.tournament['available_cards'])

		# Create the ball button
		circle_button = circleButton()

		# We add the widgets to the temporary widget list
		self.temporary_widgets.append(zone_marker_friend)
		self.temporary_widgets.append(self.str_atk_own)
		self.temporary_widgets.append(self.str_mid_own)
		self.temporary_widgets.append(self.str_def_own)
		self.temporary_widgets.append(self.team_btn_friend)
		self.temporary_widgets.append(self.team_btn_foe)
		self.temporary_widgets.append(self.card_hand)
		self.temporary_widgets.append(circle_button)

		# And now we add the widgets to the main screen
		self.add_widget(zone_marker_friend)
		self.add_widget(self.str_atk_own)
		self.add_widget(self.str_mid_own)
		self.add_widget(self.str_def_own)
		self.add_widget(self.team_btn_friend)
		self.add_widget(self.team_btn_foe)
		self.add_widget(self.card_hand)
		self.add_widget(circle_button)

		# Now we call the function that recaulculates the zone values. The reason is that when you create a card hand
		# some cards will appear already selected, and they may be (probably are) already establishing new
		# zone values. The function will update both self.zone_str and the zone label widgets.
		self.calculate_zone_strength()


	def create_secondary_widgets(self):
		"""This funtions creates the secondary widgets, which are needed after the strategy stage. It also adds them to the temporary widgets list, to the main screen and updates them.
		The secondary temporary widgets are: job (position) markers, friend and foe score labels, foe zone markers, foe zone labels and the men (players)."""

		# Creates the job markers. The function will handle itself 
		# the widget creation and adding to the temporary widget list.
		self.create_position_buttons()

		# Create the scores for the teams in the lower part of screen
		self.team_score = Label( text=str(0), font_size='85sp', font_name=g.FONT_MANDINGO, color=g.COLOR_WHITE, pos = (-130,-260) )
		self.opponent_score = Label( text=str(0), font_size='85sp', font_name=g.FONT_MANDINGO, color=g.COLOR_WHITE, pos = (130,-260) )
		
		# Creates the foe's zone marker (the triangles under the zone strength labels)
		zone_marker_foe = Image(source='./data/images/interface-zone-markers-foe.png',pos=(130+25, -40+180-8))

		# Create the foe's zone labels, which indicate how strong is each of his zones
		self.str_atk_opp = Label(text=str(self.zone_str['foe']['atk']),font_size='40sp',font_name=g.FONT_MANDINGO, color=g.COLOR_BLACK, pos = (155,260))
		self.str_mid_opp = Label(text=str(self.zone_str['foe']['mid']),font_size='40sp',font_name=g.FONT_MANDINGO, color=g.COLOR_BLACK, pos = (155,135))
		self.str_def_opp = Label(text=str(self.zone_str['foe']['def']),font_size='40sp',font_name=g.FONT_MANDINGO, color=g.COLOR_BLACK, pos = (155,9))

		# Now we add these widgets to the temporary widgets list
		self.temporary_widgets.append(self.team_score)
		self.temporary_widgets.append(self.opponent_score)
		self.temporary_widgets.append(zone_marker_foe)
		self.temporary_widgets.append(self.str_atk_opp)
		self.temporary_widgets.append(self.str_mid_opp)
		self.temporary_widgets.append(self.str_def_opp)

		# And add them as children to the main screen, so they are visible
		self.add_widget(self.team_score)
		self.add_widget(self.opponent_score)
		self.add_widget(zone_marker_foe)
		self.add_widget(self.str_atk_opp)
		self.add_widget(self.str_mid_opp)
		self.add_widget(self.str_def_opp)

		# We finally create the men themselves. This function will create them 
		# and add them to thetemporary list and as children to the main screen.
		# It will also place them in the right zones according to the chosen formation.
		self.deploy_players()


	def calculate_zone_strength(self):
		"""This function will recalculate the zone strengths of the player's team, taking into account formation, tactics, skills, counterattacks and rebounds. It will also update the zone lables on screen."""

		# First we get the selected cards. Keep in mind these are lists of card object, although the formation
		# and tactic list must contain only one element.
		chosen_formation = self.card_hand.get_cards_by_type(card_type = 'formation', card_state = 'selected')
		chosen_tactic = self.card_hand.get_cards_by_type(card_type = 'tactic', card_state = 'selected')
		chosen_skills = self.card_hand.get_cards_by_type(card_type = 'skill', card_state = 'selected')
		chosen_defenders = self.card_hand.get_cards_by_type(card_type = 'defender', card_state = 'selected')
		chosen_midfielders = self.card_hand.get_cards_by_type(card_type = 'midfielder', card_state = 'selected')
		chosen_attackers = self.card_hand.get_cards_by_type(card_type = 'attacker', card_state = 'selected')

		# We now replicate some lists, adding the name instead of card object.
		# This makes it much easier to know what cards are selected
		chosen_defenders_name = []
		chosen_midfielders_name = []
		chosen_attackers_name = []
		for card in chosen_defenders:
			chosen_defenders_name.append(card.name)
		for card in chosen_midfielders:
			chosen_midfielders_name.append(card.name)
		for card in chosen_attackers:
			chosen_attackers_name.append(card.name)

		# This list will be our final result. We will add to it as we check the cards.
		zone_values = [0,0,0]

		# Let's add the formation values, if there is a formtaion selected
		if len(chosen_formation) > 0:
			zone_values[0] += g.formations[chosen_formation[0].name]['strength'][0]
			zone_values[1] += g.formations[chosen_formation[0].name]['strength'][1]
			zone_values[2] += g.formations[chosen_formation[0].name]['strength'][2]

		# Let's add the tactic values, if there is a formtaion selected
		if len(chosen_tactic) > 0:
			zone_values[0] += g.tactics[chosen_tactic[0].name]['strength'][0]
			zone_values[1] += g.tactics[chosen_tactic[0].name]['strength'][1]
			zone_values[2] += g.tactics[chosen_tactic[0].name]['strength'][2]

			# Some tactics have conditional bonuses. For example, the Long Balls tactic ('t-long') gives a +4 attack bonus
			# to counterattacks. These conditional tactics must be considered separately.
			if chosen_tactic[0].name == 'counter':
				if g.save.match['action'] == 'counterattack':
					zone_values[2] += 4
			elif chosen_tactic[0].name == 'indiv':
				if 'pd_talent' in chosen_defenders_name:
					zone_values[0] += 1
				if 'pm_talent' in chosen_midfielders_name:
					zone_values[1] += 1
				if 'pa_talent' in chosen_attackers_name:
					zone_values[2] += 1
			elif chosen_tactic[0].name == 'man':
				# !!! IMPORTANT
				# This must be corrected further on. It gives the bonus if your formation requires 4 players, but
				# it should give it if you actually have four players. An utilitarian player taken away from the
				# defense zone could prevent the card form taking effect. You could likewise get the bonus
				# because of utilitarian players moved to defense, even if your formation would not allow it.
				if len(chosen_formation) > 0:
					if chosen_formation[0].name in ['sf-4231', 'sf-433', 'sf-libero', 'sf-442', 'sf-424', 'sf-451']:
						zone_values[0] += 3
			# Two tactics are not covered here. The Forward Defense ('forward') gives a chance for rebound and the Offside Trap ('offside') gives either a bonus or a penalty to defense. These must be taken into accont somewhere eles. The first one is considered after every attack check and the later, during every defense check.

		# Now we add the bonus given by having the talented player skills
		zone_values[0] += chosen_defenders_name.count('pd_talent')
		zone_values[1] += chosen_midfielders_name.count('pm_talent')
		zone_values[2] += chosen_attackers_name.count('pa_talent')

		# We also add the bonus for having fast and opportunist player skills
		if g.save.match['action'] == 'counterattack':
			zone_values[2] += chosen_defenders_name.count('pd_fast')
			zone_values[2] += chosen_midfielders_name.count('pm_fast')
		elif g.save.match['action'] == 'rebound':
			zone_values[2] += chosen_defenders_name.count('pd_opport')
			zone_values[2] += chosen_midfielders_name.count('pm_opport')
			
		# We set the updated self.zone_str
		self.zone_str['friend']['def'] = zone_values[0]
		self.zone_str['friend']['mid'] = zone_values[1]
		self.zone_str['friend']['atk'] = zone_values[2]

		# And we update the counters on screen
		self.str_atk_own.text = str(zone_values[2])
		self.str_mid_own.text = str(zone_values[1])
		self.str_def_own.text = str(zone_values[0])


	def create_position_buttons(self):
		"""Creates the player positions, called 'jobs'. It only creates both the background images for them and the job objects, which holds the data but have no visual rendering. Although the men available to each zone depend on the formation, the jobs available do not - they are universal to all formations and no formation."""

		# The background images representing the positions (jobs) and independent from
		# the job objects, which have no graphic representation. This functions creates both.

		# First we create lists with the positions for each job, according to the zone.
		attackers_list = [ ['st',(-22,250)], ['st',(22,250)], ['lw',(-86,230)], ['fw',(-42,208)], ['fw',(0,208)], ['fw',(42,208)], ['rw',(86,230)] ]
		midfielders_list = [ ['am',(0,140)], ['lf',(-108,119)], ['cm',(-66,100)], ['cm',(-22,100)], ['cm',(22,100)], ['cm',(66,100)], ['rf',(108,119)], ['hm',(-22,57)], ['hm',(22,57)] ]
		defenders_list = [ ['lb',(-108,5)], ['cb',(-66,-18)], ['cb',(-22,-18)], ['cb',(22,-18)], ['cb',(66,-18)], ['rb',(108,5)], ['sw',(0,-60)] ]
		
		#This is a design options. These are positional modifiers that allows us to move entire zones.
		atk_pos_mod = (0,8)
		mid_pos_mod = (0,18)
		def_pos_mod = (0,28)

		# Now, for job in each zone we create the image widget and create the Job object.
		for job in attackers_list:
			job_pos = (job[1][0]+atk_pos_mod[0], job[1][1]+atk_pos_mod[1])
			job_image = Image(source='./data/images/position-'+job[0]+'.png', pos = job_pos )
			self.temporary_widgets.append(job_image)
			self.add_widget(job_image)			
			g.job_list.append(Job(position = job_pos, code = job[0]))

		for job in midfielders_list:
			job_pos = (job[1][0]+mid_pos_mod[0], job[1][1]+mid_pos_mod[1])
			job_image = Image(source='./data/images/position-'+job[0]+'.png', pos = job_pos )
			self.temporary_widgets.append(job_image)
			self.add_widget(job_image)			
			g.job_list.append(Job(position = job_pos, code = job[0]))

		for job in defenders_list:
			job_pos = (job[1][0]+def_pos_mod[0], job[1][1]+def_pos_mod[1])
			job_image = Image(source='./data/images/position-'+job[0]+'.png', pos = job_pos )
			self.temporary_widgets.append(job_image)
			self.add_widget(job_image)			
			g.job_list.append(Job(position = job_pos, code = job[0]))
		# A Job object is a little packet of information that knows its own position, its own zone and whether he is occupied or not by a man. It also know his own position, which allows the user to activate the man on top of it.



	def deploy_players(self):
		"""This function creates the men (players, that can be dragged around to mark which jobs (positions) are taken and can be activated. It will assign automatic positions for the men, according to the selected formation's recquirements."""

		# Each Zone has a number of players assigned to it. 
		# We first have to figure out how many players go in each zone, according to the selected formation.
		selected_strategy = self.card_hand.get_cards_by_type(card_state = 'selected', card_type = 'formation')
		if len(selected_strategy) == 0:
			# No formation was selected, we default it to the parameter set in g.
			men_per_zone = g.sans_formation
		else:
			# Has formation, so we use its parameters.
			men_per_zone = g.formations[selected_strategy[0].name]['men']

		# The g.job_list is a list with all possible jobs. Let's call it 'j' to make the code more readable.
		j = g.job_list

		# Now we prioritize the positions. Basically, when creating a player, we will place it in the
		# order of the lists below, which are divided by zone. Each zone has a
		# list of preferred positions in which the players will be assigned. 
		preferred_attack_positions = [ j[4],j[1],j[5],j[2],j[6],j[0],j[3] ]
		preferred_midfield_positions = [ j[10],j[11],j[14],j[7],j[9],j[12],j[15],j[8],j[13] ]
		preferred_defense_positions = [ j[18],j[19],j[16],j[21],j[17],j[20],j[22] ]

		# Now we create the attacking men. As many as defined in the selected formation, 
		# and according to the preferred position list.
		count = 0
		for position in range(0,men_per_zone[2]):
			man = player_pin(job = preferred_attack_positions[count])
			self.temporary_widgets.append(man)
			self.add_widget(man)
			preferred_attack_positions[count].is_taken = True
			count += 1

		# We do the same for midfield players
		count = 0
		for position in range(0,men_per_zone[1]):
			man = player_pin(job = preferred_midfield_positions[count])
			self.temporary_widgets.append(man)
			self.add_widget(man)
			preferred_midfield_positions[count].is_taken = True
			count += 1

		count = 0
		# We do the same for defense players
		for position in range(0,men_per_zone[0]):
			man = player_pin(job = preferred_defense_positions[count])
			self.temporary_widgets.append(man)
			self.add_widget(man)
			preferred_defense_positions[count].is_taken = True
			count += 1


#---------------------------------------------
# End of reviewed functions from main class
#---------------------------------------------




class checkRoll(ModalView):
	""" The checkRoll is a modal view that show s midfield, defense and attack checks. It creates a panel filled with widgets that scroll down into the screen, poping widgets. It also calculates the the check rolls and saves the game. Clicking on the ball icon will close and destroy the modal view."""

	def __init__(self, **kwargs):
		super(checkRoll,self).__init__(**kwargs)

		#self.mandingo_font = './data/fonts/MANDINGO.TTF'
		#self.brown = (0.56,0.64,0.35,1.0)#(0.22,0.46,0.03,1.0)
		#self.dark_brown = (0.24,0.31,0.16,1.0)
		#self.dark_gray = (0.4,0.4,0.4,1.0)
		#self.purple = (0.56,0.29,0.65,1.0)

		# So we easily access the main screen's parameters 
		self.main_screen = g.screens['main']

		# Ugly kivy.
		# To be able to slide a panel and have its children widgets follow it, kivy requires a weird
		# combination of widgets. We MUST give it a static background (self.background). Then we must
		# create a base relative layout, also to be static (self.relative_layout_base). We must then
		# create another relative layout to be the child of the first (self.rl).
		# This second layout is what we finally move, and all its widgets will follow along.
		# But this is a nasty ugly solution.

		self.background = './data/images/background-black.png'
		self.background_color = g.COLOR_BLACK_ALPHA_50
		self.relative_layout_base = RelativeLayout()
		self.rl = RelativeLayout(size_hint = (None,None),size = (360,640),pos = (0,640))

		self.relative_layout_base.add_widget(self.rl)
		self.add_widget(self.relative_layout_base)

		# Now we the widgets to the dynamic relative layout (self.rl). The values of many of these widgets
		# depend, of course, of the current action. So, before actually creating and adding the widgets,
		# we will figure out the values to give them.

		# Let's first define action dependent values: the title and the relevant zone strength
		if g.save.match['action'] == 'midfield':
			title_text = 'midfield check'
			str_friend = self.main_screen.zone_str['friend']['mid']
			str_foe = self.main_screen.zone_str['foe']['mid']
		elif g.save.match['action'] == 'defense':
			title_text = 'defense check'
			check_type = 'defense'
			str_friend = self.main_screen.zone_str['friend']['def']
			str_foe = self.main_screen.zone_str['foe']['atk']
		elif g.save.match['action'] == 'attack':
			title_text = 'attack check'
			check_type = 'attack'
			str_friend = self.main_screen.zone_str['friend']['atk']
			str_foe = self.main_screen.zone_str['foe']['def']
		else:
			title_text = 'error'
			str_friend = 0
			str_foe = 0

		# Then we decide the dice rolls. The first to for the user, the second two for the opponent.
		dice_result = [random.randint(0,5),random.randint(0,5),random.randint(0,5),random.randint(0,5)]

		# The final values for the checks.
		total_friend = str_friend+dice_result[0]+dice_result[1]
		total_foe = str_foe+dice_result[2]+dice_result[3]

		# And the conclusion message after the check.
		conclusion_text = 'error. no conclusion text'
		if total_friend>total_foe: # The user won the dispute
			if g.save.match['action'] == 'midfield':
				conclusion_text = 'you get to attack'
			if g.save.match['action'] == 'defense':
				conclusion_text = 'your defense won'
			if g.save.match['action'] == 'attack':
				conclusion_text = 'gooooal!'
		elif total_friend<total_foe: # The user lost the dispute
			if g.save.match['action'] == 'midfield':
				conclusion_text = 'you must defend'
			if g.save.match['action'] == 'defense':
				conclusion_text = 'shucks! they scored'
			if g.save.match['action'] == 'attack':
				conclusion_text = 'the attack failed'
		elif total_friend==total_foe: # The user had a tied
			if g.save.match['action'] == 'midfield':
				conclusion_text = 'no one attacks'
			if g.save.match['action'] == 'defense':
				conclusion_text = 'you dodged a bullet'
			if g.save.match['action'] == 'attack':
				conclusion_text = 'oh! that was close'
	
		# With the values ready, we now create the widgets. They are: a white background; a title label,two zone markers, two labels showing zone strength, 4 dice (just Image widgets), two result labels, plus and equal images for both user and opponent, the result message label and an arrow pointing to the button.

		self.animated_bg = Image( source='./data/images/interface-check-background.png', pos = (0,0) )
		self.title_label = Label(text=title_text,font_size='40sp',font_name=g.FONT_MANDINGO, color=g.COLOR_BROWN, pos = (0,282))
		self.zone_marker_friend = Image( source='./data/images/interface-check-str-mid.png', pos=(-74,196) )
		self.zone_marker_foe = Image( source='./data/images/interface-check-str-mid.png', pos=(74,196) )
		self.str_friend = Label(text=str(str_friend),font_size='40sp',font_name=g.FONT_MANDINGO, color=g.COLOR_BROWN_DARK, pos = (-75,194))
		self.str_foe = Label(text=str(str_foe),font_size='40sp',font_name=g.FONT_MANDINGO, color=g.COLOR_BROWN_DARK, pos = (75,194))
		self.die1_friend = Image( source='./data/images/interface-die-'+str(dice_result[0])+'.png', pos=(-74,102) )
		self.die1_foe = Image( source='./data/images/interface-die-'+str(dice_result[2])+'.png', pos=(74,102) )
		self.die2_friend = Image( source='./data/images/interface-die-'+str(dice_result[1])+'.png', pos=(-74,38) )
		self.die2_foe = Image( source='./data/images/interface-die-'+str(dice_result[3])+'.png', pos=(74,38) )
		self.result_label_friend = Label(text=str(str_friend+dice_result[0]+dice_result[1]),font_size='60sp',font_name=g.FONT_MANDINGO, color=g.COLOR_BROWN_DARK, pos = (-73,-56))
		self.result_label_foe = Label(text=str(str_foe+dice_result[2]+dice_result[3]),font_size='60sp',font_name=g.FONT_MANDINGO, color=g.COLOR_BROWN_DARK, pos = (73,-56))
		self.sign_plus_friend = Image( source='./data/images/interface-sign-plus.png', pos=(-24,37) )
		self.sign_plus_foe = Image( source='./data/images/interface-sign-plus.png', pos=(134,37) )
		self.sign_equal_friend = Image( source='./data/images/interface-sign-equal.png', pos=(-73,-9) )
		self.sign_equal_foe = Image( source='./data/images/interface-sign-equal.png', pos=(78,-9) )
		self.label_result = Label(text=conclusion_text,font_size='40sp',font_name=g.FONT_MANDINGO, color=g.COLOR_BROWN, pos = (0,-122))
		self.label_click = Label(text='click to continue',font_size='20sp',font_name=g.FONT_MANDINGO, color=g.COLOR_PURPLE, pos = (0,-167))
		self.sign_arrow = Image( source='./data/images/interface-check-arrow-down.png', pos=(-103,-217) )

		# And now we add all the gang to the dynamic relative layout.
		widgets_to_add = [ self.animated_bg, self.title_label, self.zone_marker_friend, self.zone_marker_foe, self.str_friend, self.str_foe, self.die1_friend, self.die1_foe, self.die2_friend, self.die2_foe, self.result_label_friend, self.result_label_foe, self.sign_equal_friend, self.sign_equal_foe, self.label_result, self.label_click, self.sign_arrow ]
		for widget in widgets_to_add:
			self.rl.add_widget(widget)

#		self.pop_list = [self.zone_marker_friend, self.str_friend, self.zone_marker_foe, self.str_foe, self.die1_friend, self.die1_foe, self.die2_friend, self.die2_foe, self.sign_plus_friend, self.sign_plus_foe, self.sign_equal_friend, self.sign_equal_foe, self.result_label_friend, self.result_label_foe, self.label_result, self.label_click, self.sign_arrow]
#		print 'o'
#		for widget in self.pop_list:
#			if widget.__class__ == Label:
#				widget.final_font_size = widget.font_size
#				widget.font_size = 0
#			else:
#				widget.final_size = widget.size[:]
#				widget.final_pos = [ widget.pos[0]+180-widget.final_size[0]/2,widget.pos[1]+320-widget.final_size[1]/2 ]
#				widget.size_hint = (None,None)
#				widget.size = (0,0)
#				widget.pos = [ widget.pos[0]+180,widget.pos[1]+320 ]
#
#
#		#Now we add the title label to the animated_bg, so it animates with it.
#		#The other widgets will pop afterwards.


		# Now we add the confirm button at the bottom of the screen. It mimics the 
		# ball button of the main_screen, but with a different behavior.
		# It is added to the static relative layout.
		self.confirm_button = Button( background_normal='./data/images/interface-circle-ball.png', background_down='./data/images/interface-circle-ball.png' )
		self.confirm_button.size_hint = (None,None)
		self.confirm_button.size = (160,140)
		self.confirm_button.pos = (180-80,0)

		self.confirm_button.bind(on_release = self.confirm_release)
		self.relative_layout_base.add_widget(self.confirm_button)

		# This will runs the pages animation, which means lowering the self.rl and its children,
		# and popping up widgets galore.
		self.animation_enter()
#--------------------------------------------------------------
		self.count = 0

		#self.animation_pop()
		#Clock.schedule_once(self.animation_pop, 1.2)
		#self.animation_pop() was uncommented

		#print 'list of widgets to animate',self.pop_list, len(self.pop_list)

	def confirm_release(self, btn_object):
		print 'button clicked'

	def animation_pop(self, lapsed_time = 0.0):
		print 'self.count',self.count
		self.count +=1
		if len(self.pop_list) > 0:
			print 'stuff is bigger than 0'
			widget = self.pop_list[0]
			#print 'animate widget',widget
			if widget.__class__ == Label:
				print 'this stuff is label'
				pop = Animation(font_size = widget.final_font_size, duration = 0.6, transition = 'out_back')
			else:
				print 'this stuff is not label'
				pop = Animation(size = widget.final_size, pos = widget.final_pos, duration = 0.6, transition = 'out_back')
			pop.start(widget)
			self.pop_list.remove(widget)
			#self.animation_pop()
			Clock.schedule_once(self.animation_pop, 0.12)
		else:
			print 'abracadabra'

	def animation_enter(self):
		enter_animation = Animation(pos = (0,0), duration = 4.0)
		enter_animation.start(self.rl)

	def animation_leave(self):
		leave_animation = Animation(pos = (0,-640))
		leave_animation.start(self.rl)





class zoneMarker(ButtonBehavior,Image):
	"""There are 6 zoneMarkers in the game, indicating the strength of the Defense, Midfield and Attack zones of each team. Besides informing how strong the zones are, they are clickable buttons that bring about popups informing about the cards attached to the zone and their effects."""
	def __init__(self,position,zone,**kwargs):
		super(zoneMarker, self).__init__(**kwargs)
		self.pos = position#(-150,215)
		self.size_hint = (None,None)
		self.size = (60,120)
		font_path = g.FONT_MANDINGO
		black = g.COLOR_BLACK
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
		

class Job:
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
		""""This __init__ functions defines necessary parameters for the men"""

		# Initialize the widget class
		super(player_pin, self).__init__()#**kwargs)

		# If the team is winning, losing or tied
		self.status_game = status_game

		# If the man is fatigued or healthy
		self.status_health = status_health

		# What is the man current job
		self.job_code = job.code

		# The job object that is currently associated to this player
		self.job_object = job

		# Prevent the player from accepting rotation and scaling input
		self.do_rotation = False
		self.do_scale = False

		# Define basic properties, like size and position
		self.size_hint = (None,None)
		self.size = (36,36)
		self.pos = job.position[0]+180-18,job.position[1]+320-18

		# Bind a function to on_touch_up, which is called either if the button is dragged or clicked
		self.bind(on_touch_up = self.on_release)
		
		# A stub that will receive the image.
		self.image = 'none'

		# Defines the image to be used based on the game status and the man's health
		self.reload_image()



	def reload_image(self):
		pass
		#"""This function will destroy the previous image loaded for the man, and load new one appropriate to the game status and the man's health, than blit it in the right position."""
		## If it still does not have a graphic representation, give it one
		#if self.image == 'none':
		#	self.image = Image(source='./data/images/player-'+self.status_game+'-'+self.status_health+'.png')
		#	self.image.pos = (0,0)
		#	self.image.size = (36,36)
		#	self.add_widget(self.image)
		## If it has graphical representation, update it
		#else:
		#	self.image.source = './data/images/player-'+self.status_game+'-'+self.status_health+'.png'


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

#---------------------------------------------
# Reviewed classes
#---------------------------------------------


class teamButton(Button):
	"""Creates a semi tranparent button with the team's crest, that will provide data from the team in question. It must either be called with the argument 'friend' or 'foe'. It loads a transparent creest, clipped by a stencilview. """

	def __init__(self,team_sides,**kwargs):
		super(teamButton,self).__init__(**kwargs)
		self.size_hint = (None,None)
		self.size = (120,120)
		self.image = None
		self.allow_stretch = False
		self.color = (1,1,1,0)
		self.background_normal = './data/images/btn_team_background.png'
		self.background_down = './data/images/btn_team_background_down.png'

		if team_sides == 'friend':
			self.pos = (0,0)
			image_source = './data/images/crest_'+g.save.status['crest']+'_big.png'
		elif team_sides == 'foe':
			self.pos = (240,0)
			image_source = './data/images/crest_'+g.save.match['opponent']+'_big.png'

		self.image = Image(source= image_source, size_hint=(None,None), size = (200,200), pos = [self.pos[0]-50,self.pos[1]-50], color = (1,1,1,0.5) )
		self.stencil_box = StencilView(size_hint=(None,None), size = (120,120), pos = self.pos)
		
		self.add_widget(self.stencil_box)
		self.stencil_box.add_widget(self.image)

	def on_released(self):
		print 'Clicked on team button.'


class circleButton(Button):
	"""This is the main button of the main screen. It is clicked when the player wants to proceed to the next action (stage) of the match, usually involving rolling checks. This button will also be used to confirm the result of checks (a pro forma command that basically lets the player close the checks modal windows, since at that point the save has already been commited)."""

	def __init__(self,**kwargs):
		"""This functions will create the button appearance and bind the on_releas method."""
		super(circleButton, self).__init__(**kwargs)
		self.background_normal='./data/images/interface-circle-ball.png'
		self.background_down='./data/images/interface-circle-ball.png'
		self.size_hint = (None,None)
		self.size = (160,140)
		self.pos = (100,0)
		self.bind(on_release = self.btn_release)

	def btn_release(self, marker_object):
		""" When the main button is clicked, it changes the stage (action) of the game, which will likely change the widgets. This functions deal with what happens when the button is clicked, which depends on what the current stage is.
		If pressed during...
		strategy stage: calls for the creation of secondary widgets and sets action to midfield.
		midfield stage: calls for a midfield check.
		defense stage: calls for a defense check.
		attack stage: calls for a attack check.
		counterattack stage: calls for a counterattack check.
		rebound stage: calls for a rebound check.
		counterattack_foe stage: calls for a counterattack check.
		rebound_foe stage: calls for a rebound check."""

		action = g.save.match['action']
		game_play = g.save.match['play']

		if action == 'strategy':
			# We create secondary widgets (a function of the main screen) and update action to 'midfield'.
			self.parent.create_secondary_widgets()
			g.save.match['action'] = 'midfield'

			# We also save the game.
			write_to_save()

		elif action == 'midfield':
			# We call for a midfield check. We place the modal as a child of main_screen (this button's parent).
			self.parent.midfield_check_modal = checkRoll()
			self.parent.add_widget(self.parent.midfield_check_modal)

		elif action == 'defense':
			pass
		elif action == 'attack':
			pass
		elif action == 'counterattack':
			pass
		elif action == 'counterattack_foe':
			pass
		elif action == 'rebound':
			pass
		elif action == 'rebound_foe':
			pass







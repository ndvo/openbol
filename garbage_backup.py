# ----------------------------------------
# from class mainScreen @ screen_main.py
# ----------------------------------------

	def pop_into_existance(self, widget, make_child = True, add_to_temp_list = True):
		"""This funtions will animate widgets poping into existance, and will also add them to parent self and to the temporary widget list, unless told otherwise."""
		final_size = widget.size[:]
		widget.size = (0,0)
		pop_duration = 1.0
		pop = Animation(size = final_size, duration = pop_duration, t = 'out_back')
		pop.start(widget)

		self.temporary_widgets.append(widget)
		self.add_widget(widget)

	def load_widgets_preparation(self):
		"""This function will load the widgets necessary for the preparation phase, in which the player will position their players in the field and activate positions."""
		#Now we create the positions markers (jobs) for the players. These are also permanent widgets
		font_path = './data/fonts/MANDINGO.TTF'
		black = (0,0,0,1)

		self.create_position_buttons() #Creates the positions (jobs) for the player pins

		self.team_score = Label( text=str(0), font_size='85sp', font_name='./data/fonts/MANDINGO.TTF', color=(1,1,1,1), pos = (-130,-260) ) #65sp
		self.opponent_score = Label( text=str(0), font_size='85sp', font_name='./data/fonts/MANDINGO.TTF', color=(1,1,1,1), pos = (130,-260) )

		zone_marker_foe = Image(source='./data/images/interface-zone-markers-foe.png',pos=(130+25, -40+180-8))
		self.str_atk_opp = Label(text=str(self.zone_str['foe']['atk']),font_size='40sp',font_name=font_path, color=black, pos = (155,260))
		self.str_mid_opp = Label(text=str(self.zone_str['foe']['mid']),font_size='40sp',font_name=font_path, color=black, pos = (155,135))
		self.str_def_opp = Label(text=str(self.zone_str['foe']['def']),font_size='40sp',font_name=font_path, color=black, pos = (155,9))


		self.temporary_widgets.append(self.team_score)
		self.temporary_widgets.append(self.opponent_score)
		self.temporary_widgets.append(zone_marker_foe)
		self.temporary_widgets.append(self.str_atk_opp)
		self.temporary_widgets.append(self.str_mid_opp)
		self.temporary_widgets.append(self.str_def_opp)

		self.add_widget(self.team_score)
		self.add_widget(self.opponent_score)
		self.add_widget(zone_marker_foe)
		self.add_widget(self.str_atk_opp)
		self.add_widget(self.str_mid_opp)
		self.add_widget(self.str_def_opp)

		self.deploy_players() #Automatically deploys players according to formation




	def prepare_layout(self):
		"""Unlike other screens, the main screen will change some aspects of its layout while it is still visible to the user. These changes occur according to g.save.match['action'], that basically defines what currently happening in the game. The possible answers are: strategy (equiping cards at the beginning of the match), preparation (equiping cards between two plays), defense, midfield, attack, counterattack, counterattack_against, rebound and free kick. Each actions also has a list of messages that are played on its startup. Widget placing is made by called outside functions, so they can be all called in sequence at the start of a loaded game."""
		action = g.save.match['action']

		if action == 'strategy':
			print 'prepare layout ran strategy'
			# Widget creation: creates card hand, zone markers and zone labels.
			# Allowed actions: cards can be equiped. 
			self.messages = [['MATCH PREPARATION','primary'],['CLICK THE BALL','secondary'],['WHEN YOU ARE READY','secondary'],['YOU SHOULD CHOOSE','tutorial'],['WHICH CARDS TO EQUIP','tutorial'],['PICK ONE FORMATION','tutorial'],['ONE TACTIC','tutorial'],['AND AS MANY SKILLS','tutorial'],['AS POSSIBLE','tutorial']]
			#Create card-box to receive player's cards
			self.load_widgets_strategy()

		elif action == 'preparation':
			print 'prepare layout ran preparation'
			# Widget creation: creates player positions and players, who are also placed in provisional positions.
			# Allowed actions: tactics and skill cards can be equiped, and players may be relocated.
			self.messages = [ ['PLAY X- PREPARATION','primary'],['CHOOSE POSITIONS','secondary'],['CLICK THE BALL','secondary'],['WHEN YOU ARE READY','secondary'],['YOU CAN REARRANGE THE MEN','tutorial'],['BY DRAGGING THEM','tutorial'],['TO NEW POSITIONS','tutorial'] ]
			self.load_widgets_preparation()
			#self.card_hand.get_available
			for card in self.card_hand.get_cards_by_type(card_state = 'all', card_type = 'formation'):
				card.switch_mode('blocked')

		elif action == 'defense':
			# Widget creation: none.
			# Allowed actions: positions may be activated.
			self.messages = [ ['PLAY X- DEFENSE','primary'],['YOU MAY TRY TO ACTIVATE POSITIONS','secondary'],['BY DRAGGING THE MEN','secondary'],['INTO THEIR OWN POSITIONS','secondary'], ['YOU ARE NOW UNDER ATTACK', 'tutorial'],  ['YOUR OPPONENT WILL SCORE UNLESS', 'tutorial'], ['YOU BEAT HIM IN A DEFENSE CHECK', 'tutorial'], ['AGAINST HIS ATTACK', 'tutorial'], ['TO HELP YOU OUT, YOU COULD', 'tutorial'], ['ACTIVATE DEFENSIVE POSITIONS', 'tutorial'], ['ESPECIALLY THE CENTER-BACKS (CB)', 'tutorial']]
	
		elif action == 'midfield':
			# Widget creation: none.
			# Allowed actions: positions may be activated.
			self.messages = [ ['PLAY X- MIDFIELD','primary'],['YOU MAY TRY TO ACTIVATE POSITIONS','secondary'],['BY DRAGGING THE MEN','secondary'],['INTO THEIR OWN POSITIONS','secondary'], ['ONCE PER PLAY YOU MUST TEST', 'tutorial'],  ['YOUR MIDFIELD ZONE', 'tutorial'], ['IF YOU WIN YOU MUST ATTACK', 'tutorial'], ['IF YOU LOSE YOU MUST DEFEND', 'tutorial'], ['BUT YOU CAN IMPROVE', 'tutorial'], ['YOUR CHANCES BY ACTIVATING', 'tutorial'], ['MIDFIELD POSITIONS, SUCH AS', 'tutorial'], ['CENTER-MIDFIELDERS (CM)', 'tutorial']]

		elif action == 'attack':
			# Widget creation: none.
			# Allowed actions: positions may be activated.
			self.messages = [ ['PLAY X- ATTACK','primary'],['YOU MAY TRY TO ACTIVATE POSITIONS','secondary'],['BY DRAGGING THE MEN','secondary'],['INTO THEIR OWN POSITIONS','secondary'],['GREAT! NOW YOU GET TO ATTACK','secondary'], ['YOU WILL MAKE AN ATTACK CHECK', 'tutorial'],  ["AGAINST YOUR OPPONENT'S DEFENSE", 'tutorial'], ['IF YOU WIN, YOU SCORE A GOAL', 'tutorial'] ]


	def load_messages(self, time_elapsed = 0):
		"""This function will sort out which messages are relevant and call them through recursive calling."""

		if self.interrupt_messages == True:
			#This allows us to shut the messages when needed.
			self.messages = []
			self.interrupt_messages = False

		if len(self.messages) >0:
			#We can only load messages if there are messages to load.

			message = self.messages[0]
			if message[1] == 'tutorial' and g.save.tournament['id'] != '3rd-div':
				# Message irrelevant. Ignore it and load the next one.
				self.messages.remove(message)
				self.load_messages()
			else:
				#Message relevant. Print it on screen and load the next one in 2 seconds.
				self.messages.remove(message)
				message_label = labelMessage(message = message[0], relevance = message[1])
				self.add_widget(message_label)
				Clock.schedule_once(self.load_messages,2)

#		relevant_messages = []
#		for message in self.messages[self.stage]:
#			if message[1] == 'tutorial' and g.save.tournament['id'] != '3rd-div':
#				pass
#			else:
#				relevant_messages.append(message)
#
#		if self.msg_count < len(relevant_messages):
#			message = labelMessage(message = relevant_messages[self.msg_count][0], relevance = relevant_messages[self.msg_count][1])
#			self.add_widget(message)
#			self.msg_count += 1
#			Clock.schedule_once(self.load_messages,2)
#		else:
#			print 'end of messages' #from here



	def create_zone_markers(self):
		self.add_widget(zoneMarker(zone = 'attack', position = (0,475)))
		self.add_widget(zoneMarker(zone = 'midfield',source='./data/images/zone-midfield-left-normal.png', position = (0,355)))
		self.add_widget(zoneMarker(zone = 'defense',source='./data/images/zone-defense-left-normal.png', position = (0,235)))


#------------------------------------------
# Classes from screen_main.py
#------------------------------------------



class labelMessage(Label):
	"""This massages will be displayed throughout the game."""
	def __init__(self,message = 'THIS IS A TEXT MESSAGE', relevance = 'comment',**kwargs):
		super(labelMessage,self).__init__(**kwargs)
		self.text = message
		self.relevance = relevance # Can be 'primary', 'secondary', 'tutorial' or 'comment'.
		self.end_color = (0,0,1,1)


		#print 'message',message,'relevance',relevance
		if self.relevance == 'primary':
			self.color = (1,1,1,1)
			self.end_color = (0,0,0,.6)
		elif self.relevance == 'secondary':
			self.color = (1,1,1,1)
			self.end_color = (1,1,1,0)
		elif self.relevance == 'tutorial':
			self.color = (.91,0.93,0.82,1)
			self.end_color = (.91,0.93,0.82,0)
		elif self.relevance == 'comment':
			self.color = (0.71,0.73,0.62,1)
			self.end_color = (0.71,0.73,0.62,0)
		else:
			self.color = (0,0,1,1)
			self.end_color = (0,0,1,1)
			print 'wrong relevance tag'

		self.create_message()

	def create_message(self):

		self.font_size = 0
		self.font_name = './data/fonts/H.H. Samuel-font-defharo.ttf'
		#self.padding = (0,0)

		self.size = (0,0)

		##Ugly Kivy! We can't animate the label aligned by the left. As a workaround,
		##we need to know the positions and sizes of the label at different points of the animation...
		fake_label1 = Label(text = self.text, font_size = 32, font_name = self.font_name, pos = (180,100))
		fake_label1.texture_update()
		fake_label1.size = fake_label1.texture_size
		self.big_size = fake_label1.texture_size[0]

		fake_label2 = Label(text = self.text, font_size = 22, font_name = self.font_name, pos = (180,300))
		fake_label2.texture_update()
		fake_label2.size = fake_label2.texture_size
		self.small_size = fake_label2.texture_size[0]

		#self.pos = (self.big_size/2-180+20, 240-320+10)
		#self.final_pos = (self.small_size/2-180+20, 610-320+10)
		self.pos = (0, 240-320+10-7)
		self.final_pos = (0, 610-320+10-3)
		self.size = fake_label1.size
		self.final_size = fake_label2.size


		self.appear_animation()

	def appear_animation(self):
		self.texture_update()

		appear_duration = 0.3
		lasting_duration = 1.7

		animation = Animation(font_size = 32, duration = appear_duration, t='out_back')
		animation.start(self)
		Clock.schedule_once(self.float_animation, lasting_duration)

	def float_animation(self, time_elapsed):
		self.texture_update()

		float_duration = 15.0
		fade_duration = 3.0
		animation = Animation(pos = self.final_pos, duration = float_duration)
		animation &= Animation(size = self.final_size, duration = float_duration)
		animation &= Animation(font_size = 22, duration = float_duration/3, t = 'out_cubic')
		animation &= Animation(color = self.end_color, duration = fade_duration)
		animation.start(self)
		Clock.schedule_once(self.check_permanence, float_duration)

	def check_permanence(self, time_elapsed):
		self.texture_update()

		if self.relevance == 'primary':
			if self.parent.active_message != None:
				self.parent.remove_widget(self.parent.active_message)
			self.parent.active_message = self
		else:
			try:
				self.parent.remove_widget(self)
			except:
				print "IMPORTANT ERROR: non primary labels can't be removed from parent (is there a parent?)."
				print self
				print self.relevance
				print self.message




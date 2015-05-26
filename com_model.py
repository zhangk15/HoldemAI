#-*- coding: utf-8 -*-
import socket
import sys
import com_handle
from collections import deque

class game_link:
	def __init__(self, target_addr, self_addr):
		self.__target_addr = target_addr
		self.__self_addr = self_addr
		self.__sock = None
		self.__msg_queue = deque([])
	
	def __del__(self):
		#pass
		if self.__sock != None:
			self.__sock.close()
	
	def __send(self, msg):
		#print(bytes(msg, encoding = 'ascii'))
		try:
			self.__sock.send(bytes(msg)) #, encoding = 'ascii'))
		except socket.error as msg:
			print("cannot send!")
			print(msg)
			return

	def __recv(self):
		try:
			buf = self.__sock.recv(2048)
		except socket.error as msg:
			print("cannot recv!")
			print(msg)
			return ""
		return str(buf) #, encoding = 'ascii')

	def link_start(self):
		self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.__sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
		try:
			self.__sock.bind(self.__self_addr)
		except socket.error as meg:
			print(msg)
			print("Bind Error!!!")
			self.__sock.close()
			self.__sock = None
		try:
			self.__sock.connect(self.__target_addr)
		except socket.error as msg:
			print(msg)
			print("Connection Error!!!")
			self.__sock.close()
			self.__sock = None

		if self.__sock is None:
			print("cannot connect")
			return False
		return True

		
	def msg_reg(self, pid, pname):
		self.__send('reg: ' + str(pid) + ' ' + pname + ' \n')

	def msg_action(self, action):
		self.__send(action + '\n')
	
	def get_msg(self):
		if len(self.__msg_queue) == 0:
			raw_msg = self.__recv()
			#print('RAW_MSG:')
			#print(raw_msg)
			temp = com_handle.patten_head.findall(raw_msg)
			for one_msg in temp:
				self.__msg_queue.append(one_msg)

		if len(self.__msg_queue) != 0:
			return self.__msg_queue.popleft()
		else:
			return ('','','','')

class player_info:
	def __init__(self):
		self.reset((0, 0, 0))
		self.actions = []
		self.history = []

	def __str__(self):
		return str(self.pid) + ': ' + str(self.jetton) + ' ' + str(self.money) + str(self.actions)

	def reset(self, info):
		self.pid = int(info[0])
		self.jetton = int(info[1])
		self.money = int(info[2])
		self.bet = 0
		self.cards = []

	def add_action(self, action):
		if action == 'raise':
			pass
		self.actions.append(action)
		
class game_info:
	def __init__(self, pid, game_conn):
		self.reset()
		self.player_list = {}
		self.history = []
		self.__is_new_game = True
		self.self_id = pid
		self.game_conn = game_conn

	def reset(self):
		self.total = 0
		self.blind = 0
		self.call_jetton = 0
		self.min_raise = 0
		self.common_card = []
		
def game_seat(msg, game):
	player = player_info()
	seats = com_handle.patten_seat.findall(msg)
	for seat in seats:
		if self.__is_new_game:
			player.reset(seat)
			game.player_list[player.pid] = player
			player = player_info()
		else:
			game.player_list[int(seat[0])].reset(seat)
	
	self.__is_new_game = False

	for item in game.player_list.values():
		print(str(item))

def game_blind(msg, game):
	blinds = com_handle.get_bet(msg)
	game.blind == blinds[0][1]
	for one_blind in blinds:
		game.total += int(one_blind[1])

def game_get_card(msg, game):
	for card in msg:
		if len(msg) == 2:
			game.player_list[game.self_id].cards.append(card)
		else:
			game.common_card.append(card)

def game_player_info(msg, game):
	players = (com_handle.get_userinfo(msg))
	d_jetton = 0
	d_money = 0
	for player in players:
		d_money = game.player_list[int(player[0])].money - int(player[2])
		d_jetton = game.player_list[int(player[0])].jetton - int(player[1])

		game.player_list[int(player[0])].jetton = int(player[1])
		game.player_list[int(player[0])].money = int(player[2])
		game.player_list[int(player[0])].bet = int(player[3])
		game.player_list[int(player[0])].actions.append((player[4], d_money + d_jetton))
		print(game.player_list[int(player[0])])
	
	game.total = int(com_handle.patten_inquire_total.findall(msg)[0])
	print(msg)
	print(game.total)	
		
def game_action(msg, game):
	game_player_info(msg, game)
	#get action
	game.game_conn.msg_action('fold')
	pass

def game_showdown(msg, game):
	results = com_handle.patten_shutdown_rank.findall(msg)
	
	for one in results:
		game.paleyer_list[one[1]].history.append(one)

def game_pot_win(msg, game)
	winners = com_handle.get_bet(raw_msg[2])
	for winner in winners:
		game.history.append((int(winner[0]), int(winnner[1])))
	

game_func['seat'] = game_seat
game_func['blind'] = game_blind
game_func['hold'] = game_get_card
game_func['flop'] = game_get_card
game_func['turn'] = game_get_card
game_func['river'] = game_get_card
game_func['notify'] = game_player_info
game_func['inquire'] = game_action
game_func['showdown'] = game_show_down
game_func['pot-win'] = game_pot_win

def game_loop(game_conn, pid):
	game = game_info(pid, game_coon)

	raw_msg = game_conn.get_msg()
	while raw_msg[0] != 'game-over \n' or len(raw_msg[0]) == 0:
		game_func[raw_msg[1]](raw_msg[2], game)
	game.reset()

def main(argv):
	try:
		target_addr = (argv[1], int(argv[2]))
		self_addr = (argv[3], int(argv[4]))
		pid = argv[5]
	except IndexError:
		print("Wrong arg!")
		return

	game_conn = game_link(target_addr, self_addr)
	if not game_conn.link_start():
		print("Can't connect")
		return
	game_conn.msg_reg(pid, 'HL')
	print("Connected. Game will start soon!!!")	

	game_loop(game_conn, int(pid))
	'''raw_msg = game_conn.get_msg()
	while raw_msg[0] != 'game-over \n' or len(raw_msg[0]) == 0:
		print("seat:")
		print(com_handle.patten_seat.findall(raw_msg[2]))
		print('')
	
		raw_msg = game_conn.get_msg()
		print("blind:")
		#print(raw_msg)
		#print("result:")
		print(com_handle.get_bet(raw_msg[2]))
		print('')

		raw_msg = game_conn.get_msg()
		print("hold cards:")
		#print(raw_msg)
		#print('result:')
		print(com_handle.get_cards(raw_msg[2]))
		print('')

		raw_msg = game_conn.get_msg()
		while raw_msg[1] == 'inquire':
			print("users action:")
			#print(raw_msg)
			print(com_handle.get_userinfo(raw_msg[2]))
			game_conn.msg_action('all_in')
			print('')

			raw_msg = game_conn.get_msg()
		print("flop cards:")
		#print(raw_msg)
		print(com_handle.get_cards(raw_msg[2]))
		print('')
		
		raw_msg = game_conn.get_msg()
		while raw_msg[1] == 'inquire':
			print("users action:")
			#print(raw_msg)
			print(com_handle.get_userinfo(raw_msg[2]))
			game_conn.msg_action('all_in')
			print('')

			raw_msg = game_conn.get_msg()
		print("turn cards:")
		#print(raw_msg)
		print(com_handle.get_cards(raw_msg[2]))
		print('')
		
		raw_msg = game_conn.get_msg()
		while raw_msg[1] == 'inquire':
			print("users action:")
			#print(raw_msg)
			print(com_handle.get_userinfo(raw_msg[2]))
			game_conn.msg_action('all_in')
			print('')
			
			raw_msg = game_conn.get_msg()
		print("river cards:")
		#print(raw_msg)
		print(com_handle.get_cards(raw_msg[2]))
		print('')
		
		raw_msg = game_conn.get_msg()
		while raw_msg[1] == 'inquire':
			print("users action:")
			#print(raw_msg)
			print(com_handle.get_userinfo(raw_msg[2]))
			game_conn.msg_action('all_in')
			print('')
	
			raw_msg = game_conn.get_msg()
		print("shutdown:")
		#print(raw_msg)
		print(com_handle.get_cards(raw_msg[2]))
		print(com_handle.patten_shutdown_rank.findall(raw_msg[2]))
		print('')
	
		raw_msg = game_conn.get_msg()
		print("win:")
		#print(raw_msg)
		print(com_handle.get_bet(raw_msg[2]))
		print('')

		raw_msg = game_conn.get_msg()'''
	print("\nGame over!")

if __name__ == '__main__':
	main(sys.argv)

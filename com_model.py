#-*- coding: utf-8 -*-
import socket
import sys
import com_handle
import decision
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
		self.__send('reg: ' + str(pid) + ' ' + pname + ' need_notify \n')

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


#-----------------------------------------------------------------------------#

class player_info:
	def __init__(self):
		self.reset((0, 0, 0))
		self.actions = []
		self.history = []

	def __str__(self):
		return str(self.pid) + ': ' + str(self.jetton) + ' ' + str(self.money) + ' ' + str(self.bet) + ' '# + str(self.actions)

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
		
#-----------------------------------------------------------------------------#

class game_info:
	def __str__(self):
		result = ''
		result += 'players:\n'
		for player in self.player_list.values():
			result += '\tplayer ' + str(player) + '\n'
		result += 'blind: ' + str(self.blind) + '\n'
		result += 'call_jetton: ' + str(self.call_jetton) + '\n'
		result += 'min_raise: ' + str(self.min_raise) + '\n'
		result += 'self_card: ' + str(self.player_list[self.self_id].cards) + '\n'
		result += 'commnd_card: ' + str(self.common_card) + '\n'
		result += 'total: ' + str(self.total) + '\n'
		return result

	def __init__(self, pid, game_conn):
		self.player_list = {}
		self.opponents = set()
		self.history = []
		self.is_new_game = True
		self.self_id = pid		#self:player_list[self_id]
		self.game_conn = game_conn
		self.reset()

	def reset(self):
		self.total = 0
		self.blind = 0
		self.call_jetton = 0
		self.min_raise = 0
		self.common_card = []
		self.opponents = set(self.player_list.keys())

	def round_finished(self):
		self.call_jetton = self.blind
		self.min_raise = 2 * self.call_jetton
		
#-----------------------------------------------------------------------------#
#-----------------------------------------------------------------------------#
#-----------------------------------------------------------------------------#
		
def game_seat(msg, game):
	player = player_info()
	seats = com_handle.patten_seat.findall(msg)
	for seat in seats:
		if game.is_new_game:
			player.reset(seat)
			game.player_list[player.pid] = player
			game.opponents.add(player.pid)
			player = player_info()
		else:
			game.player_list[int(seat[0])].reset(seat)
	
	game_is_new_game = False

	for item in game.player_list.values():
		print(str(item))

def game_blind(msg, game):
	blinds = com_handle.get_bet(msg)
	print(blinds)

	game.blind = int(blinds[0][1])
	if len(blinds) > 1:
		game.blind *= 2

	for one_blind in blinds:
		game.total += int(one_blind[1])
	
	game.round_finished()

def game_get_card(msg, game):
	cards = com_handle.get_cards(msg)
	for card in cards:
		if len(cards) == 2:
			game.player_list[game.self_id].cards.append(card)
		else:
			game.round_finished()
			game.common_card.append(card)

	print(cards)

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

		game.min_raise = max(game.min_raise, d_money + d_jetton)
		game.call_jetton = max(game.call_jetton, int(player[3]))

		if player[4] == 'fold':
			game.opponents.discard(int(player[0]))
		print(game.player_list[int(player[0])])
	
	game.total = int(com_handle.patten_inquire_total.findall(msg)[0])
	print(game.total)	
		
def game_action(msg, game):
	game_player_info(msg, game)
	#get action
	result = decision.make_decision(game.player_list[game.self_id].cards, game.common_card, game)
	print("call_jetton: " + str(game.call_jetton))
	print("self.bet: " + str(game.player_list[game.self_id].bet))
	print(result)
	game.game_conn.msg_action(result)
	pass

def game_showdown(msg, game):
	results = com_handle.patten_shutdown_rank.findall(msg)
	
	for one in results:
		game.player_list[int(one[1])].history.append(one)

	print(results)

def game_pot_win(msg, game):
	winners = com_handle.get_bet(msg)
	for winner in winners:
		game.history.append((int(winner[0]), int(winner[1])))
	print(game.history)
	print(game)
	game.reset()
	
game_func = {}
game_func['seat'] = game_seat
game_func['blind'] = game_blind
game_func['hold'] = game_get_card
game_func['flop'] = game_get_card
game_func['turn'] = game_get_card
game_func['river'] = game_get_card
game_func['notify'] = game_player_info
game_func['inquire'] = game_action
game_func['showdown'] = game_showdown
game_func['pot-win'] = game_pot_win

def game_loop(game_conn, pid):
	game = game_info(pid, game_conn)

	raw_msg = game_conn.get_msg()
	while raw_msg[0] != 'game-over \n' or len(raw_msg[0]) == 0:
		print('\n' + raw_msg[1])
		print(game_func[raw_msg[1]])
		#try:
		game_func[raw_msg[1]](raw_msg[2], game)
		raw_msg = game_conn.get_msg()
		#except KeyError as msg:
		#	print("KeyError!!!!")
		#	print(msg)
		#	print(raw_msg)
		#	return 

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

	print("\nGame over!")

if __name__ == '__main__':
	main(sys.argv)

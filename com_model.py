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
		self.__send('check ' + action + '\n')
	
	def get_msg(self):
		raw_msg = self.__recv()
		print('RAW_MSG:')
		print(raw_msg)
		temp = com_handle.patten_head.findall(raw_msg)
		print('MEG_QUEUE_ADD:')
		for one_msg in temp:
			print(one_msg)
			self.__msg_queue.append(one_msg)

		if len(self.__msg_queue) != 0:
			return self.__msg_queue.popleft()
		else:
			return ('','','','')

def main(argv):
	#for arg in argv:
	#	print(arg)

	try:
		target_addr = (argv[1], int(argv[2]))
		self_addr = (argv[3], int(argv[4]))
	except IndexError:
		print("Wrong arg!")
		return

	game_conn = game_link(target_addr, self_addr)
	if not game_conn.link_start():
		print("Can't connect")
		return
	game_conn.msg_reg(argv[5], 'HL')
	print("Connected. Game will start soon!!!")	
	raw_msg = game_conn.get_msg()
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
		game_conn.msg_action('fold')
		print('')

		raw_msg = game_conn.get_msg()
	print("flop cards:")
	#print(raw_msg)
	print(com_handle.get_cards(raw_msg[2]))
	print('')

	raw_msg = game_conn.get_msg()
	print("turn cards:")
	#print(raw_msg)
	print(com_handle.get_cards(raw_msg[2]))
	print('')
		
	raw_msg = game_conn.get_msg()
	print("river cards:")
	#print(raw_msg)
	print(com_handle.get_cards(raw_msg[2]))
	print('')

	raw_msg = game_conn.get_msg()
	print("shutdown:")
	#print(raw_msg)
	print(com_handle.get_cards(raw_msg[2]))
	print(com_handle.patten_shutdown_rank.findall(raw_msg[2]))
	print('')

	raw_msg = game_conn.get_msg()
	print("win:")
	print(raw_msg)
	print(com_handle.get_bet(raw_msg[2]))
	print('')

	raw_msg = game_conn.get_msg()
	if raw_msg[0] == "game-over \n":
		print("\nGame over!")


if __name__ == '__main__':
	main(sys.argv)

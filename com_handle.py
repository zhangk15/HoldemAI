import re

__flag = re.I | re.M | re.S
patten_head = re.compile(r'(\w+)/\s+', __flag)
#patten_tail = re.compile(r'/(\1)\s+', __flag)

patten_seat = re.compile(r'\s*(\d)\s+(\d+)\s+(\d+)\s*', __flag)
patten_blind = re.compile(r'\s*(\d):\s*(\d)\s+(\d)\s*', __flag)
patten_card = re.compile(r'(SPADES|HEARTS|CLUBS|DIAMONDS)\s+([2-9]|10|J|Q|K|A)\s*', __flag)
patten_inquire = re.compile(r'(\d)\s+(\d+)\s+(\d+)\s+(\d+)\s+(blind|check|call|raise|all_in|fold)\s*', __flag)
patten_inquire_total = re.compile(r'total pot:\s*(\d+)\s*', __flag)
patten_shutdown_rank = re.compile(r'rank:\s*(SPADES|HEARTS|CLUBS|DIAMONDS)\s+([2-9]|10|J|Q|K|A)\s+(SPADES|HEARTS|CLUBS|DIAMONDS)\s+([2-9]|10|J|Q|K|A)\s+(HIGH_CARD|ONE_PAIR|TWO_PAIR|THREE_OF_A_KIND|STRAIGHT|FLUSH|FULL_HOUSE|FOUR_OF_A_KIND|STRAIGHT_FLUSH)\s*', __flag)
patten_pot_win = re.compile(r'(\d):\s*(\d+)\s+', __flag)

def get_msg(raw_msg):
	pass

def get_cards(raw_msg):
	return patten_card.findall(raw_msg)

def get_userinfo(raw_msg):
	return patten_inquire.findall(raw_msg)

def get_bet(raw_msg):
	return patten_blind.findall(raw_msg)



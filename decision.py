#!/usr/bin/env python
'''
Author: DY.HUST
Date: 2015-05-24
Email: ml_143@sina.com
'''

import random
import operator

HIGH_CARD   = 0
ONE_PAIR    = 1
TWO_PAIRS   = 2
THREE_KIND  = 3
STRAIGHT    = 4
FLUSH       = 5
FULL_HOUSE  = 6
FOUR_KIND   = 7
STRAIGHT_FLUSH = 8

card_map = {
        '2':0, '3':1, '4':2,
        '5':4, '6':5, '7':6,
        '8':7, '9':8, '10':8,
        'J':9, 'Q':10, 'K':11, 'A':12, }

rank_to_primer = {
        0:2, 1:3, 2:5,
        3:7, 4:11, 5:13,
        6:17, 7:19, 8:23,
        9:29, 10:31, 11:37, 12:41,
        }

suits_map = {
        'SPADES':1,
        'HEARTS':2,
        'CLUBS':4,
        'DIAMONDS':8 }

################################################################################

def is_suited(five_suits):
    return reduce(operator.and_, five_suits)

# The following functions assume that five cards is already sorted

def is_straight(five_ranks):
    if five_ranks[0]==0 and five_ranks[1]==1 and five_ranks[2]==2 and five_ranks[3]==3 and five_ranks[4]==12:
        return True
    for i in xrange(1, len(five_ranks)):
        if five_ranks[i] - five_ranks[i-1] != 1:
            return False
    return True

def is_four_kind(five_primers, product):
    if 0 == product % five_primers[1]**4:
        return True
    return False

def is_full_house(five_primers, product):
    if (0 == product % five_primers[0]**3 and 0 == product % five_primers[4]**2
            or 0 == product % five_primers[0]**2 and 0 == product % five_primers[4]**3):
        return True
    return False

def is_three_kind(five_primers, product):
    # assume that cards is not FOUR_KIND
    if 0 == product % five_primers[2]**3:
        return True
    return False

def is_two_pair(five_primers, product):
    # assume that cards is not FOUR_KIND or THREE_KIND
    if 0 == product % five_primers[1]**2 and 0 == product % five_primers[3]**2:
        return True
    return False

def is_one_pair(five_primers, product):
    # assume that cards is not FOUR_KIND or THREE_KIND or TOW_PAIR
    if 0 == product % five_primers[1]**2 or 0 == product % five_primers[3]**2:
        return True
    return False

################################################################################

def ranks_identify(five_cards):
    occurs = [0] * 13
    for num in five_cards:
        occurs[num] += 1

    three_ranks = []
    pair_ranks = []
    single_ranks = []
    for i in xrange(12, -1, -1):
        if 3 == occurs[i]:
            three_ranks.append(i)
        elif 2 == occurs[i]:
            pair_ranks.append(i)
        elif 1 == occurs[i]:
            single_ranks.append(i)
    return three_ranks + pair_ranks + single_ranks

################################################################################

def get_pattern(five_cards):
    if is_suited(five_cards[1]):
        if is_straight(five_cards[0]):
            return STRAIGHT_FLUSH
        else:
            return FLUSH

    if is_straight(five_cards[0]):
        return STRAIGHT

    five_primers = map(rank_to_primer.get, five_cards[0])
    product = reduce(operator.mul, five_primers)

    if is_four_kind(five_primers, product):
        return FOUR_KIND
    elif is_full_house(five_primers, product):
        return FULL_HOUSE
    elif is_three_kind(five_primers, product):
        return THREE_KIND
    elif is_two_pair(five_primers, product):
        return TWO_PAIRS
    elif is_one_pair(five_primers, product):
        return ONE_PAIR
    else:
        return HIGH_CARD

def pattern_compare(own, opponent):
    own_pattern = own[2]
    opp_pattern = opponent[2]
    if own_pattern != opp_pattern:
        return own_pattern - opp_pattern

    if STRAIGHT_FLUSH == own_pattern:
        return own[0][2] - opponent[0][2]
    elif FOUR_KIND == own_pattern:
        if own[0][2] != opponent[0][2]:
            return own[0][2] - opponent[0][2]
        else:
            return own[0][0] - opponent[0][0] + own[0][4] - opponent[0][4]
    elif HIGH_CARD == own_pattern:
        return cmp(own, opponent)
    else:
        return cmp( ranks_identify(own[0]), ranks_identify(opponent[0]) )

def test_compare(own):
    own_pattern = get_pattern(own)
    print own_pattern

    if STRAIGHT_FLUSH == own_pattern:
        print 'straight_flush', own[0][2]
    elif FOUR_KIND == own_pattern:
        print 'four_kind', own[0][2], own[0][0] + own[0][4]
    else:
        print ranks_identify(own[0])

def test_patter_and_compare():
    # pattern test
    straight_flush = ([0,1,2,3,12], [2,2,2,2,2])
    print get_pattern(straight_flush)
    #four_kind = ([1,1,1,1,2], [8,1,2,4,8])
    four_kind = ([1,2,2,2,2], [8,1,2,4,8])
    print get_pattern(four_kind)
    #full_house = ([1,1,1,2,2], [8,1,2,8,1])
    full_house = ([1,1,2,2,2], [8,1,2,8,1])
    print get_pattern(full_house)
    flush = ([1,2,3,4,6], [2,2,2,2,2])
    print get_pattern(flush)
    straight = ([1,2,3,4,5], [8,1,1,1,1])
    print get_pattern(straight)
    #three_kind = ([1,3,3,3,4], [8,1,2,4,8])
    #three_kind = ([1,1,1,3,4], [8,1,2,4,8])
    three_kind = ([1,2,4,4,4], [8,1,2,4,8])
    print get_pattern(three_kind)
    #two_pairs = ([1,2,2,3,3], [8,1,8,1,2])
    two_pairs = ([1,1,2,2,3], [8,1,8,1,2])
    #two_pairs = ([1,1,2,3,3], [8,1,8,1,2])
    print get_pattern(two_pairs)
    #one_pair = ([1,1,2,3,4], [8,1,8,1,2])
    one_pair = ([1,2,2,3,4], [8,1,8,1,2])
    #one_pair = ([1,2,3,3,4], [8,1,8,1,2])
    #one_pair = ([1,2,3,4,4], [8,1,8,1,2])
    print get_pattern(one_pair)
    high_card = ([1,3,4,6,7], [8,1,2,4,8])

    # compare test
    test_compare(straight_flush)
    test_compare(four_kind)
    test_compare(full_house)
    test_compare(flush)
    test_compare(straight)
    test_compare(three_kind)
    test_compare(two_pairs)
    test_compare(one_pair)

    # NOTICE: you should not call the patter_compare

################################################################################

def calc_value_table():
    import itertools
    import time
    print 'begin generating the table', time.time()
    total = []
    for five in itertools.combinations(range(52), 5):
        ranks = map(lambda x: x%13, five)
        suits = map(lambda x: 1<<(x/13), five)
        ranks.sort()
        pattern = get_pattern((ranks, suits))
        total.append( (ranks, suits, pattern) )

    print 'finish generating the table, begin sorting', time.time()
    total.sort(cmp=pattern_compare)
    print 'finish sorting the table, begin generating the value map', time.time()

    suited_map = {}
    unsuited_map = {}
    for index in xrange(len(total)):
        product = reduce(operator.mul, map(rank_to_primer.get, total[index][0]))
        if is_suited(total[index][1]):
            suited_map[product] = index
        else:
            unsuited_map[product] = index
    print 'finish generating the value map', time.time()
    return suited_map, unsuited_map

################################################################################

def transfer_raw_card(cards):
    return [(cards_map[x[1]], suits_map[x[0]]) for x in cards]

def random_card(hold):
    while True:
        card = (random.randint(0, 12), 1<<random.randint(0, 3))
        if not card in hold:
            return card

def choose_best_value(seven_cards, value_map):
    from itertools import combinations

    max_value = -1
    for five in combinations(seven_cards, 5):
        suited = five[0][1] & five[1][1] & five[2][1] & five[3][1] & five[4][1]
        product = (rank_to_primer[five[0][0]] * rank_to_primer[five[1][0]] * rank_to_primer[five[2][0]]
                    * rank_to_primer[five[3][0]] * rank_to_primer[five[4][0]])
        if suited:
            max_value = max(max_value, value_map[0][product])
        else:
            max_value = max(max_value, value_map[1][product]) 
    return max_value

def probability(start, public, opponent_num, value_map, iterate=500):
    public_num = len(public)
    total = []
    total = start + public + [ (-1,-1) for i in xrange(100-public_num) ]

    opponents = [-1] * opponent_num

    win = 0; tie = 0
    for iterator in xrange(iterate):
        for i in xrange(2+public_num, 7 + opponent_num*2):
            total[i] = random_card(total[:i])

        own = choose_best_value(total[:7], value_map)

        max_opp = -1
        for i in xrange(opponent_num):
            max_opp = max(max_opp, choose_best_value(total[2:7] + total[7+i:9+i], value_map))

        if own > max_opp:
            win += 1
        elif own == max_opp:
            tie += 1

    return float(win*2 + tie) / (iterate * 2)

if __name__ == '__main__':
    #test_patter_and_compare()

    #value_map = calc_value_table()
    import pickle
    #pickle.dump(value_map, open('value_map', 'wb'), 2)
    value_map = pickle.load(open('value_map', 'rb'))

    start = [(11, 1), (11, 2)]
    public = [(0, 1), (3, 4), (5, 8), (7, 4), (9, 8)]
    import time
    old_clock = time.clock()
    #print probability(start, [[4, 6, 8, 9, 11], [1, 2, 4, 8, 2]], value_map)
    print probability(start, [], 7, value_map)
    print time.clock() - old_clock
    old_clock = time.clock()

    print probability(start, public, 7, value_map)
    print time.clock() - old_clock


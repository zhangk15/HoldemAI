#!/usr/bin/env python
'''
Author: DY.HUST
Date: 2015-05-24
Email: ml_143@sina.com
'''

import random
import operator
import pickle
import logging

#------------------------------------------------------------------------------#
# global constant

HIGH_CARD   = 0
ONE_PAIR    = 1
TWO_PAIRS   = 2
THREE_KIND  = 3
STRAIGHT    = 4
FLUSH       = 5
FULL_HOUSE  = 6
FOUR_KIND   = 7
STRAIGHT_FLUSH = 8

rank_to_primer = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41]

#------------------------------------------------------------------------------#

def is_suited(cards):
    return (cards[0][1] & cards[1][1] & cards[2][1] & cards[3][1] & cards[4][1])

# The following functions assume that five cards is already sorted

def is_straight(cards):
    if (cards[0][0]==0 and cards[1][0]==1 and cards[2][0]==2 and cards[3][0]==3 and cards[4][0]==12):
        return True
    for i in xrange(1, 5):
        if cards[i][0] - cards[i-1][0] != 1:
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

#------------------------------------------------------------------------------#

def ranks_identify(cards):
    occurs = [0] * 13
    for i in range(5):
        occurs[cards[i][0]] += 1

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

#------------------------------------------------------------------------------#

def get_pattern(cards):
    if is_suited(cards):
        if is_straight(cards):
            return STRAIGHT_FLUSH
        else:
            return FLUSH

    if is_straight(cards):
        return STRAIGHT

    five_primers = ( rank_to_primer[cards[0][0]],
            rank_to_primer[cards[1][0]],
            rank_to_primer[cards[2][0]],
            rank_to_primer[cards[3][0]],
            rank_to_primer[cards[4][0]] )
    product = ( rank_to_primer[cards[0][0]]
            *rank_to_primer[cards[1][0]] 
            *rank_to_primer[cards[2][0]]
            *rank_to_primer[cards[3][0]]
            *rank_to_primer[cards[4][0]] )

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
    own_pattern = own[1]
    opp_pattern = opponent[1]
    if own_pattern != opp_pattern:
        return own_pattern - opp_pattern

    if STRAIGHT_FLUSH == own_pattern:
        return own[0][2][0] - opponent[0][2][0]
    elif FOUR_KIND == own_pattern:
        if own[0][2][0] != opponent[0][2][0]:
            return own[0][2][0] - opponent[0][2][0]
        else:
            return own[0][0][0] - opponent[0][0][0] + own[0][4][0] - opponent[0][4][0]
    elif HIGH_CARD == own_pattern:
        for i in range(5):
            if own[0][i][0] < opponent[0][i][0]:
                return -1
            elif own[0][i][0] > opponent[0][i][0]:
                return 1
        return 0
    else:
        return cmp( ranks_identify(own[0]), ranks_identify(opponent[0]) )
    
#------------------------------------------------------------------------------#
# test

def test_compare(cards):
    cards_pattern = get_pattern(cards)
    print cards_pattern

    if STRAIGHT_FLUSH == cards_pattern:
        print 'straight_flush', cards[2][0]
    elif FOUR_KIND == cards_pattern:
        print 'four_kind', cards[2][0], cards[0][0] + cards[4][0]
    else:
        print ranks_identify(cards)

def test_patter_and_compare():
    # pattern test
    straight_flush = ((0,2),(1,2),(2,2),(3,2),(12,2))
    print get_pattern(straight_flush)
    four_kind = ((1,8),(2,1),(2,2),(2,4),(2,8))
    print get_pattern(four_kind)
    full_house = ((1,8),(1,1),(2,2),(2,8),(2,1))
    print get_pattern(full_house)
    flush = ((1,2),(2,2),(3,2),(4,2),(6,2))
    print get_pattern(flush)
    straight = ((1,8),(2,1),(3,1),(4,1),(5,1))
    print get_pattern(straight)
    three_kind = ((1,8),(2,1),(4,2),(4,4),(4,8))
    print get_pattern(three_kind)
    two_pairs = ((1,8),(1,1),(2,8),(2,1),(3,2))
    print get_pattern(two_pairs)
    one_pair = ((1,8),(2,1),(2,8),(3,1),(4,2))
    print get_pattern(one_pair)
    high_card = ((1,8),(3,1),(4,2),(6,4),(7,8))
    print get_pattern(high_card)

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

#------------------------------------------------------------------------------#

def calc_and_dump_value_table():
    import itertools
    import time

    logging.info('Begin generating the value table. %f' % time.clock())
    total = []

    card_compare = lambda x, y: x[0] - y[0]
    for five in itertools.combinations(range(52), 5):
        cards = [ (five[0]%13, 1<<(five[0]/13)),
            (five[1]%13, 1<<(five[1]/13)),
            (five[2]%13, 1<<(five[2]/13)),
            (five[3]%13, 1<<(five[3]/13)),
            (five[4]%13, 1<<(five[4]/13)) ]
        cards.sort(card_compare)
        pattern = get_pattern(cards)
        total.append( (cards, pattern) )

    logging.info('finish generating the table, begin sorting. %f' % time.clock())
    total.sort(cmp=pattern_compare)

    logging.info('finish sorting the table, begin generating the value map. %f', time.clock())
    suited_map = {}
    unsuited_map = {}
    for index in xrange(len(total)):
        cards = total[index][0]
        product = ( rank_to_primer[cards[0][0]]
                *rank_to_primer[cards[1][0]] 
                *rank_to_primer[cards[2][0]]
                *rank_to_primer[cards[3][0]]
                *rank_to_primer[cards[4][0]] )

        if is_suited(cards):
            suited_map[product] = index
        else:
            unsuited_map[product] = index

    logging.info('finish generating the value map. %f' % time.clock())

    value_map = (suited_map, unsuited_map)
    pickle.dump(value_map, open('value_map', 'wb'), 2)

def calc_head_table(value_map, opponent_num, iterate=1000):
    head_table_suited = [[0]*13 for i in xrange(13)]
    head_table_unsuited = [[0]*13 for i in xrange(13)]

    for i in xrange(13):
        start = [(i, 1), (i, 2)]
        head_table_unsuited[i][i] = probability(start, [], opponent_num, value_map, iterate)

        for j in xrange(i+1, 13):
            start = [(i, 1), (j, 1)]
            head_table_suited[i][j] = probability(start, [], opponent_num, value_map, iterate)
            head_table_suited[j][i] = head_table_suited[i][j]

            start = [(i, 1), (j, 2)]
            head_table_unsuited[i][j] = probability(start, [], opponent_num, value_map, iterate)
            head_table_unsuited[j][i] = head_table_unsuited[i][j]

    return (head_table_suited, head_table_unsuited)

def dump_head_table(value_map, opponent_num, iterate=1000):
    old_clock = time.clock()
    head_table = []
    for i in xrange(1, 8):
        head_table.append( calc_head_table(value_map, i, iterate) )
        print time.clock() - old_clock

    pickle.dump(head_table, open('head_table', 'wb'), 2)

#------------------------------------------------------------------------------#

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    #calc_and_dump_value_table()
    calc_and_dump_value_table()
    #test_patter_and_compare()

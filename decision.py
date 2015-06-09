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
import itertools

#------------------------------------------------------------------------------#
# global constant

cards_map = {
        '2':0, '3':1, '4':2,
        '5':4, '6':5, '7':6,
        '8':7, '9':8, '10':8,
        'J':9, 'Q':10, 'K':11, 'A':12, }

rank_to_primer = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41]

suits_map = {
        'SPADES':1,
        'HEARTS':2,
        'CLUBS':4,
        'DIAMONDS':8 }

#------------------------------------------------------------------------------#

def transfer_raw_card(cards):
    return [(cards_map[x[1]], suits_map[x[0]]) for x in cards]

def random_card(hold):
    while True:
        card = (random.randint(0, 12), 1<<random.randint(0, 3))
        if not card in hold:
            return card

def choose_best_value(seven_cards, value_map):
    max_value = -1

    for five in itertools.combinations(seven_cards, 5):
        suited = five[0][1] & five[1][1] & five[2][1] & five[3][1] & five[4][1]
        product = (rank_to_primer[five[0][0]] * rank_to_primer[five[1][0]] * rank_to_primer[five[2][0]]
                    * rank_to_primer[five[3][0]] * rank_to_primer[five[4][0]])

        if suited:
            value = value_map[0].get(product, -1)
        else:
            value = value_map[1].get(product, -1)

        if -1 == value:
            logging.warning('There is a suit which do not match any pattern')
            #print len(value_map[0])
            #print len(value_map[1])
            #print five
            #raw_input()
            # TODO
    
        if value > max_value:
            max_value = value

    return max_value

def probability(start, public, opponent_num, value_map, iterate=1000):
    public_num = len(public)
    total = start + public + [ (-1,-1) for i in xrange(21-public_num) ]

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

#------------------------------------------------------------------------------#

class Evaluation:
    def __init__(self):
        self.E = 0.0
        self.win_per = 0.0
        self.odds = 0.0
        self.jetton = 0.0

#def calc_fold_probability(win_per, total_info):
def calc_fold_base(E):
    if E < 0.8:
        return 1.0
    elif E < 1.0:
        return 1.0 - (E-0.8)
    elif E < 1.1:
        return 0.8 - (E-1.0)*6.0
    elif E < 1.3:
        return 0.2 - (E-1.1)
    else:
        return 0.0

def calc_fold_probability(evaluation, total_info):
    if evaluation.E < 1.0:
        return 1
    else:
        return 0

    # calc the base probability 
    p = calc_fold_base(evaluation.E)

    # protect the jetton
    cost_rate = float(total_info.call_jetton) / evaluation.jetton
    if (evaluation.jetton > 2000 and cost_rate > 0.75 and 
            (evaluation.win_per < 0.3 or evaluation.E < 1.0)):
        p = 1.0

    if (0 == evaluation.current_round and evaluation.win_per > 0.5):
        p *= 0.85

    if (0 == evaluation.current_round and evaluation.win_per > 0.7):
        p *= 0.75

    if (3 == evaluation.current_round and evaluation.win_per < 0.3 and evaluation.E < 1.0):
        p *= 1.5

    return p

#def calc_call_probability(win_per, total_info):
def calc_call_probability(evaluation, total_info):
    if evaluation.bet > 1000:
        return 1.0

    if evaluation.E < 1.5:
        return 1.0
    elif evaluation.E < 2.5:
        return 1.0 - 0.5 * (evaluation.E - 1.5)
    else:
        return 0.5

#def calc_raise_jetton(win_per, total_info):
def calc_raise_jetton(E):
    if E < 1.0:
        return 1.0
    else:
        return E * 100

def make_probability_estimate(evaluation, total_info):
    own_info = total_info.player_list[total_info.self_id]

    evaluation.odds = float(total_info.total + total_info.call_jetton) / total_info.call_jetton
    odds_estimate = 0.25*len(total_info.opponents) + 1.75
    if odds_estimate > evaluation.E:
        evaluation.odds = odds_estimate
        print 'ESTIMATE: ', odds_estimate
    #evaluation.odds = max(evaluation.odds, 0.25*len(total_info.opponents)+1.75)
    evaluation.E = evaluation.win_per * evaluation.odds
    evaluation.jetton = own_info.jetton
    evaluation.bet = own_info.bet

    print 'DECISION: win_per:%f odds:%f E:%f total:%d call:%d' % (
            evaluation.win_per, 
            evaluation.odds, 
            evaluation.E, 
            total_info.total, 
            total_info.call_jetton)

    # make the strategy

    c = random.random()
    p = calc_fold_probability(evaluation, total_info)
    if c < p:
        return 'fold'

    c = random.random()
    p = calc_call_probability(evaluation, total_info)
    if c < p:
        return 'call'

    raise_jetton = calc_raise_jetton(evaluation.E)
    return 'raise ' + str(raise_jetton)

def make_decision(start, public, total_info):
    global value_map
    global head_table

    start = transfer_raw_card(start)
    public = transfer_raw_card(public)

    evaluation = Evaluation()

    if 0 == len(public):
        evaluation.current_round = 0
    elif 3 == len(public):
        evaluation.current_round = 1
    elif 4 == len(public):
        evaluation.current_round = 2
    elif 5 == len(public):
        evaluation.current_round = 3
    
    evaluation.win_per = probability(start, public, len(total_info.opponents), value_map)
    action = make_probability_estimate(evaluation, total_info) 

    return action

#------------------------------------------------------------------------------#

def decision_test():
    start = [(11, 4), (11, 1)]
    public = [(9, 4), (8, 1), (0, 8)]

    import time

    old_clock = time.clock()
    print 'probability', probability(start, [], 7, value_map, 1000)
    print time.clock() - old_clock

    old_clock = time.clock()
    print 'probability', probability(start, public, 7, value_map, 1000)
    print time.clock() - old_clock

    raw_start = [('SPADES', 'A'), ('HEARTS', 'K')]

    import com_model

    player = com_model.player_info()
    player.jetton   = 1950
    player.money    = 8000
    player.bet      = 50

    total_info = com_model.game_info(None, None)
    total_info.player_list  = { 8888:player }
    total_info.self_id      = 8888
    total_info.total        = 2000
    total_info.blind        = 50
    total_info.call_jetton  = 100
    total_info.min_raise    = 200
    total_info.common_card  = [('HEART', 'A'), ('HEART', 'K'), ('HEART', 'Q')]
    total_info.opponents    = [0] * 3

    make_decision(raw_start, [], total_info)

#------------------------------------------------------------------------------#

# load the static data
value_map = pickle.load(open('value_map', 'rb'))
head_table = pickle.load(open('head_table', 'rb'))

print len(value_map[0])
print len(value_map[1])

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    decision_test()

#------------------------------------------------------------------------------#

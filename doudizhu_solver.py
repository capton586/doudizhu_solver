# -*- coding: UTF-8 -*-
# Author: Tim Wu
# Author: Carl King


# 牌型枚举
class COMB_TYPE:
    PASS, SINGLE, PAIR, TRIPLE, TRIPLE_ONE, TRIPLE_TWO, FOURTH_TWO_ONES, FOURTH_TWO_PAIRS, STRIGHT, BOMB = range(10)


# 3-14 分别代表 3-10, J, Q, K, A
# 16, 18, 19 分别代表 2, little_joker, big_joker
# 将 2 与其他牌分开是为了方便计算顺子
# 定义 HAND_PASS 为过牌
little_joker, big_joker = 18, 19
HAND_PASS = {'type':COMB_TYPE.PASS, 'main': 0, 'component':[]}

# 牌的映射关系
def get_porker(input):
    vals = { '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14, '2': 16, 'Y': 18, 'Z': 19, 'j': 11, 'q': 12, 'k': 13, 'a': 14, '2': 16, 'y': 18, 'z': 19 }
    cards= input.split()
    pokers = []
    for card in cards:
        if vals.has_key(card):
            pokers.append(vals[card])
        else:
            return 0
    return pokers

def get_card(output):
    vals = { 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 10: '10', 11:'J', 12:'Q', 13:'K', 14:'A', 16:'2', 18:'Y', 19:'Z'}
    cards = []
    for poker in output:
        cards.append(vals[poker])
    return str(cards)

# 根据当前手牌，获取此牌所有可能出的牌型
# 牌型数据结构为 {牌类型，主牌，包含的牌}
# 同种牌类型可以通过主牌比较大小
# 为方便比较大小, 将顺子按照不同长度分为不同牌型
def get_all_hands(pokers):
    if not pokers:
        return []

    # 过牌
    combs = [HAND_PASS]

    # 获取每个点数的数目
    dic = counter(pokers)

    # 王炸
    if little_joker in pokers and big_joker in pokers:
        combs.append({'type':COMB_TYPE.BOMB, 'main': big_joker, 'component': [big_joker, little_joker]})

    # 非顺子, 非王炸
    for poker in dic:
        if dic[poker] >= 1:
            # 单张
            combs.append({'type':COMB_TYPE.SINGLE, 'main':poker, 'component':[poker]})

        if dic[poker] >= 2:
            # 对子
            combs.append({'type':COMB_TYPE.PAIR, 'main':poker, 'component':[poker, poker]})

        if dic[poker] >= 3:
            # 三带零
            combs.append({'type':COMB_TYPE.TRIPLE, 'main':poker, 'component':[poker, poker, poker]})
            for poker2 in dic:
                if ALLOW_THREE_ONE and dic[poker2] >= 1 and poker2 != poker:
                    # 三带一
                    combs.append({'type':COMB_TYPE.TRIPLE_ONE, 'main':poker, 'component': [poker, poker, poker, poker2]})
                if ALLOW_THREE_TWO and dic[poker2] >= 2 and poker2 != poker:
                    # 三带二
                    combs.append({'type':COMB_TYPE.TRIPLE_TWO, 'main':poker, 'component': [poker, poker, poker, poker2, poker2]})

        if dic[poker] == 4:
            # 炸弹
            combs.append({'type':COMB_TYPE.BOMB, 'main':poker, 'component': [poker, poker, poker, poker]})
            if ALLOW_FOUR_TWO:
                pairs = []
                ones = []
                for poker2 in dic:
                    if dic[poker2] == 1:
                        ones.append(poker2)
                    elif dic[poker2] == 2:
                        pairs.append(poker2)

                # 四带二单
                for i in range(len(ones)):
                    for j in range(i + 1, len(ones)):
                        combs.append({'type':COMB_TYPE.FOURTH_TWO_ONES, 'main':poker, \
                            'component':[poker, poker, poker, poker, ones[i], ones[j]]})

                # 四带二对
                for i in range(len(pairs)):
                    combs.append({'type':COMB_TYPE.FOURTH_TWO_ONES, 'main':poker, \
                        'component': [poker, poker, poker, poker, pairs[i], pairs[i]]})
                    for j in range(i + 1, len(pairs)):
                        combs.append({'type':COMB_TYPE.FOURTH_TWO_PAIRS, 'main':poker, \
                            'component': [poker, poker, poker, poker, pairs[i], pairs[i], pairs[j], pairs[j]]})

    # 所有顺子组合
    # 以 COMB_TYPE.STRIGHT * len(straight) 标志顺子牌型, 不同长度的顺子是不同的牌型
    for straight in create_straight(list(set(pokers)), 5):
        combs.append({'type':COMB_TYPE.STRIGHT * len(straight), 'main': straight[0], 'component': straight})

    # 返回所有可能的出牌类型
    return combs

# 根据出的牌，确定出牌类型,不符合出牌规则返回0
def get_hand(pokers):
    if not pokers:
        hand = [HAND_PASS]
        return hand
    # 王炸
    
    if little_joker in pokers and big_joker in pokers:
        hand = {'type':COMB_TYPE.BOMB, 'main': big_joker, 'component': [big_joker, little_joker]}
        return hand
    hand = {'component': pokers}
    dic = counter(pokers)

    for poker in dic:
        # 单张
        if len(pokers) == 1:
            hand['type'] = COMB_TYPE.SINGLE
            hand['main'] = pokers[0]
            return hand
        # 对子
        elif len(pokers) == 2 and dic[poker]==2:
            hand['type'] = COMB_TYPE.PAIR
            hand['main'] = pokers[0]
            return hand
        # 三带零
        elif len(pokers) == 3 and dic[poker]==3:
            hand['type'] = COMB_TYPE.TRIPLE
            hand['main'] = pokers[0]
            return hand
        elif len(pokers) == 4:
            # 三带一
            if dic[poker] == 3:
                hand['type'] = 9
                hand['main'] = poker
                return hand
            # 炸弹
            elif dic[poker] == 4:
                hand['type'] = 9
                hand['main'] = pokers[0]
                return hand
        elif len(pokers) >= 5:
            # 三带二
            if dic[poker] == 3:
                hand['type'] = COMB_TYPE.TRIPLE_TWO
                hand['main'] = poker
                return hand
            elif dic[poker] == 4:
                for poker2 in dic:
                    # 四带二单
                    if dic[poker2] == 1:
                        hand['type'] = COMB_TYPE.FOURTH_TWO_ONES
                        hand['main'] = poker
                        return hand
                    # 四带二对
                    elif dic[poker2] == 2:
                        hand['type'] = COMB_TYPE.FOURTH_TWO_PAIRS
                        hand['main'] = poker
                        return hand
    if len(pokers) >= 5:
        # 顺子
        straight=create_straight(list(set(pokers)), len(pokers))
        #出的牌不符合规则
        if len(straight) == 0:#修改下
            return 0
        hand['type'] = COMB_TYPE.STRIGHT * len(straight[0])
        hand['main'] = straight[0][0]
        return hand
    return 0

# 根据列表创建顺子
def create_straight(list_of_nums, min_length):
    a = sorted(list_of_nums)
    lens = len(a)
    for start in range(0, lens):
        for end in range(start, lens):
            if a[end] - a[start] != end - start:
                break
            elif end - start >= min_length - 1:
                yield list(range(a[start], a[end] + 1))



# 统计列表中每个元素的个数
def counter(pokers):
    dic = {}
    for poker in pokers:
        dic[poker] = pokers.count(poker)
    return dic



# comb1 先出，问后出的 comb2 是否能打过 comb1
# 1. 同种牌型比较 main 值, main 值大的胜
# 2. 炸弹大过其他牌型
# 3. 牌型不同, 后出为负
def can_beat(comb1, comb2):
    if not comb2 or comb2['type'] == COMB_TYPE.PASS:
        return False

    if not comb1 or comb1['type'] == COMB_TYPE.PASS:
        return True

    if comb1['type'] == comb2['type']:
        return comb2['main'] > comb1['main']
    elif comb2['type'] == COMB_TYPE.BOMB:
        return True
    else:
        return False



# 给定 pokers，求打出手牌 hand 后的牌
# 用 component 字段标志打出的牌, 可以方便地统一处理
def make_hand(pokers, hand):
    poker_clone = pokers[:]
    for poker in hand['component']:
        if poker in poker_clone:
            poker_clone.remove(poker)
        else:
            return 0
    return poker_clone



# 模拟每次出牌, my_pokers 为当前我的牌, enemy_pokers 为对手的牌
# last_hand 为上一手对手出的牌, cache 用于缓存牌局与胜负关系
def hand_out(my_pokers, enemy_pokers, last_hand = None, cache = {}):
    # 牌局终止的边界条件
    if not my_pokers:
        return True
        
    if not enemy_pokers:
        return False
        
    # 如果上一手为空, 则将上一手赋值为 HAND_PASS
    if last_hand is None:
        last_hand = HAND_PASS

    # 从缓存中读取数据
    key = str((my_pokers, enemy_pokers, last_hand['component']))
    if key in cache:
        return cache[key]

    # 模拟出牌过程, 深度优先搜索, 找到赢的分支则返回 True
    for current_hand in get_all_hands(my_pokers):
        # 转换出牌权有两种情况: 
        # 1. 当前手胜出, 则轮到对方选择出牌
        # 2. 当前手 PASS, 且对方之前没有 PASS, 则轮到对方出牌
        if can_beat(last_hand, current_hand) or \
        (last_hand['type'] != COMB_TYPE.PASS and current_hand['type'] == COMB_TYPE.PASS):
            if not hand_out(enemy_pokers, make_hand(my_pokers, current_hand), current_hand, cache):
                #print(True,' :', key)
                cache[key] = True
                return cache

    # 遍历所有情况, 均无法赢, 则返回 False
    # print(False, ':', key)
    cache[key] = False
    return False


# todo:
# 1. 用出牌列表作为 last_hand 的值, 方便调用函数


if __name__ == '__main__':


    # 残局1
    # 是否允许三带一
    ALLOW_THREE_ONE = True
    # 是否允许三带二
    ALLOW_THREE_TWO = True
    # 是否允许四带二
    ALLOW_FOUR_TWO = True
    # 3-14 分别代表 3-10, J, Q, K, A
    # 16, 18, 19 分别代表 2, little_joker, big_joker
    # 将 2 与其他牌分开是为了方便计算顺子
    # 定义 HAND_PASS 为过牌
    while True:
        cache={}
        #输入扑克牌，不区分大小写，y 或Y 代表little_joker，z 或Z 代表big_joker
        print 'Input porkes,\'y\' or \'Y\' is little_joker, \'z\' or \'Z\' is big_joker'
        while True:
            playerA = raw_input('lord porker:')
            lord = get_porker(playerA)
            if lord ==0:
                print "Error,don't exit the porker,please try again"
            elif len(lord)==0:
                print "Pleas input the Porkers"
            else:
                break
        while True:
            playerB = raw_input('farmer porker:')
            farmer = get_porker(playerB)
            if farmer ==0:
                print "Error,don't exit the porker,please try again"
            elif len(farmer)==0:
                print "Pleas input the Porkers"
            else:
                break
        
        print
        print 'Computing the result,please wait...'
        cache = hand_out(lord, farmer)
        if cache ==False:
            print 'The farmer will Win!please input again' 
        else:
            print 'The Lord will Win!'
            print
            last_hand = HAND_PASS
            lord_hand = HAND_PASS
            while len(lord) != 0:
                for current_hand in get_all_hands(lord):
                    if can_beat(last_hand, current_hand) or \
                    (last_hand['type'] != COMB_TYPE.PASS and current_hand['type'] == COMB_TYPE.PASS):
                        if not hand_out(farmer, make_hand(lord, current_hand), current_hand,cache):
                            #print(True,' :', key)
                            #cache[key] = True
                            lord = make_hand(lord,current_hand)
                            lord_hand = current_hand
                            print 'lord porkers: '+get_card(lord)
                            print 'lord:'+get_card(current_hand['component'])
                            print 'farmer porkers: '+ get_card(farmer)
                            break
                if len(lord) == 0:
                    print
                    print 'Lord win!'
                    break
                while True:
                    input = raw_input('farmer:')
                    if input =='':
                        last_hand = HAND_PASS
                        break
                    else:    
                        pokers = get_porker(input)
                        # 检查扑克中是否有这张牌
                        if pokers == 0:
                            print "Error,don't exit the porker,please try again"
                        else:
                            last_hand = get_hand(pokers)
                            result = last_hand
                            # 检查出牌的类型否符合COMB_TYPE:
                            if last_hand ==0:
                                print 'Error,your porker(s) doesn\'t conform to the rules,please try again or edit the rules'
                            # 检查出的牌是否是farmer拥有的牌
                            elif make_hand(farmer, last_hand) == 0:
                                print 'Error,you don\'t have the porker(s),check it and try again'
                            #检查出的牌是否能大于lord的牌
                            elif not can_beat(lord_hand, last_hand):
                                print 'Error,your porker(s) can\'t beat the lord\'s,please try again'
                            else:
                                farmer = make_hand(farmer, last_hand)
                                break
                        


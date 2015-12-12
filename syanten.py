#!/usr/bin/python
#coding=utf-8
import copy, argparse, random, sys

class pai:
  PAI_TYPE = ['0萬', '1萬', '2萬', '3萬', '4萬', '5萬', '6萬', '7萬', '8萬', '9萬', '0筒', '1筒', '2筒', '3筒', '4筒', '5筒', '6筒', '7筒', '8筒', '9筒', '0索', '1索', '2索', '3索', '4索', '5索', '6索', '7索', '8索', '9索', '_裏', '_東', '_南', '_西', '_北', '_白', '_發', '_中']
  NULL_PAI = 40
  FLOWER_TYPE = ['_春', '_夏', '_秋', '_冬', '_梅', '_蘭', '_菊', '_竹']
  THIRTEEN_SET = [1, 9, 11, 19, 21, 29, 31, 32, 33, 34, 35, 36, 37]
  def __init__(self, array):
    if isinstance(array[0], int):
      self.tehai = array
    elif isinstance(array[0], str):
      self.tehai = [0] * 38
      invstr = [array[len(array)-i-1] for i in range(len(array)) if array[len(array)-i-1] in '0123456789mpszMPSZ']
      offset = pai.NULL_PAI
      for char in invstr:
        if char == 'm' or char == 'M':
          offset = 0
        elif char == 'p' or char == 'P':
          offset = 10
        elif char == 's' or char == 'S':
          offset = 20
        elif char == 'z' or char == 'Z':
          offset = 30
        elif int(char) + offset < 38:
          self.tehai[int(char) + offset] += 1

  def pai_print(self):
    self.pai_array = ''
    for i in range(len(self.tehai)):
      self.pai_array += (pai.PAI_TYPE[i] + ' ') * self.tehai[i]

  tehai = [0] * 38
  pai_array = ''
  tempTehai = [0] * 38
  red5manCount = 0
  red5pinCount = 0
  red5souCount = 0

  n_eval = 0
  fixed_mentsu_suu = 0
  jantou = 0
  koutsu_suu = 0
  shuntsu_suu = 0
  koutsu = [0] * 4
  shuntsu = [0] * 4
  koritsu = 0 #bit expression
  n4 = 0 #bit expression
  kanzen_koutsu_suu = 0
  kanzen_shuntsu_suu = 0
  kanzen_toitsu_check = 0
  kanzen_koritsu_suu = 0
  syanten_temp = 8
  syanten_normal = 8
  syanten_seven = 6
  syanten_thirteen = 13
  #sequence: head, triples, sequences
  winhand_breakdown = [] #added for win hand break down output
  winhand_string = ''
  effective_string = ''

  def checkReddora(self):
    self.red5manCount = 0
    self.red5pinCount = 0
    self.red5souCount = 0
    if (self.tehai[0]):
      self.red5manCount += self.tehai[0]
    if (self.tehai[10]):
      self.red5pinCount += self.tehai[10]
    if (self.tehai[20]):
      self.red5souCount += self.tehai[0]

  def moveReddora(self):
    if (self.red5manCount):
      self.tehai[5] += self.tehai[0]
      self.tehai[0] = 0
    if (self.red5pinCount):
      self.tehai[15] += self.tehai[10]
      self.tehai[10] = 0
    if (self.red5souCount):
      self.tehai[25] += self.tehai[20]
      self.tehai[20] = 0

  def syantenCheck(self):
    self.fixed_mentsu_suu = int((14 - sum(self.tehai)) / 3)
    self.tempTehai = copy.deepcopy(self.tehai)
    self.toitsu_suu = 0
    self.mentsu_suu = 0
    self.taatsu_suu = 0
    self.syanten_temp = 0
    self.syanten_suu = 8 - 2 * self.fixed_mentsu_suu
    self.winhand_breakdown = [] #added for win hand break down output
    self.jantou = 0
    self.koutsu_suu = 0
    self.shuntsu_suu = 0
    self.koutsu = [pai.NULL_PAI] * 4
    self.shuntsu = [pai.NULL_PAI] * 4
    self.koritsu = 0
    self.extractCount = 0
    for i in range(30): #avoid 5th pair wait
      if self.tehai[i] == 4: self.n4 |= 1 << i

    #independent triples, sequences and tiles check, can remove?
    self.koutsu_suu = self.KanzenKoutsuCheck()
    self.shuntsu_suu = self.KanzenShuntsuCheck()
    self.mentsu_suu = self.koutsu_suu + self.shuntsu_suu + self.fixed_mentsu_suu
    self.n_eval = 0
    self.extract(1)
    return self.syanten_suu

  def extract(self, depth):
    self.n_eval += 1
    while (not self.tempTehai[depth] and depth < 30): depth += 1
    if depth == 30:
      if self.toitsu_suu:
        effective_taatsu_suu = min(4-self.mentsu_suu, self.taatsu_suu+self.toitsu_suu-1)
        self.syanten_temp = 7 - self.mentsu_suu*2 - effective_taatsu_suu
        if self.mentsu_suu == 3 and self.taatsu_suu == 0 and self.toitsu_suu == 1 and self.koritsu == 0: self.syanten_temp += .5 #virtual mode, no single tile for tatsu
      else:
        self.syanten_temp = 8 - self.mentsu_suu*2 - min(4-self.mentsu_suu, self.taatsu_suu)
        if not self.koritsu & ~(self.n4): self.syanten_temp += .5 #virtual mode, no pair wait
        elif self.mentsu_suu == 3 and self.taatsu_suu == 0 and bin(self.koritsu).count('1') == 1: self.syanten_temp += .5 #virtual mode, no single tile for tatsu
      if self.syanten_temp < self.syanten_suu: self.syanten_suu = self.syanten_temp
    i = depth % 10
    if self.tempTehai[depth] == 4:
      #triple + sequence/tatsu/single
      self.add_triple(depth)
      if i < 8 and self.tempTehai[depth+2]:
        if self.tempTehai[depth+1]: #sequence
          self.add_sequence(depth)
          self.extract(depth+1)
          self.del_sequence(depth)
        self.add_tatsu_close(depth) #close wait, can add "else"?
        self.extract(depth+1)
        self.del_tatsu_close(depth)
      if i < 9 and self.tempTehai[depth+1]: #open or end wait
        self.add_tatsu_open(depth)
        self.extract(depth+1)
        self.del_tatsu_open(depth)
      self.add_single(depth) #single
      self.extract(depth+1)
      self.del_single(depth)
      self.del_triple(depth)
      #pair + sequence/..., no duplicated pairs
      self.add_pair(depth)
      if i < 8 and self.tempTehai[depth+2]:
        if self.tempTehai[depth+1]: #sequence
          self.add_sequence(depth)
          self.extract(depth+1)
          self.del_sequence(depth)
        self.add_tatsu_close(depth) #close wait
        self.extract(depth+1)
        self.del_tatsu_close(depth)
      if i < 9 and self.tempTehai[depth+1]: #open or end wait
        self.add_tatsu_open(depth)
        self.extract(depth+1)
        self.del_tatsu_open(depth)
      self.del_pair(depth)
    elif self.tempTehai[depth] == 3:
      #triple only
      self.add_triple(depth)
      self.extract(depth+1)
      self.del_triple(depth)
      #pair + sequence/tatsu
      self.add_pair(depth)
      if i < 8 and self.tempTehai[depth+1] and self.tempTehai[depth+2]: #sequence
        self.add_sequence(depth)
        self.extract(depth+1)
        self.del_sequence(depth)
      else:
        if i < 8 and self.tempTehai[depth+2]:
          self.add_tatsu_close(depth) #close wait
          self.extract(depth+1)
          self.del_tatsu_close(depth)
        if i < 9 and self.tempTehai[depth+1]:
          self.add_tatsu_open(depth)
          self.extract(depth+1)
          self.del_tatsu_open(depth)
      self.del_pair(depth)
      #sequences
      if i < 8 and self.tempTehai[depth+1] >= 2 and self.tempTehai[depth+2] >= 2:
        self.add_sequence(depth)
        self.add_sequence(depth)
        self.extract(depth+1)
        self.del_sequence(depth)
        self.del_sequence(depth)
    elif self.tempTehai[depth] == 2:
      #pair
      self.add_pair(depth)
      self.extract(depth+1)
      self.del_pair(depth)
      #sequence...
      if i < 8 and self.tempTehai[depth+1] and self.tempTehai[depth+2]:
        self.add_sequence(depth)
        self.extract(depth)
        self.del_sequence(depth)
    elif self.tempTehai[depth] == 1:
      if i < 7 and self.tempTehai[depth+1] == 1 and self.tempTehai[depth+2]: #lengthened pair wait
        self.add_sequence(depth)
        self.extract(depth+2)
        self.del_sequence(depth)
      else:
        self.add_single(depth)
        self.extract(depth+1)
        self.del_single(depth)
        #sequence...
        if i < 8 and self.tempTehai[depth+2]:
          if self.tempTehai[depth+1]: #sequence
            self.add_sequence(depth)
            self.extract(depth+1)
            self.del_sequence(depth)
          self.add_tatsu_close(depth) #close wait
          self.extract(depth+1)
          self.del_tatsu_close(depth)
        if i < 9 and self.tempTehai[depth+1]: #open or end wait
          self.add_tatsu_open(depth)
          self.extract(depth+1)
          self.del_tatsu_open(depth)

  def add_triple(self, k):
    self.tempTehai[k] -= 3
    self.mentsu_suu += 1
  def del_triple(self, k):
    self.tempTehai[k] += 3
    self.mentsu_suu -= 1

  def add_pair(self, k):
    self.tempTehai[k] -= 2
    self.toitsu_suu += 1
  def del_pair(self, k):
    self.tempTehai[k] += 2
    self.toitsu_suu -= 1

  def add_sequence(self, k):
    self.tempTehai[k] -= 1
    self.tempTehai[k+1] -= 1
    self.tempTehai[k+2] -= 1
    self.mentsu_suu += 1
  def del_sequence(self, k):
    self.tempTehai[k] += 1
    self.tempTehai[k+1] += 1
    self.tempTehai[k+2] += 1
    self.mentsu_suu -= 1

  def add_tatsu_open(self, k):
    self.tempTehai[k] -= 1
    self.tempTehai[k+1] -= 1
    self.taatsu_suu += 1
  def del_tatsu_open(self, k):
    self.tempTehai[k] += 1
    self.tempTehai[k+1] += 1
    self.taatsu_suu -= 1

  def add_tatsu_close(self, k):
    self.tempTehai[k] -= 1
    self.tempTehai[k+2] -= 1
    self.taatsu_suu += 1
  def del_tatsu_close(self, k):
    self.tempTehai[k] += 1
    self.tempTehai[k+2] += 1
    self.taatsu_suu -= 1

  def add_single(self, k):
    self.tempTehai[k] -= 1
    self.koritsu |= 1 << k
  def del_single(self, k):
    self.tempTehai[k] += 1
    self.koritsu &= ~(1 << k)

  def find_winhand(self): #together with quick win hand judgment
    for i in range(31, 38):
      if self.tehai[i] == 1 or self.tehai[i] == 4: return
    self.fixed_mentsu_suu = int((14 - sum(self.tehai)) / 3)
    self.tempTehai = copy.deepcopy(self.tehai)
    self.mentsu_suu = 0
    self.koutsu_suu = 0
    self.shuntsu_suu = 0
    self.koutsu = [pai.NULL_PAI] * 4
    self.shuntsu = [pai.NULL_PAI] * 4
    #independent triples, sequences and tiles check
    self.n_eval = 0
    head = pai.NULL_PAI
    #sum of mentsu is always multiples of 3
    sum_m = 2 * (self.tehai[1] + self.tehai[4] + self.tehai[7]) + (self.tehai[2] + self.tehai[5] + self.tehai[8])
    sum_p = 2 * (self.tehai[11] + self.tehai[14] + self.tehai[17]) + (self.tehai[12] + self.tehai[15] + self.tehai[18])
    sum_s = 2 * (self.tehai[21] + self.tehai[24] + self.tehai[27]) + (self.tehai[22] + self.tehai[25] + self.tehai[28])
    if sum(self.tehai[1:10]) % 3 == 2:
      head = (sum_m + 2) % 3 + 1
      sum_m = sum_m - head
    elif sum(self.tehai[11:20]) % 3 == 2: 
      head = (sum_p + 2) % 3 + 11
      sum_p = sum_p - (head-10)
    elif sum(self.tehai[21:30]) % 3 == 2: 
      head = (sum_s + 2) % 3 + 21
      sum_s = sum_s - (head-20)
    else:
      for i in range(31, 38):
        if self.tehai[i] == 2:
          head = i
          break
    if sum_m % 3 or sum_p % 3 or sum_s % 3 or head == pai.NULL_PAI: return
    self.koutsu_suu = self.KanzenKoutsuCheck()
    self.shuntsu_suu = self.KanzenShuntsuCheck()
    self.mentsu_suu = self.koutsu_suu + self.shuntsu_suu + self.fixed_mentsu_suu
    if head > 30:
      self.jantou = head
      self.tempTehai[head] -= 2
      self.mentsu_cut(1)
    else:
      for i in range(3):
        #all possible heads are of the same kinds and congruence modulo of 3
        self.jantou = head+3*i
        if self.tempTehai[self.jantou] >= 2:
          self.tempTehai[self.jantou] -= 2
          self.mentsu_cut(1)
          self.tempTehai[self.jantou] += 2

  def mentsu_cut(self, depth):
    while (not self.tempTehai[depth] and depth < 30): depth += 1
    if depth == 30:
      if self.mentsu_suu == 4:
        winarray = [self.jantou] + sorted(self.koutsu) + sorted(self.shuntsu)
        if winarray not in self.winhand_breakdown: self.winhand_breakdown.append(winarray)
    i = depth % 10
    if i < 8 and self.tempTehai[depth] == 4 and self.tempTehai[depth+1] and self.tempTehai[depth+2]:
      #triple + sequence
      self.add_triple(depth)
      self.koutsu[self.koutsu_suu] = depth
      self.koutsu_suu += 1
      self.add_sequence(depth)
      self.shuntsu[self.shuntsu_suu] = depth
      self.shuntsu_suu += 1
      self.mentsu_cut(depth+1)
      self.del_sequence(depth)
      self.shuntsu_suu -= 1
      self.shuntsu[self.shuntsu_suu] = pai.NULL_PAI
      self.del_triple(depth)
      self.koutsu_suu -= 1
      self.koutsu[self.koutsu_suu] = pai.NULL_PAI
      #four identical sequences
      if self.tempTehai[depth+1] == 4 and self.tempTehai[depth+2] == 4:
        self.add_sequence(depth)
        self.add_sequence(depth)
        self.add_sequence(depth)
        self.add_sequence(depth)
        self.shuntsu = [depth] * 4
        self.shuntsu_suu += 4
        self.mentsu_cut(depth+3)
        self.del_sequence(depth)
        self.del_sequence(depth)
        self.del_sequence(depth)
        self.del_sequence(depth)
        self.shuntsu_suu -= 4
        self.shuntsu = [pai.NULL_PAI] * 4
    elif self.tempTehai[depth] == 3:
      #triple only
      self.add_triple(depth)
      self.koutsu[self.koutsu_suu] = depth
      self.koutsu_suu += 1
      self.mentsu_cut(depth+1)
      self.del_triple(depth)
      self.koutsu_suu -= 1
      self.koutsu[self.koutsu_suu] = pai.NULL_PAI
      #three identical sequences
      if i < 8 and self.tempTehai[depth+1] >= 3 and self.tempTehai[depth+2] >= 3:
        self.add_sequence(depth)
        self.add_sequence(depth)
        self.add_sequence(depth)
        self.shuntsu[self.shuntsu_suu] = self.shuntsu[self.shuntsu_suu+1] = self.shuntsu[self.shuntsu_suu+2] = depth
        self.shuntsu_suu += 3
        self.mentsu_cut(depth+1)
        self.del_sequence(depth)
        self.del_sequence(depth)
        self.del_sequence(depth)
        self.shuntsu_suu -= 3
        self.shuntsu[self.shuntsu_suu] = self.shuntsu[self.shuntsu_suu+1] = self.shuntsu[self.shuntsu_suu+2] = pai.NULL_PAI
    #two identical sequences
    elif self.tempTehai[depth] == 2 and i < 8 and self.tempTehai[depth+1] >= 2 and self.tempTehai[depth+2] >= 2:
      self.add_sequence(depth)
      self.add_sequence(depth)
      self.shuntsu[self.shuntsu_suu] = self.shuntsu[self.shuntsu_suu+1] = depth
      self.shuntsu_suu += 2
      self.mentsu_cut(depth+1)
      self.del_sequence(depth)
      self.del_sequence(depth)
      self.shuntsu_suu -= 2
      self.shuntsu[self.shuntsu_suu] = self.shuntsu[self.shuntsu_suu+1] = pai.NULL_PAI
    #sequence
    elif self.tempTehai[depth] == 1 and i < 8 and self.tempTehai[depth+1] and self.tempTehai[depth+2]:
      self.add_sequence(depth)
      self.shuntsu[self.shuntsu_suu] = depth
      self.shuntsu_suu += 1
      self.mentsu_cut(depth+1)
      self.del_sequence(depth)
      self.shuntsu_suu -= 1
      self.shuntsu[self.shuntsu_suu] = pai.NULL_PAI

  #independent triples check
  def KanzenKoutsuCheck(self):
    kanzenkoutsu_suu = 0

    #honor tiles independent triples check
    for i in range(31, 38):
      if self.tempTehai[i] >= 3:
        self.koutsu[kanzenkoutsu_suu] = i
        kanzenkoutsu_suu += 1
        self.tempTehai[i] = 0
      elif self.tempTehai[i] == 2:
        self.toitsu_suu += 1
        self.tempTehai[i] = 0
      elif self.tempTehai[i] == 1:
        self.tempTehai[i] = 0
        self.add_single(i)

    #suited tiles independent triples check
    for i in range(0, 30, 10):
      if self.tempTehai[i+1] >= 3 and not self.tempTehai[i+2] and not self.tempTehai[i+3]:
        self.koutsu[kanzenkoutsu_suu] = i+1
        self.tempTehai[i+1] -= 3
        kanzenkoutsu_suu += 1

      if not self.tempTehai[i+1] and self.tempTehai[i+2] >= 3 and not self.tempTehai[i+3] and not self.tempTehai[i+4]:
        self.koutsu[kanzenkoutsu_suu] = i+2
        self.tempTehai[i+2] -= 3
        kanzenkoutsu_suu += 1

      #check for 3~7 independent triples
      for j in range(0, 5):
        if not self.tempTehai[i+j+1] and not self.tempTehai[i+j+2] and self.tempTehai[i+j+3] >= 3 and not self.tempTehai[i+j+4] and not self.tempTehai[i+j+5]:
          self.koutsu[kanzenkoutsu_suu] = i+j+3
          self.tempTehai[i+j+3] -= 3
          kanzenkoutsu_suu += 1

      if not self.tempTehai[i+6] and not self.tempTehai[i+7] and self.tempTehai[i+8] >= 3 and not self.tempTehai[i+9]:
        self.koutsu[kanzenkoutsu_suu] = i+8
        self.tempTehai[i+8] -= 3
        kanzenkoutsu_suu += 1

      if not self.tempTehai[i+7] and not self.tempTehai[i+8] and self.tempTehai[i+9] >= 3:
        self.koutsu[kanzenkoutsu_suu] = i+9
        self.tempTehai[i+9] -= 3
        kanzenkoutsu_suu += 1

    return kanzenkoutsu_suu

  #independent sequences check
  def KanzenShuntsuCheck(self):
    kanzenshuntsu_suu = 0

    for p in range(0, 30, 10): #mps
      for i in range(8): #123~789
        for j in range(2): #identical sequences
          if not self.tempTehai[p+i] and self.tempTehai[p+i+1] > 0 and self.tempTehai[p+i+1] < 3 and self.tempTehai[p+i+2] > 0 and self.tempTehai[p+i+2] < 3 and self.tempTehai[p+i+3] > 0 and self.tempTehai[p+i+3] < 3 and not self.tempTehai[p+i+4]:
            self.shuntsu[kanzenshuntsu_suu] = p+i+1
            self.tempTehai[p+i+1] -= 1
            self.tempTehai[p+i+2] -= 1
            self.tempTehai[p+i+3] -= 1
            kanzenshuntsu_suu += 1

    return kanzenshuntsu_suu

  def winhandOutput(self):
    for array in self.winhand_breakdown:
      self.winhand_string += 'Regular win hand\n'
      self.winhand_string += 'Head: ' + pai.PAI_TYPE[array[0]] + ' ' + pai.PAI_TYPE[array[0]] + '\n'
      for i in range(4):
        if array[i+1] != pai.NULL_PAI:
          self.winhand_string += 'Triple: ' + pai.PAI_TYPE[array[i+1]] + ' ' + pai.PAI_TYPE[array[i+1]] + ' ' + pai.PAI_TYPE[array[i+1]] + '\n'
      for i in range(4):
        if array[i+5] != pai.NULL_PAI:
          self.winhand_string += 'Sequence: ' + pai.PAI_TYPE[array[i+5]] + ' ' + pai.PAI_TYPE[array[i+5]+1] + ' ' + pai.PAI_TYPE[array[i+5]+2] + '\n'
      self.winhand_string += '\n'

  def EffectiveTiles(self, syanten_suu, syanten_seven, syanten_thirteen): #only 13 tiles hand
    syanten_min = min(int(syanten_suu + .5), int(syanten_seven + .5), int(syanten_thirteen + .5))
    check = (syanten_min == int(syanten_suu + .5)) + ((syanten_min == int(syanten_seven + .5)) << 1) + ((syanten_min == int(syanten_thirteen + .5)) << 2) #bit expression, 1 for regular hand, 2 for seven pairs, 4 for thirteen orphans
    effectivetiles = [0] * 38
    for i in range(38):
      if i % 10 == 0 or self.tehai[i] >= 4: continue
      if check & 4 and i in pai.THIRTEEN_SET: #thirteen orphans
        if not self.tehai[i]: effectivetiles[i] = 4
        elif syanten_thirteen - int(syanten_thirteen): effectivetiles[i] = 3
      if check & 2 and self.tehai[i] < 2 and not effectivetiles[i]: #seven pairs
        if self.tehai[i] == 1: effectivetiles[i] = 3
        elif syanten_seven - int(syanten_seven): effectivetiles[i] = 4
      if check & 1 and not effectivetiles[i]: #regular hand
        #tiles contact analysis, for virtual mode all are effective tiles
        if (i > 30 and not self.tehai[i]) or (i % 10 == 1 and not self.tehai[i] and not self.tehai[i+1] and not self.tehai[i+2]) or (i % 10 == 9 and not self.tehai[i-2] and not self.tehai[i-1] and not self.tehai[i]) or (not self.tehai[i-2] and not self.tehai[i-1] and not self.tehai[i] and not self.tehai[i+1] and not self.tehai[i+2]):
          if syanten_suu - int(syanten_suu): effectivetiles[i] = 4
          continue
        array = copy.deepcopy(self.tehai)
        array[i] += 1
        try_pai = pai(array)
        if syanten_suu > 0:
          if try_pai.syantenCheck() < syanten_suu:
            effectivetiles[i] = 4 - self.tehai[i]
        else:
          try_pai.winhand_breakdown = []
          try_pai.find_winhand()
          if try_pai.winhand_breakdown != []:
            effectivetiles[i] = 4 - self.tehai[i]
    return effectivetiles

  def syantenCheck_seven(self):
    cnt = cnt_pair = 0
    for i in range(38):
      if i % 10 == 0: continue
      if self.tehai[i]: cnt += 1
      if self.tehai[i] >= 2: cnt_pair += 1
    self.syanten_seven = 6 - min(7, cnt_pair) + max(0, 6.5 - cnt) #if not enough kinds of tiles, virtual mode
    if self.syanten_seven == -1: #winhand output
      self.winhand_string += 'Seven pairs win hand\n'
      for i in range(38):
        if self.tehai[i] >= 2: self.winhand_string += 'Pair: ' + pai.PAI_TYPE[i] + ' ' + pai.PAI_TYPE[i] + '\n'
      self.winhand_string += '\n'
    return self.syanten_seven

  #not in use
  def EffectiveTiles_seven(self, syanten_seven): #only 13 tiles hand
    effectivetiles = [0] * 38
    for i in range(38):
      if i % 10 == 0 or self.tehai[i] >= 2: continue
      elif self.tehai[i] == 1: effectivetiles[i] = 3
      elif syanten_seven - int(syanten_seven): effectivetiles[i] = 4
    return effectivetiles

  def syantenCheck_thirteen(self):
    cnt = cnt_pair = 0
    for i in pai.THIRTEEN_SET:
      if self.tehai[i]: cnt += 1
      if self.tehai[i] >= 2: cnt_pair = 1
    self.syanten_thirteen = 12.5 - cnt - .5 * cnt_pair #if no pair, virtual mode
    if self.syanten_thirteen == -1:
      self.winhand_string += 'Thirteen orphans win hand\n'
      for i in pai.THIRTEEN_SET:
        if self.tehai[i]: self.winhand_string += (pai.PAI_TYPE[i] + ' ') * self.tehai[i]
      self.winhand_string += '\n'
    return self.syanten_thirteen

  #not in use
  def EffectiveTiles_thirteen(self, syanten_thirteen):
    effectivetiles = [0] * 38
    for i in pai.THIRTEEN_SET:
      if not self.tehai[i]: effectivetiles[i] = 4
      elif syanten_thirteen - int(syanten_thirteen): effectivetiles[i] = 3

  def calculate(self, allhands = True):
    self.checkReddora()
    self.moveReddora()
    sum_tehai = sum(self.tehai)
    if sum_tehai > 14 or sum_tehai % 3 == 0: sys.exit('Invalid hand!')
    for i in range(38):
      if self.tehai[i] > 4: sys.exit('Invalid hand!')
    self.fixed_mentsu_suu = int((14 - sum(self.tehai)) / 3)
    syanten_min = syanten_suu = self.syantenCheck()
    if syanten_suu == -1: self.find_winhand()
    self.winhandOutput()
    if self.fixed_mentsu_suu == 0 and allhands:
      syanten_seven = self.syantenCheck_seven()
      syanten_thirteen = self.syantenCheck_thirteen()
      syanten_min = min(syanten_suu, syanten_seven, syanten_thirteen)
    else:
      syanten_seven = syanten_thirteen = 15
    self.pai_print()
    flower = int(random.uniform(0, 8))
    if sum(self.tehai) % 3 == 1:
      print self.pai_array + pai.FLOWER_TYPE[flower]
    else:
      print self.pai_array
    print
    print 'Regular hand to ready number:', int(syanten_suu + 1.5) - 1
    if self.fixed_mentsu_suu == 0 and allhands:
      print 'Seven pairs to ready number:', int(syanten_seven + 1.5) - 1
      print 'Thirteen orphans to ready number:', int(syanten_thirteen + 1.5) - 1
#    if syanten_suu != int(syanten_suu): print 'Triple tiles abundant. Suggest declaration of quad.'
    print
    if self.winhand_string != '':
      print 'All break down:\n'
      print self.winhand_string
    #no tile to discard
    if sum(self.tehai) % 3 == 1:
      effectivetiles = self.EffectiveTiles(syanten_suu, syanten_seven, syanten_thirteen)
      if sum(effectivetiles):
        if syanten_min <= 0: self.effective_string += 'Discard ' + pai.FLOWER_TYPE[flower] + ', waiting tiles:\n'
        else: self.effective_string += 'Discard ' + pai.FLOWER_TYPE[flower] + ', effective tiles:\n'
        for i in range(38):
          if effectivetiles[i]:
            self.effective_string += pai.PAI_TYPE[i] + ' '
        self.effective_string += 'total ' + str(sum(effectivetiles)) + ' tiles\n'
    #discard one tile
    elif sum(self.tehai) % 3 == 2:
      effective_compound = []
      for i in range(38):
        if i % 10 == 0: continue
        if self.tehai[i]:
          array = copy.deepcopy(self.tehai)
          array[i] -= 1
          discarded_pai = pai(array)
          discarded_syanten_min = discarded_pai.syantenCheck()
          if self.fixed_mentsu_suu == 0 and allhands:
            discarded_pai.syantenCheck_seven()
            discarded_pai.syantenCheck_thirteen()
            discarded_syanten_min = min(discarded_pai.syanten_suu, discarded_pai.syanten_seven, discarded_pai.syanten_thirteen)
          if discarded_syanten_min > max(syanten_min, 0): continue
          effectivetiles = discarded_pai.EffectiveTiles(discarded_pai.syanten_suu, discarded_pai.syanten_seven, discarded_pai.syanten_thirteen)
          if effectivetiles[i]: effectivetiles[i] -= .5
          if sum(effectivetiles):
            effective_line = [0, 0, ''] #-total number of effective tiles, discarded tile, string of effective tiles. The first two is for sorting
            if syanten_suu <= 0: effective_line[2] += 'Discard ' + pai.PAI_TYPE[i] + ', waiting tiles:\n'
            else: effective_line[2] += 'Discard ' + pai.PAI_TYPE[i] + ', effective tiles:\n'
            for j in range(38):
              if effectivetiles[j]:
                effective_line[2] += pai.PAI_TYPE[j] + ' '
            effective_line[2] += 'total ' + str(int(sum(effectivetiles))) + ' tiles\n'
            effective_line[0] = -int(sum(effectivetiles))
            effective_line[1] = i
            effective_compound.append(effective_line)
      #sort the effective tile lines from more to less
      for i in sorted(range(len(effective_compound)), key=effective_compound.__getitem__): self.effective_string += effective_compound[i][2]
    print self.effective_string


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('-p', '-pai', '--pai', default='')
  parser.add_argument('-q', '-qai', '--qai', default='1112345678999m')
  args = parser.parse_args()
  if args.pai != '':
    k = pai(args.pai)
    k.calculate(False)
  else:
    k = pai(args.qai)
    k.calculate(True)

if __name__ == "__main__":
  main()

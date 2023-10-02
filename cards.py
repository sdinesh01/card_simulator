from __future__ import annotations
import random

# FYI - this is a thing:
# my_type: TypeAlias = tuple[list[int], bool]


class Hand:
    # Hand object should be
    # a collection of cards
    # and determine whether there are 
    # pairs, straights, etc.
    
    def __init__(self,
                 cards: list[Card]
                ):
        
        # validate cards -- no repeats
        self.__validate_hand(cards)
        self.__cards = cards
        self.count_faces_suits()
        self.__cards_sorted = sorted(self.__cards)
        return
    
    def __validate_hand(self, cards:list[Card]
                        ):
        
        for i in range(len(cards)): 
            for j in range(i+1, len(cards)):
                if cards[i] == cards[j]:
                    raise ValueError('Hand contains two of: ' + str(cards[i]))
    
    def __create_rules(self): 
        self.__RULES = {
                 'straight_flush': self.get_straight_flush,
                 'four_kind'     : self.get_quadruples,
                 'flush'         : self.get_flush,
                 'straight'      : self.get_straight,
                 'three_kind'    : self.get_triples,
                 'two_kind'      : self.get_pairs,
                 'high_card'     : self.get_high_card
                }
        return
    
    def get_best_hand(self) -> tuple[int]: # Rank of the hand (low wins)
                                     # Hand info
        
        for rank, (hand_name, func) in enumerate(self.__RULES.items()):
            output = func()
            if all(output):
                return rank, hand_name, output
        return
    
    def __repr__(self):
        return 'Hand with:\n' + str(self.__cards)
    
    def count_faces_suits(self):
        self.__face_counts = {}
        self.__suit_counts = {}
        
        for card in self.__cards:
            face = card.get_face_num()
            suit = card.get_suit_name()
            
            if face in self.__face_counts:
                self.__face_counts[face] += 1
            else:
                self.__face_counts[face] = 1
            
            if suit in self.__suit_counts:
                self.__suit_counts[suit] += 1
            else:
                self.__suit_counts[suit] = 1
        return
    
    def get_face_counts(self):
        return self.__face_counts.copy()
    
    def get_suit_counts(self):
        return self.__suit_counts.copy()
    
    def get_high_card(self):
        return (self.__cards_sorted[-1].get_face_num(), )
    
    def get_flush(self
                 ) -> tuple[int, # High card 
                            str  # Suit name
                           ]:
        for suit, count in self.__suit_counts.items():
            if count >= 5:
                high_card = 0
                for card in self.__cards:
                    if card.get_suit_name() == suit:
                        high_card = max(high_card, card.get_face_num())
                return high_card, suit
        return None, None
    
    def get_straight(self) -> int:
        # Compte the difference between the
        # consecutive sorted cards
        diffs = []
        for i in range(len(self.__cards_sorted)-1):
            diffs.append(self.__cards_sorted[i+1] - self.__cards_sorted[i])
        
        # We have a straight if the list of differences
        # contains 4 ones, not separated by anything other
        # than zeros
        ones = 0
        idx_high_card = -1
        for idx,val in enumerate(diffs):
            if val == 1:
                ones += 1
                if ones >= 4:
                    idx_high_card = idx
            elif (val == 0):
                pass
            else:
                ones = 0
        if idx_high_card == -1:
            return (None, )
        else:
            return (self.__cards_sorted[idx_high_card+1].get_face_num(), )
    
    def get_straight_flush(self) -> int:
        _, suit = self.get_flush()
        
        face = (None, )
        # if suit is not none, make a new hand containing cards from that suit
        if suit is not None:
            cards = []
            for card in self.__cards:
                if card.get_suit_name() == suit:
                    cards.append(card)
            hand = Hand(cards)
            # Check if the subset contains a straight
            face = hand.get_straight()
        return face
    
    def get_mults(self, n:int) -> list[str]:
        mults = []
        for face, count in self.__face_counts.items():
            if count == n:
                mults.append(face)
        if len(mults) == 0:
            return None
        else:
            return mults
    
    def get_pairs(self) -> list[str]:
        return (self.get_mults(2), )
    
    def get_triples(self) -> list[str]:
        return (self.get_mults(3), )
    
    def get_quadruples(self) -> list[str]:
        return (self.get_mults(4), )

class Deck:
    def __init__(self):
        self.fill_deck()
        self.shuffle()
        return
    
    def fill_deck(self):
        self.__cards = [Card(n) for n in range(52)]
        return
    
    def shuffle(self,
                restore_deck: bool = True):
        if restore_deck:
            self.fill_deck()
        # A very unrealistic shuffle
        random.shuffle(self.__cards)
        return
    
    def deal(self, 
             num_cards: int
            ) -> Hand:
        
        cards = []
        
        if num_cards > len(self.__cards):
            raise ValueError("Not enough cards left in the deck.")
        
        while len(cards) < num_cards:
            cards.append(self.__cards.pop())
        
        return Hand(cards)

class Card:
    
    __SUITS = ['Clubs', 
               'Diamonds',
               'Hearts',
               'Spades']
    
    __FACES = {n+1:n+1 for n in range(13)}
    __FACES[1]  = 'Ace'
    __FACES[11] = 'Jack'
    __FACES[12] = 'Queen'
    __FACES[13] = 'King'
    
    __FACE_NUMS = {}
    __FACE_NUMS['Ace']   = 1
    __FACE_NUMS['Jack']  = 11
    __FACE_NUMS['Queen'] = 12
    __FACE_NUMS['King']  = 13
    
    def __init__(self, 
                 value: int = None,
                 suit:  str = None,
                 face:  str = None
                ):
        if suit is not None:
            suit = suit.capitalize()
        self.__validate_input(value, suit, face)
        
        if face is not None:
            if face in self.__FACE_NUMS:
                value = self.__FACE_NUMS[face]
            else:
                value = int(face)
        if suit is not None:
            value += 13*self.__SUITS.index(suit) - 1
        
        self.__value = value
        self.__face = value % 13 + 1
        self.__suit = value//13
        return
    
    def __validate_input(self, 
                         value: int, 
                         suit:  str, 
                         face:  str
                        ) -> None:
        
        MSG_BAD_INPUT_COMBO = 'Either value, OR suit and face, should be provided.'
        
        if (value is None) and (suit is None) and (face is None):
            raise ValueError(MSG_BAD_INPUT_COMBO)
        
        if value is not None:
            if (suit is not None) or (face is not None):
                raise ValueError(MSG_BAD_INPUT_COMBO)
        
        if suit is not None:
            if suit not in self.__SUITS:
                raise ValueError(suit + ' is not a valid suit name.')
            if face is None:
                raise ValueError('Suit was specified without a face value.')
        if face is not None:
            if suit is None:
                raise ValueError('Face was specified without a suit.')
        
        if (suit is not None) and (face is not None):
            if value is not None:
                raise ValueError(MSG_BAD_INPUT_COMBO)
        
        return
    
    def get_face_num(self):
        return self.__face
    
    def get_face_name(self):
        return self.__FACES[self.__face]
    
    def get_suit_num(self):
        return self.__suit
    
    def get_suit_name(self):
        return self.__SUITS[self.__suit]
    
    def __repr__(self):
        return str(self.__FACES[self.__face]) + \
               ' of ' + str(self.__SUITS[self.__suit])
    
    def __gt__(self, other):
        return self.__face > other.__face
    
    def __sub__(self, other):
        return self.__face - other.__face
    
    def __eq__(self, other):
        return (self.__face == other.__face) and (self.__suit == other.__suit)
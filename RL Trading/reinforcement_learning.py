import os
import pandas as pd
import numpy as np
from random import *
  
# state class definition
class state: 
    
    PE_RATIO_MIN = 0
    PE_RATIO_MAX = 1000
   
    def __init__(self, 
                 stock_name = "",
                 qty = 0, # int: qty of shares holding
                 close_sma_ratio = 0, # int: [0-9] discretized value of closing price to sma ratio
                 price_bb_ratio = 0,  # int: [0-9] discretized value of closing price_sma difference to bollinger band ratio
                 momentum = 0,  # int: [0-9] discretized value of momentum              
                 total_return = 0): # int: [0-9] discretized value of total return from holding the security
        
        self.stock_name = stock_name
        self.qty = qty       
        self.close_sma_ratio = close_sma_ratio
        self.price_bb_ratio = price_bb_ratio
        self.momentum = momentum        
        self.total_return = total_return
    
    def holding(self):
        return (self.qty > 0)
    
    def value(self):
        return (int(self.holding()) * 10000 + self.close_sma_ratio * 1000 +
                self.price_bb_ratio * 100 + self.momentum * 10 + self.total_return)
    
    def __hash__(self):
        return hash(self.value())
    
    def __eq__(self, other): 
        return (self.value() == other.value())

    
# action class definition
class action:
    
    # value is a real number [-1 to +1] 
    # for now only -1, -0.5, 0, 0.5, and 1 are used
    # -ve meaning sell, +ve meaning buy, and value is the percentage of current holdings
    # example: -0.5 means sell 50% of holdings, +1 means buy 100% (maximum) amount for a holding, 0 means do nothing
    def __init__(self, value = 0):
        self.value = value
    
    def __eq__(self, other): 
        return self.value == other.value

# Q(s,a) value class definition
class Q:
    def __init__(self, s=state(), a=action()):
        self.s = s
        self.a = a
        self.value = 0
    
    def __hash__(self):
        return hash(str(self.s.value())+str(self.a))
    
    def __eq__(self, other): 
        return (self.s == other.s and self.a == other.a)
    
# experience tuple <s, a, s', r> class definition
class experience: 

    def __init__(self, s1 = state(), a1 = action(), s2 = state(), r = 0):
        self.s1 = s1
        self.a1 = a1
        self.s2 = s2
        self.r = r
        
    def __eq__(self, other): 
        return (self.s1 == other.s1 and 
                self.a1 == other.a1 and 
                self.s2 == other.s2 and 
                self.r == other.r)

# policy class definition
class policy:
    
    def __init__(self, sa_dict=dict(), init_epsilon=1, min_epsilon=0):
        '''sa_dict: dict with key=state, value=list of (a, Q<s,a>) tuples for all actions a, taken in state s'''
        self.sa_dict = sa_dict
        
        '''number < 1, to be used in an epsilon-greedy policy'''
        self.init_epsilon = init_epsilon
        self.min_epsilon = min_epsilon
        
        '''list of all possible actions'''
        self.all_actions = [-1, -0.5, 0, 0.5, 1]
    
    '''method that returns an action to be taken according to our policy
       follows an epsilon-greedy policy where with prob(epsilon) we choose 
       a random action, otherwise we choose the best action (highest Q value)'''
    def get_action(self, s, epoch=None, allowed_actions=None):
        
        # adjust epsilon according to out number of epiosdes
        if (epoch != None):
            epsilon = max(self.min_epsilon, self.init_epsilon-(epoch/1e4))
        else:
            epsilon = self.init_epsilon
            
        # with P(epsilon) choose a random action
        # otherwise choose the best action
        rand = random()
        action = 0
        
        #epsilon
        if (rand <= epsilon):
            if (allowed_actions == None):
                actions = self.all_actions
            else:
                actions = allowed_actions
                
            a = sample(actions, 1)
            action = a[0]
        #greedy
        else:
            if s in self.sa_dict:
                # find the tuple(a, Q) with the max Q and return a
                max_tuple = max(self.sa_dict[s], key=lambda item:item[1].value)
                action = max_tuple[0]
        
        return action
    
    '''method that returns the action that maximizes the Q over all possible actions in state s '''
    def get_maxQ_action(self, s, allowed_actions=None):
                                                       
        action = 0

        #greedy
        if s in self.sa_dict:
            # find the tuple(a, Q) with the max Q and return a
            max_tuple = max(self.sa_dict[s], key=lambda item:item[1].value)
            action = max_tuple[0]     
                                                       
        return action
    
    '''method to update the current policy with a new Q<s,a>
       if state s already exists, update the Q value, 
       if not add action and an initial Q=0 to our list of tuples'''
    def update(self, s, a, q):
        if s in self.sa_dict:
            # find item with action a, and update with (a, Q)
            aQ_list = list()
            for aQ in self.sa_dict[s]:
                if (a == aQ[0]):
                    #aQ = (a, q)
                    #break
                    aQ_list.append((a, q))                   
                else:
                    aQ_list.append(aQ)
            self.sa_dict[s] = aQ_list
        else:
            aQ_list = list()
            for action in self.all_actions:
                if (a == action):
                    aQ_list.append((a, q))
                else:                    
                    aQ_list.append((action, Q(s,action)))
            self.sa_dict[s] = aQ_list
                                                       
class Qtable:
    def __init__(self, init_alpha=0.2, min_alpha=0.01, gamma=0.9):
        # learning rate
        self.init_alpha = init_alpha   
        self.min_alpha = min_alpha
        # discount rate: lower means we value near rewards more
        self.gamma = gamma        
        # Q table is a dict with key=hash from state-action, and value=Q object
        self.table = dict()
    
    def get_key(self, s=state(), a=action()):
        return hash(str(s.value())+str(a))
    
    def get_Q(self, s=state(), a=action()):
        key = self.get_key(s,a)
        if (key in self.table):
            return self.table[key]
        else:
            return Q(s,a)
    
    def update(self, exp, pi, epoch=None):
                            
        # if the Q(s1,a1) does not exists in table, add it
        key = self.get_key(exp.s1, exp.a1)
        if (key not in self.table):
            self.table[key] = Q(exp.s1, exp.a1)
        
        # decay alpha if epoch is provided
        if (epoch != None):
            alpha = max(self.min_alpha, self.init_alpha-(epoch/1e5))
        else:
            alpha = self.init_alpha
        
        # update Q(s1,a1) with <s1, a1, s2, r> experience tuple
        maxQ = self.get_Q(exp.s2, pi.get_maxQ_action(exp.s2))
        self.table[key].value = (1 - alpha) * self.table[key].value + alpha * (exp.r + self.gamma * maxQ.value)
                                                       
            
       

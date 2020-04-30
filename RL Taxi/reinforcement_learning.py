import os
import pandas as pd
import numpy as np
from random import *
import pickle
  
# state class definition
class state: 
   
    def __init__(self, 
                 taxi_i = 0, 
                 taxi_j = 0,
                 pass_i = 0,  
                 pass_j = 0,              
                 dest_i = 9,
                 dest_j = 9,
                 north_cell = 0,
                 east_cell = 0,
                 south_cell = 0,
                 west_cell = 0,
                 pass_picked = False): 
        
        self.taxi_i = taxi_i
        self.taxi_j = taxi_j       
        self.pass_i = pass_i
        self.pass_j = pass_j
        self.dest_i = dest_i        
        self.dest_j = dest_j
        self.north_cell = north_cell
        self.east_cell = east_cell
        self.south_cell = south_cell
        self.west_cell = west_cell
        self.pass_picked = pass_picked
    
    def value(self):
        return (str(self.taxi_i) + '_' + str(self.taxi_j) + '_' +
                str(self.pass_i) + '_' + str(self.pass_j) + '_' +
                str(self.dest_i) + '_' + str(self.dest_j) + '_' + 
                str(self.north_cell) + '_' + str(self.east_cell) + '_' +
                str(self.south_cell) + '_' + str(self.west_cell) + '_' +
                str(int(self.pass_picked)))
    
    def __hash__(self):
        return hash(self.value())
    
    def __eq__(self, other): 
        return (self.value() == other.value())

    
# action class definition
class action:
    
    # value is right, left, up, down, pickup, drop-off
    def __init__(self, value = ""):
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
        # west, east, north, south, pick-up, drop-off
        self.all_actions = ['w', 'e', 'n', 's', 'p', 'd']
        
    def get_epsilon(self, epoch=None):
        # adjust epsilon according to out number of epiosdes
        if (epoch != None):
            epsilon = max(self.min_epsilon, self.init_epsilon-(epoch/1e3))
        else:
            epsilon = self.init_epsilon
            
        return epsilon
            
    '''method that returns an action to be taken according to our policy
       follows an epsilon-greedy policy where with prob(epsilon) we choose 
       a random action, otherwise we choose the best action (highest Q value)'''
    def get_action(self, s, epoch=None, allowed_actions=None):
        
        epsilon = self.get_epsilon(epoch)
            
        # with P(epsilon) choose a random action
        # otherwise choose the best action
        rand = random()
        action = 'e'
        
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
                                                       
        action = 'e'

        #greedy
        if s in self.sa_dict:
            # find the tuple(a, Q) with the max Q and return a
            max_tuple = max(self.sa_dict[s], key=lambda item:item[1].value)
            action = max_tuple[0]     
                                                       
        return action
    
    '''method to update the current policy with a new Q<s,a>
       if state s already exists, update the Q value, 
       if not, add tuple (a=action, Q=0) to our list of tuples'''
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
            
    def save(self, filename):
        with open(filename, 'wb') as output:  # Overwrites any existing file.
            pickle.dump(self, output, pickle.HIGHEST_PROTOCOL)
    
    @staticmethod
    def read(filename):
        with open(filename, 'rb') as input:
            obj = pickle.load(input)
        return obj
                                                       
class Qtable:
    def __init__(self, init_alpha=0.2, min_alpha=0.01, gamma=0.9, q_table=None):
        # learning rate
        self.init_alpha = init_alpha   
        self.min_alpha = min_alpha
        # discount rate: lower means we value near rewards more
        self.gamma = gamma        
        # Q table is a dict with key=hash from state-action, and value=Q object
        if q_table == None:
            self.table = dict()
        else:
            self.table = q_table.copy()
    
    def get_key(self, s=state(), a=action()):
        return hash(str(s.value())+str(a))
    
    def get_Q(self, s=state(), a=action()):
        key = self.get_key(s,a)
        if (key in self.table):
            return self.table[key]
        else:
            return Q(s,a)
    
    def get_alpha(self, epoch=None):
        # decay alpha if epoch is provided
        if (epoch != None):
            alpha = max(self.min_alpha, self.init_alpha-(epoch/1e3))
        else:
            alpha = self.init_alpha
            
        return alpha
    
    def update(self, exp, pi, epoch=None):
                            
        # if the Q(s1,a1) does not exists in table, add it
        key = self.get_key(exp.s1, exp.a1)
        if (key not in self.table):
            self.table[key] = Q(exp.s1, exp.a1)
        
        alpha = self.get_alpha(epoch)
        
        # update Q(s1,a1) with <s1, a1, s2, r> experience tuple
        maxQ = self.get_Q(exp.s2, pi.get_maxQ_action(exp.s2))
        self.table[key].value = (1 - alpha) * self.table[key].value + alpha * (exp.r + self.gamma * maxQ.value)
                                                       
    def save(self, filename):
        with open(filename, 'wb') as output:  # Overwrites any existing file.
            pickle.dump(self, output, pickle.HIGHEST_PROTOCOL)
    
    @staticmethod
    def read(filename):
        with open(filename, 'rb') as input:
            obj = pickle.load(input)
        return obj
 
def save_data(q_table, policy, filename):
    data_tuple = (q_table, policy)
    with open(filename, 'wb') as output:  # Overwrites any existing file.
        pickle.dump(data_tuple, output, pickle.HIGHEST_PROTOCOL)

def read_data(filename):
    with open(filename, 'rb') as input:
        obj = pickle.load(input)
    return obj

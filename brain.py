"""
Brain system using Q-learning for creature decision-making
Processes sensory input and decides actions
"""

import numpy as np
import random
from collections import defaultdict

class Action:
    """Enumeration of possible actions"""
    MOVE_UP = 0
    MOVE_DOWN = 1
    MOVE_LEFT = 2
    MOVE_RIGHT = 3
    EAT = 4
    REPRODUCE = 5
    PHOTOSYNTHESIZE = 6
    STAY = 7

    @staticmethod
    def count():
        return 8


class Brain:
    """Q-learning based decision-making system for creatures"""

    def __init__(self, learning_rate=0.1, discount_factor=0.9, exploration_rate=0.3):
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.q_table = defaultdict(lambda: np.zeros(Action.count()))
        self.last_state = None
        self.last_action = None
        self.last_reward = 0

    def get_state_representation(self, vision_data, internal_state):
        """Convert sensory input into a discrete state representation"""
        energy_level = int(internal_state['energy'] / 20)
        nearby_food = vision_data.get('food_nearby', False)
        nearby_plant = vision_data.get('plant_nearby', False)
        nearby_wall = vision_data.get('wall_nearby', False)
        nearby_creature = vision_data.get('creature_nearby', False)
        state = (energy_level, nearby_food, nearby_plant, nearby_wall, 
                nearby_creature, internal_state.get('can_reproduce', False))
        return state

    def choose_action(self, state, valid_actions=None):
        """Choose an action using epsilon-greedy strategy"""
        if valid_actions is None:
            valid_actions = list(range(Action.count()))
        if random.random() < self.exploration_rate:
            action = random.choice(valid_actions)
        else:
            q_values = self.q_table[state]
            valid_q_values = [(a, q_values[a]) for a in valid_actions]
            action = max(valid_q_values, key=lambda x: x[1])[0]
        return action

    def update_q_value(self, state, action, reward, next_state):
        """Update Q-value using Q-learning update rule"""
        current_q = self.q_table[state][action]
        max_next_q = np.max(self.q_table[next_state])
        new_q = current_q + self.learning_rate * (
            reward + self.discount_factor * max_next_q - current_q
        )
        self.q_table[state][action] = new_q

    def learn(self, state, action, reward, next_state):
        """Learning step: update Q-values based on experience"""
        self.update_q_value(state, action, reward, next_state)
        self.last_state = state
        self.last_action = action
        self.last_reward = reward

    def copy(self):
        """Create a copy of the brain (for offspring, with some inheritance)"""
        new_brain = Brain(self.learning_rate, self.discount_factor, self.exploration_rate)
        for state, q_values in self.q_table.items():
            new_brain.q_table[state] = q_values + np.random.normal(0, 0.1, Action.count())
        return new_brain

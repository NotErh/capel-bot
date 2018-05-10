import discord
import pickle

# Stores statistics for the bot
class Stats:
    # on init, open stats.p if possible
    # failing that, create a new dict
    def __init__(self):
        self.fname = 'stats.p'
        try:
            self.stat_dict = self.unpickle_dict()
        except (FileNotFoundError, pickle.UnpicklingError):
            self.stat_dict = self.initialize_dict()
        self.pickle_dict()

    def initialize_dict(self):
        d = dict()
        d['rot_count'] = 0              # number of rot13's the bot has done
        d['headpat_dict'] = dict()      # dict with users and number of times
        return d                            # they've been headpatted
        
    def pickle_dict(self):
        pickle.dump(self.stat_dict, open(self.fname, 'wb+'))

    def unpickle_dict(self):
        return pickle.load(open(self.fname, 'rb'))

    def get_rot_count(self):
        return self.stat_dict['rot_count']

    def increment_rot(self):
        self.stat_dict['rot_count'] += 1
        self.pickle_dict()

    def set_rot_count(self, num):
        self.stat_dict['rot_count'] = num
        self.pickle_dict()

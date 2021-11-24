from src.Critic import Critic
import numpy as np

class VarietyCritic(Critic):
    #Essentially the Line critic with a flat line, the move variation the higher the score
    def __init__(self):
        pass

    def critique(self, lvl):
        #Returns a score between 0-1 based on the particular critics scope
        # Returns a score between 0-1 based on the particular critics scope
        array1 = np.array(lvl.height_line)
        return np.var(array1)  # sum Squared difference

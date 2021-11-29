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
        array2 = np.array(lvl.height_line) #Theoretical max variance
        array2[::2] = 2
        array2[1::2] = 0
        print(array2)
        return (np.var(array1)/np.var(array2))  #variance relative to theoretical max, we want more variance so 1- is added

    def print(self):
        print("VARIETY CRITIC")

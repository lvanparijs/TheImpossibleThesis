from src.Critic import Critic


class DifficultyCritic(Critic): #Difficulty consists of a combination of speed, spikes ratio(CompnentFrequencyCritic), ratio of jump/no_action, and VarietyCritic
    def __init__(self):
        pass

    def critique(self, lvl):
        speed_ratio = lvl.song.tempo/200 #200BPM is insane hardstyle techno, will be the highest "possible" tempo in this project
        al = lvl.action_list
        jumps = 0
        for a in al:
            if a: #1 = jump
                jumps += 1
        jump_ratio = jumps/len(al)
        #Returns a score between 0-1 based on the particular critics scope
        return (speed_ratio+jump_ratio)/2

    def print(self):
        print("DIFFICULTY CRITIC")
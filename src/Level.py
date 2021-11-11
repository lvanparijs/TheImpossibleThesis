import math
import random
from random import randrange

import pygame
import librosa

from src.Box import Box
from src.Lava import Lava
from src.Platform import Platform
from src.Spike import Spike

vec = pygame.math.Vector2
BOX_SIZE = 40
JUMP = 1
NO_ACTION = 0

class Level:

    ##A level is essentially a collection of obstacles, the ground is always the same, created based on a music track

    def __init__(self, file_name, height, player, boxes, spikes,screen_height):
        if file_name is None:
            self.width = 640
            self.tempo = 0
        else:
            self.file_name = file_name #Path to the music file
            self.y, self.sampling_rate = librosa.load(self.file_name) #Audio time series and sampling rate of the song
            self.song_duration = librosa.get_duration(y=self.y, sr=self.sampling_rate) #Time in s
            self.tempo, self.beat_frames = librosa.beat.beat_track(y=self.y, sr=self.sampling_rate)

            bps = self.tempo/60 #beats per second
            print("BPM")
            print(self.tempo)

            self.spb = 1/bps #Seconds per beat
            self.beat_times = 0
            self.action_list = []


            player.pixels_per_second = int((5*BOX_SIZE)/self.spb)#Desired jump distance
            print(player.get_jump_length())
            player.set_velocity(player.get_jump_length())
            self.width = self.song_duration*player.max_vel*60  # Width of the level in pixels, determined by length of song, speed of player

        self.boxes = boxes #Set of boxes in the level
        self.spikes = spikes #Set of spikes in the level
        self.height = height #Height of the level

        self.box_frequency = 2 #Amount of boxes per 100 pixels, for random generation
        self.spike_frequency = 1 #Amount of spikes per 100 pixels
        self.ground_level = int(screen_height * 0.76)#Ground level
        self.platform = Platform(vec(0, self.ground_level),self.width) #Main platform of the level
        self.boxes.add(self.platform)

    def generate_random(self):
        sum = 300 #Starting Buffer zone

        while sum < self.width:
            interval = randrange(350, 400)
            num_obstacles = 0
            rnd = random.uniform(0,1)
            if rnd >= 0.6:
                num_obstacles = random.randint(1, 8)
                interval = (num_obstacles)*BOX_SIZE*4
                self.boxes.add(Box((sum, self.ground_level - BOX_SIZE / 2)))
                if num_obstacles == 1:
                    self.spikes.add(Spike((sum, self.ground_level - BOX_SIZE - BOX_SIZE / 2 + 2)))
                else:
                    for i in range(1,num_obstacles):
                        self.boxes.add(Box((sum + i*BOX_SIZE*4,self.ground_level-BOX_SIZE/2-BOX_SIZE*i)))
                        self.spikes.add(Lava((sum + i*BOX_SIZE * 4, self.ground_level)))
                        self.spikes.add(Lava((sum + i*BOX_SIZE * 4 - BOX_SIZE*1, self.ground_level)))
                        self.spikes.add(Lava((sum + i*BOX_SIZE * 4 - BOX_SIZE*2, self.ground_level)))
                        self.spikes.add(Lava((sum + i*BOX_SIZE * 4 - BOX_SIZE*3, self.ground_level)))
                    if random.uniform(0,1) >= 0.5:
                        interval_rev = 0
                        for i in range(1, num_obstacles):
                            spaces = 5
                            if random.uniform(0, 1) >= 0.5:
                                spaces = 3
                            interval_tmp = BOX_SIZE * spaces
                            interval_rev += interval_tmp

                            for j in range(1,spaces):
                                self.spikes.add(Lava((sum + (num_obstacles - 1) * BOX_SIZE * 4 + interval_rev - BOX_SIZE * j,self.ground_level)))
                            if i < num_obstacles-1:
                                self.spikes.add(Lava((sum + (
                                            num_obstacles - 1) * BOX_SIZE * 4 + interval_rev,
                                                      self.ground_level)))

                            self.boxes.add(Box((sum + (num_obstacles - 1) * BOX_SIZE * 4 + interval_rev,
                                                self.ground_level - BOX_SIZE / 2 - (
                                                            BOX_SIZE * (num_obstacles - i - 1)))))

                        interval += interval_rev

            elif rnd >= 0.2:
                num_obstacles = random.randint(1, 2)
                interval = num_obstacles * BOX_SIZE
                for i in range(0,num_obstacles):
                    self.spikes.add(Spike((sum + BOX_SIZE*i, self.ground_level - BOX_SIZE/2 + 2)))
            else:
                interval = 5 * BOX_SIZE

            sum += interval + 5 * BOX_SIZE



    def generate_from_bpm(self,vel):

        #beat_times = librosa.frames_to_time(self.beat_frames, sr=self.sampling_rate) #Times of each beat
        self.beat_times = range(0,len(self.beat_frames))
        self.beat_times *= self.spb
        #print(beat_times)
        #print(self.beat_frames)
        #CURRENT PITCH SOLUTION: FIND FUNDAMENTAL FREQUENCY BETWEEN BEAT TIMES
        old_bf = 0
        note = 'C2'
        beat_freqs = []
        for bf in self.beat_frames:
            f0 = librosa.yin(self.y[old_bf:bf], fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))
            old_bf = bf
            if math.isnan(f0):
                note = note
                beat_freqs.append(librosa.note_to_hz('C2'))
            else:
                note = librosa.hz_to_note(f0)

                if f0[0] >= librosa.note_to_hz('C7'):
                    beat_freqs.append(librosa.note_to_hz('C2'))
                else:
                    beat_freqs.append(f0[0])
        print("BEAT FREQS")
        print(beat_freqs)

        for b in self.beat_times: #Generates actions for the times of the beats
            if random.uniform(0,1) > 0.8:
                self.action_list += [NO_ACTION]
            else:
                self.action_list += [JUMP]

        obstacle_pos = self.beat_times * vel * 60
        height_cnt = -1
        print(len(self.beat_times)==len(beat_freqs))
        for i in range(1,len(obstacle_pos)):
            if self.action_list[i]: #Jump
                if beat_freqs[i] == beat_freqs[i-1]: #If on same level, add box and spike
                    if height_cnt == 0:
                        for j in range(0,5):
                            self.boxes.add(Box((obstacle_pos[i]+BOX_SIZE*j, self.ground_level - BOX_SIZE / 2 - BOX_SIZE*height_cnt)))
                    if height_cnt > 0:
                        for j in range(0,5):
                            self.boxes.add(Box((obstacle_pos[i]+BOX_SIZE*j, self.ground_level - BOX_SIZE / 2 - BOX_SIZE*height_cnt)))
                        for j in range(0, 5):
                            self.spikes.add(Lava((obstacle_pos[i] + BOX_SIZE*j,self.ground_level)))

                    #self.boxes.add(Box((obstacle_pos[i] + BOX_SIZE, self.ground_level - BOX_SIZE / 2 - BOX_SIZE*height_cnt)))
                    num_spikes = random.randint(1,2)
                    for s in range(0,num_spikes):
                        self.spikes.add(
                            Spike((obstacle_pos[i] + BOX_SIZE + BOX_SIZE * s, self.ground_level - BOX_SIZE - BOX_SIZE / 2 + 2 - BOX_SIZE*height_cnt)))
                elif beat_freqs[i] > beat_freqs[i-1]: #If next note is higher, jump up a level
                    if height_cnt > 0:
                        self.boxes.add(
                        Box((obstacle_pos[i], self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height_cnt)))

                        if random.uniform(0,1) > 0.75:#Plant spikes
                            for s in range(1,4):
                                self.boxes.add(
                                    Box((obstacle_pos[i]+BOX_SIZE*s, self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height_cnt)))
                                if s < 3:
                                    self.spikes.add(Spike((obstacle_pos[i] + BOX_SIZE * s,
                                           self.ground_level - BOX_SIZE - BOX_SIZE / 2 + 2 - BOX_SIZE * height_cnt)))
                        for j in range(0, 5):
                            self.spikes.add(Lava((obstacle_pos[i] + BOX_SIZE * j, self.ground_level)))

                        self.boxes.add(
                            Box((obstacle_pos[i] + BOX_SIZE * 4, self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height_cnt - BOX_SIZE)))
                    elif height_cnt == 0:
                        self.boxes.add(
                            Box((obstacle_pos[i], self.ground_level - BOX_SIZE / 2)))

                        if random.uniform(0, 1) > 0.75:  # Plant spikes
                            for s in range(1, 4):
                                self.boxes.add(
                                    Box((obstacle_pos[i] + BOX_SIZE * s,
                                         self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height_cnt)))
                                if s < 3:
                                    self.spikes.add(Spike((obstacle_pos[i] + BOX_SIZE * s,
                                                           self.ground_level - BOX_SIZE - BOX_SIZE / 2 + 2 - BOX_SIZE * height_cnt)))
                            self.spikes.add(Lava((obstacle_pos[i] + BOX_SIZE * 4, self.ground_level)))
                        else:
                            for j in range(1, 5):
                                self.spikes.add(Lava((obstacle_pos[i] + BOX_SIZE * j, self.ground_level)))
                        self.boxes.add(Box((obstacle_pos[i] + BOX_SIZE * 4,self.ground_level - BOX_SIZE / 2 - BOX_SIZE)))
                    else:
                        self.boxes.add(
                            Box((obstacle_pos[i] + BOX_SIZE * 4,
                                 self.ground_level - BOX_SIZE / 2)))
                    height_cnt += 1
                elif beat_freqs[i] < beat_freqs[i-1]: #If next note is lower, jump down a level

                    #for j in range(0,4):
                    #    self.boxes.add(Box((obstacle_pos[i]+BOX_SIZE*j, self.ground_level - BOX_SIZE / 2 - BOX_SIZE*height_cnt)))
                    if height_cnt > 1:
                        self.boxes.add(
                            Box((obstacle_pos[i], self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height_cnt)))
                        for j in range(0, 5):
                            self.spikes.add(Lava((obstacle_pos[i] + BOX_SIZE*j,self.ground_level)))
                        height_cnt -= 1
                        self.boxes.add(Box(
                            (obstacle_pos[i] + BOX_SIZE * 4, self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height_cnt)))
                    elif height_cnt == 1:
                        self.boxes.add(
                            Box((obstacle_pos[i], self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height_cnt)))
                        for j in range(0, 4):
                            self.spikes.add(Lava((obstacle_pos[i] + BOX_SIZE * j, self.ground_level)))
                        height_cnt -= 1
                        self.boxes.add(Box(
                            (obstacle_pos[i] + BOX_SIZE * 4, self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height_cnt)))
                    elif height_cnt == 0:
                        self.boxes.add(
                            Box((obstacle_pos[i], self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height_cnt)))
                        height_cnt -= 1
                        for j in range(1, 3):
                            self.spikes.add(Spike((obstacle_pos[i] + BOX_SIZE * j,
                                                   self.ground_level - BOX_SIZE - BOX_SIZE / 2 + 2 - BOX_SIZE * height_cnt)))




            else: #No action
                if beat_freqs[i] >= beat_freqs[i - 1]:
                    if height_cnt >= 0:
                        for j in range(0,5):
                            self.boxes.add(Box((obstacle_pos[i]+BOX_SIZE*j, self.ground_level - BOX_SIZE / 2 - BOX_SIZE*height_cnt)))
                    if height_cnt > 0:
                        for j in range(0, 5):
                            self.spikes.add(Lava((obstacle_pos[i] + BOX_SIZE*j, self.ground_level)))

                    #self.boxes.add(Box((obstacle_pos[i], self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height_cnt)))
                else:
                    if height_cnt > 1:
                        self.boxes.add(Box(
                            (obstacle_pos[i], self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height_cnt)))
                        height_cnt -= 1
                        self.boxes.add(
                            Box((obstacle_pos[i] + BOX_SIZE * 4,
                                 self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height_cnt)))
                        self.boxes.add(
                            Box((obstacle_pos[i] + BOX_SIZE * 3,
                                 self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height_cnt)))

                        for j in range(0, 5):
                            self.spikes.add(Lava((obstacle_pos[i] + BOX_SIZE*j, self.ground_level)))
                    elif height_cnt == 1:
                        self.boxes.add(Box(
                            (obstacle_pos[i], self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height_cnt)))
                        height_cnt -= 1
                        self.boxes.add(
                            Box((obstacle_pos[i] + BOX_SIZE * 4,
                                 self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height_cnt)))
                        self.boxes.add(
                            Box((obstacle_pos[i] + BOX_SIZE * 3,
                                 self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height_cnt)))
                        for j in range(0, 3):
                            self.spikes.add(Lava((obstacle_pos[i] + BOX_SIZE*j, self.ground_level)))
                    elif height_cnt == 0:
                        for j in range(0, 5):
                            self.boxes.add(Box(
                                (obstacle_pos[i]+BOX_SIZE*j, self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height_cnt)))


                    #self.boxes.add(Box((obstacle_pos[i], self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height_cnt)))

            #if action_list[i]: #If JUMP
            #    if random.uniform(0, 1) > 0.7: #Add box with spike to jump over
            #        self.boxes.add(Box((obstacle_pos[i]+BOX_SIZE, self.ground_level - BOX_SIZE / 2)))
            #        self.spikes.add(Spike((obstacle_pos[i]+BOX_SIZE, self.ground_level - BOX_SIZE - BOX_SIZE / 2 + 2)))
            #    else: #Add box to jump on
            #        self.boxes.add(Box((obstacle_pos[i], self.ground_level - BOX_SIZE / 2)))


        #for o in obstacle_pos:
        #    self.boxes.add(Box((o, self.ground_level - BOX_SIZE / 2)))
        #    if random.uniform(0,1) > 0.7:
        #        self.spikes.add(Spike((o, self.ground_level - BOX_SIZE - BOX_SIZE / 2 + 2)))


    def generate_n_spikes(self,n):
        return
    def generate_n_boxes(self,n):
        return

    def get_all_obstacles(self, lower_bound, upper_bound):
        obstacles = pygame.sprite.Group()
        obstacles.add(self.platform)
        for b in self.boxes:
            if lower_bound <= b.rect.topright[0] <= upper_bound:
                obstacles.add(b)
        for s in self.spikes:
            if lower_bound <= s.rect.topright[0] <= upper_bound:
                obstacles.add(s)
        return obstacles

    def get_spikes(self, lower_bound, upper_bound):
        obstacles = pygame.sprite.Group()
        obstacles.add(self.platform)
        for s in self.spikes:
            if lower_bound <= s.rect.topright[0] <= upper_bound:
                obstacles.add(s)
        return obstacles

    def get_boxes(self, lower_bound, upper_bound):
        obstacles = pygame.sprite.Group()
        obstacles.add(self.platform)
        for b in self.boxes:
            if lower_bound <= b.rect.topright[0] <= upper_bound:
                obstacles.add(b)
        return obstacles

    def get_all_spikes(self):
        return self.spikes

    def get_all_boxes(self):
        return self.boxes
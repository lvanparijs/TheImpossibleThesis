import math
import random
from random import randrange

import pygame
import librosa
import numpy as np

from src.Box import Box
from src.Lava import Lava
from src.Platform import Platform
from src.Spike import Spike

import matplotlib.pyplot as plt
import librosa.display
from pyAudioAnalysis import audioTrainTest as att

vec = pygame.math.Vector2
BOX_SIZE = 40
JUMP = 1
NO_ACTION = 0




class Level:

    ##A level is essentially a collection of obstacles, the ground is always the same, created based on a music track

    def __init__(self, song, height, player, boxes, spikes,screen_height):
        if song is None:
            self.width = 640
            self.tempo = 0
        else:
            #TODO: Add check if level for this song has already been generated
            self.song = song
            self.action_list = []
            #self.spb = song.spb
            self.beat_times = range(0, len(self.song.beat_frames))
            self.beat_times *= self.song.spb
            self.generate_rhythm()
            #self.beat_frames = song.beat_frames


            self.height_line = []

            player.pixels_per_second = int((5*BOX_SIZE)/self.song.spb)#Desired jump distance

            player.set_velocity(player.get_jump_length())
            player.parameter_tuning(5)
            self.width = song.song_duration*player.max_vel*60  # Width of the level in pixels, determined by length of song, speed of player
            print("DONE PYIN")

            #Critics needed to be extracted
            print("CLASSIFYING")
            class_id, probability, classes = att.file_classification(self.song.file_name, "C:/Users/lvanp/PycharmProjects/TheImpossibleThesis/src/res/svm_rbf_musical_genre_6", "svm")
            print(class_id)
            print(probability)
            print(classes)
            print("DONE CLASSIFYING")

        self.boxes = boxes #Set of boxes in the level
        self.spikes = spikes #Set of spikes in the level
        self.height = height #Height of the level

        self.max_height = 6

        self.box_frequency = 2 #Amount of boxes per 100 pixels, for random generation
        self.spike_frequency = 1 #Amount of spikes per 100 pixels
        self.ground_level = int(screen_height * 0.9)#Ground level
        self.platform = Platform(vec(0, self.ground_level),self.width) #Main platform of the level
        self.boxes.add(self.platform)

    def get_lvl_data(self):
        return self.boxes,self.spikes

    def generate_flat_level(self):
        return

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

    def generate_geometry(self,vel):
        self.beat_times = range(0, len(self.beat_frames))
        self.beat_times *= self.spb
        notes = []
        print("GENERATING GEOMETRY")
        for bt in self.beat_times:
            p = self.detect_pitch(bt)
            print(p)
            if math.isnan(p):
                notes += [librosa.hz_to_note(400)]
            else:
                notes += [librosa.hz_to_note(p)]

        beat_freqs = librosa.note_to_hz(notes)
        self.generate_rhythm()

        obstacle_pos = self.beat_times * vel * 60
        height_cnt = -1
        print(len(self.beat_times) == len(beat_freqs))
        for i in range(1, len(obstacle_pos)):
            if self.action_list[i]:  # Jump
                if beat_freqs[i] == beat_freqs[i - 1]: #UP  # If on same level, add box and spike
                    if height_cnt == 0:
                        for j in range(0, 5):
                            self.boxes.add(Box((obstacle_pos[i] + BOX_SIZE * j,
                                                self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height_cnt)))
                    if height_cnt > 0:
                        for j in range(0, 5):
                            self.boxes.add(Box((obstacle_pos[i] + BOX_SIZE * j,
                                                self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height_cnt)))
                        for j in range(0, 5):
                            self.spikes.add(Lava((obstacle_pos[i] + BOX_SIZE * j, self.ground_level)))

                    # self.boxes.add(Box((obstacle_pos[i] + BOX_SIZE, self.ground_level - BOX_SIZE / 2 - BOX_SIZE*height_cnt)))
                    num_spikes = random.randint(1, 2)
                    for s in range(0, num_spikes):
                        self.spikes.add(
                            Spike((obstacle_pos[i] + BOX_SIZE + BOX_SIZE * s,
                                   self.ground_level - BOX_SIZE - BOX_SIZE / 2 + 2 - BOX_SIZE * height_cnt)))
                elif beat_freqs[i] > beat_freqs[i - 1]:  # If next note is higher, jump up a level
                    if height_cnt > 0:
                        self.boxes.add(
                            Box((obstacle_pos[i], self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height_cnt)))

                        if random.uniform(0, 1) > 0.75:  # Plant spikes
                            for s in range(1, 4):
                                self.boxes.add(
                                    Box((obstacle_pos[i] + BOX_SIZE * s,
                                         self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height_cnt)))
                                if s < 3:
                                    self.spikes.add(Spike((obstacle_pos[i] + BOX_SIZE * s,
                                                           self.ground_level - BOX_SIZE - BOX_SIZE / 2 + 2 - BOX_SIZE * height_cnt)))
                        for j in range(0, 5):
                            self.spikes.add(Lava((obstacle_pos[i] + BOX_SIZE * j, self.ground_level)))

                        self.boxes.add(
                            Box((obstacle_pos[i] + BOX_SIZE * 4,
                                 self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height_cnt - BOX_SIZE)))
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
                        self.boxes.add(
                            Box((obstacle_pos[i] + BOX_SIZE * 4, self.ground_level - BOX_SIZE / 2 - BOX_SIZE)))
                    else:
                        self.boxes.add(
                            Box((obstacle_pos[i] + BOX_SIZE * 4,
                                 self.ground_level - BOX_SIZE / 2)))
                    height_cnt += 1
                elif beat_freqs[i] < beat_freqs[i - 1]:  # If next note is lower, jump down a level

                    # for j in range(0,4):
                    #    self.boxes.add(Box((obstacle_pos[i]+BOX_SIZE*j, self.ground_level - BOX_SIZE / 2 - BOX_SIZE*height_cnt)))
                    if height_cnt > 1:
                        self.boxes.add(
                            Box((obstacle_pos[i], self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height_cnt)))
                        for j in range(0, 5):
                            self.spikes.add(Lava((obstacle_pos[i] + BOX_SIZE * j, self.ground_level)))
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




            else:  # No action
                if beat_freqs[i] >= beat_freqs[i - 1]:
                    if height_cnt >= 0:
                        for j in range(0, 5):
                            self.boxes.add(Box((obstacle_pos[i] + BOX_SIZE * j,
                                                self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height_cnt)))
                    if height_cnt > 0:
                        for j in range(0, 5):
                            self.spikes.add(Lava((obstacle_pos[i] + BOX_SIZE * j, self.ground_level)))

                    # self.boxes.add(Box((obstacle_pos[i], self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height_cnt)))
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
                            self.spikes.add(Lava((obstacle_pos[i] + BOX_SIZE * j, self.ground_level)))
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
                            self.spikes.add(Lava((obstacle_pos[i] + BOX_SIZE * j, self.ground_level)))
                    elif height_cnt == 0:
                        for j in range(0, 5):
                            self.boxes.add(Box(
                                (obstacle_pos[i] + BOX_SIZE * j,
                                 self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height_cnt)))

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

        print(self.beat_frames)
        for bf in self.beat_frames:
            f0 = librosa.yin(self.y[old_bf:bf], fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))
            notes = []

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
        #print("BEAT FREQS")
        #print(beat_freqs)

        self.generate_rhythm()

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

    def generate_geometry_from_grammar(self,vel):
        self.beat_times = range(0, len(self.beat_frames))
        self.beat_times *= self.spb
        notes = []
        print("GENERATING GEOMETRY")
        for bt in self.beat_times:
            p = self.detect_pitch(bt)
            print(p)
            if math.isnan(p):
                notes += [librosa.hz_to_note(400)]
            else:
                notes += [librosa.hz_to_note(p)]

        beat_freqs = librosa.note_to_hz(notes)
        self.generate_rhythm()

        obstacle_pos = self.beat_times * vel * 60
        height_cnt = 0 #Floor == 0

        for i in range(1, len(obstacle_pos)):
            if self.action_list[i]:  # Jump
                if beat_freqs[i] == beat_freqs[i - 1]: #FLAT  # If on same level, add box and spike
                    #flat_blocks_spikes, flat_jump_lava, spikes_flat(1..3)
                    if height_cnt > 0: #off the floor
                        if random.uniform(0,1) > 0.8:
                            self.flat_jump_lava(obstacle_pos[i],height_cnt)
                        else:
                            n_spikes = random.randint(1,4)
                            if n_spikes == 1:
                                self.flat_blocks_spike_1(obstacle_pos[i],height_cnt)
                            elif n_spikes == 2:
                                self.flat_blocks_spike_2(obstacle_pos[i],height_cnt)
                            elif n_spikes == 3:
                                self.flat_blocks_spike_3(obstacle_pos[i],height_cnt)

                    else: #floor
                        n_spikes = random.randint(1,4)
                        if n_spikes == 1:
                            self.spikes_flat_1(obstacle_pos[i], height_cnt)
                        elif n_spikes == 2:
                            self.spikes_flat_2(obstacle_pos[i], height_cnt)
                        elif n_spikes == 3:
                            self.spikes_flat_3(obstacle_pos[i], height_cnt)

                elif beat_freqs[i] > beat_freqs[i - 1]:  # If next note is higher, jump up a level
                    if random.uniform(0, 1) > 0.3:
                        self.jump_up_1(obstacle_pos[i], height_cnt)
                        height_cnt += 1
                    else:
                        self.jump_up_2(obstacle_pos[i], height_cnt)
                        height_cnt += 2

                elif beat_freqs[i] < beat_freqs[i - 1]:  # If next note is lower, jump down a level\
                    if height_cnt > 0:
                        self.jump_down(obstacle_pos[i], height_cnt)
                        height_cnt -= 1
                    else:
                        self.empty_platform()

            else:  # No action
                if beat_freqs[i] >= beat_freqs[i - 1]:
                    if height_cnt > 0: #Off the ground
                        self.flat_blocks(obstacle_pos[i], height_cnt)
                    else: #On the ground
                        self.empty_platform()
                else:
                    if height_cnt > 0: #Off the floor
                        self.fall_down(obstacle_pos[i], height_cnt)
                        height_cnt -= 1
                    else:
                        self.empty_platform()
            height_cnt = max(0,height_cnt)

    def generate_geometry_from_grammar_rnd(self,vel):
        #self.beat_times = range(0, len(self.song.beat_frames))
        #self.beat_times *= self.song.spb
        notes = []
        print("GENERATING GEOMETRY")

        #self.generate_rhythm()

        obstacle_pos = self.beat_times * vel * 60
        height_cnt = 0 #Floor == 0
        self.height_line += [height_cnt]
        for i in range(1, len(obstacle_pos)):
            if self.action_list[i]:  # Jump
                rnd_direction = random.uniform(0, 1) #Randomise the directions
                if rnd_direction > 0.67: #UP
                    rnd_threshold = random.uniform(0, 1)
                    if random.uniform(0, 1) > rnd_threshold:
                        self.jump_up_1(obstacle_pos[i], height_cnt)
                        height_cnt += 1
                    else:
                        self.jump_up_2(obstacle_pos[i], height_cnt)
                        height_cnt += 2
                elif rnd_direction > 0.33: #FLAT
                    if height_cnt > 0: #off the floor
                        rnd_threshold = random.uniform(0,1)
                        if random.uniform(0,1) > rnd_threshold:
                            self.flat_jump_lava(obstacle_pos[i],height_cnt)
                        else:
                            n_spikes = random.randint(1,3)
                            if n_spikes == 4 or n_spikes == 0:
                                print("PROBLEM 1")

                            if n_spikes == 1:
                                self.flat_blocks_spike_1(obstacle_pos[i],height_cnt)
                            elif n_spikes == 2:
                                self.flat_blocks_spike_2(obstacle_pos[i],height_cnt)
                            elif n_spikes == 3:
                                self.flat_blocks_spike_3(obstacle_pos[i],height_cnt)

                    else: #floor
                        height_cnt = 0
                        n_spikes = random.randint(1,3)
                        if n_spikes == 4 or n_spikes == 0:
                            print("PROBLEM 2")
                        if n_spikes == 1:
                            self.spikes_flat_1(obstacle_pos[i], height_cnt)
                        elif n_spikes == 2:
                            self.spikes_flat_2(obstacle_pos[i], height_cnt)
                        elif n_spikes == 3:
                            self.spikes_flat_3(obstacle_pos[i], height_cnt)

                else: #DOWN and on the floor = FLAT
                    if height_cnt > 0:
                        self.jump_down(obstacle_pos[i], height_cnt)
                        height_cnt -= 1
                    else:
                        height_cnt = 0
                        n_spikes = random.randint(1,3)
                        if n_spikes == 4 or n_spikes == 0:
                            print("PROBLEM 3")
                        if n_spikes == 1:
                            self.spikes_flat_1(obstacle_pos[i], height_cnt)
                        elif n_spikes == 2:
                            self.spikes_flat_2(obstacle_pos[i], height_cnt)
                        elif n_spikes == 3:
                            self.spikes_flat_3(obstacle_pos[i], height_cnt)

            else:
                rnd_direction = random.uniform(0, 1)  # Randomise the directions
                if rnd_direction > 0.67:  # UP/FLAT
                    self.flat_blocks(obstacle_pos[i], height_cnt)
                else:
                    if height_cnt > 0: #Off the floor
                        self.fall_down(obstacle_pos[i], height_cnt)
                        height_cnt -= 1
                    else:
                        self.empty_platform()
            height_cnt = max(0,height_cnt)
            height_cnt = min(self.max_height,height_cnt)
            self.height_line += [height_cnt]

    def generate_final_level(self,vel):
        n_lvls = 100
        for i in range(0,n_lvls):
            self.generate_geometry_from_grammar_rnd(vel)

    def get_next_geometry_piece(self): #Geomety Generation Grammar
        #Picks a piece at random based on whether it has to go down(-1), flat(0), up(1)
        return

    def empty_platform(self):
        return

    def spikes_flat_1(self,pos,height):
        self.spikes.add(Spike((pos + BOX_SIZE,
                       self.ground_level - BOX_SIZE / 2 + 2 - BOX_SIZE * height)))

    def spikes_flat_2(self,pos,height):
        self.spikes.add(Spike((pos + BOX_SIZE,
                               self.ground_level - BOX_SIZE / 2 + 2 - BOX_SIZE * height)))
        self.spikes.add(Spike((pos + BOX_SIZE + BOX_SIZE,
                               self.ground_level - BOX_SIZE / 2 + 2 - BOX_SIZE * height)))

    def spikes_flat_3(self,pos,height):
        self.spikes.add(Spike((pos + BOX_SIZE,
                               self.ground_level - BOX_SIZE / 2 + 2 - BOX_SIZE * height)))
        self.spikes.add(Spike((pos + BOX_SIZE*2,
                               self.ground_level - BOX_SIZE / 2 + 2 - BOX_SIZE * height)))
        self.spikes.add(Spike((pos + BOX_SIZE*3,
                               self.ground_level - BOX_SIZE / 2 + 2 - BOX_SIZE * height)))

    def fall_down(self,pos,height):
        if height > 1:
            for j in range(0, 5):
                self.spikes.add(Lava((pos + BOX_SIZE * j, self.ground_level)))
        elif height > 0:
            for j in range(0, 3):
                self.spikes.add(Lava((pos + BOX_SIZE * j, self.ground_level)))

        self.boxes.add(Box(
            (pos, self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height)))
        height -= 1
        self.boxes.add(
            Box((pos + BOX_SIZE * 4,
                 self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height)))
        self.boxes.add(
            Box((pos + BOX_SIZE * 3,
                 self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height)))

    def jump_down(self,pos,height):
        if height > 0: #Off the floor
            self.boxes.add(
                Box((pos, self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height)))
            if height == 1:
                for j in range(0, 4):
                    self.spikes.add(Lava((pos + BOX_SIZE * j, self.ground_level)))
            else:
                for j in range(0, 5):
                    self.spikes.add(Lava((pos + BOX_SIZE * j, self.ground_level)))
            height -= 1
            self.boxes.add(Box(
                (pos + BOX_SIZE * 4, self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height)))
        else: #One above floor, jump down to floor
            self.boxes.add(
                Box((pos, self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height)))

    def jump_up_1(self,pos,height):
        if height > 0: #Off the floor
            self.boxes.add(
                Box((pos, self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height)))

            for j in range(0, 5):
                self.spikes.add(Lava((pos + BOX_SIZE * j, self.ground_level)))

            self.boxes.add(
                Box((pos + BOX_SIZE * 4,
                     self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height - BOX_SIZE)))
        else:
            self.boxes.add(
                Box((pos + BOX_SIZE * 4, self.ground_level - BOX_SIZE / 2 - BOX_SIZE)))
            self.spikes.add(Lava((pos + BOX_SIZE * 4, self.ground_level)))
            self.spikes_flat_3(pos, height)


    def jump_up_2(self,pos,height):
        if height > 0: #Off the floor
            self.boxes.add(
                Box((pos, self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height)))

            for j in range(0, 5):
                self.spikes.add(Lava((pos + BOX_SIZE * j, self.ground_level)))

            self.boxes.add(
                Box((pos + BOX_SIZE * 4,
                     self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height - BOX_SIZE*2)))
            self.boxes.add(
                Box((pos + BOX_SIZE * 3,
                     self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height - BOX_SIZE*2)))
        else:
            self.boxes.add(
                Box((pos + BOX_SIZE * 4,
                     self.ground_level - BOX_SIZE / 2 - BOX_SIZE * 2)))
            self.spikes.add(Lava((pos + BOX_SIZE * 4, self.ground_level)))
            self.spikes_flat_3(pos,height)

    def flat_blocks(self,pos,height):
        for i in range(0,5):
            self.boxes.add(Box((pos + BOX_SIZE * i,
                            self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height)))

        if height > 0:
            for j in range(0, 5):
                self.spikes.add(Lava((pos + BOX_SIZE * j, self.ground_level)))

    def flat_blocks_spike_1(self,pos,height):
        if height > 0: #Off the floor
            for j in range(0, 5):
                self.boxes.add(Box((pos + BOX_SIZE * j,
                                    self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height)))
            if height >= 1:
                for j in range(0, 5):
                    self.spikes.add(Lava((pos + BOX_SIZE * j, self.ground_level)))

        self.spikes.add(
            Spike((pos + BOX_SIZE + BOX_SIZE,
                   self.ground_level - BOX_SIZE - BOX_SIZE / 2 + 2 - BOX_SIZE * height)))

    def flat_blocks_spike_2(self,pos,height):
        print(height)
        if height > 0: #Off the floor
            for j in range(0, 5):
                self.boxes.add(Box((pos + BOX_SIZE * j,
                                    self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height)))
            if height >= 1:
                for j in range(0, 5):
                    self.spikes.add(Lava((pos + BOX_SIZE * j, self.ground_level)))

        self.spikes.add(
            Spike((pos + BOX_SIZE,
                   self.ground_level - BOX_SIZE - BOX_SIZE / 2 + 2 - BOX_SIZE * height)))

        self.spikes.add(
            Spike((pos + BOX_SIZE*2,
                   self.ground_level - BOX_SIZE - BOX_SIZE / 2 + 2 - BOX_SIZE * height)))

    def flat_blocks_spike_3(self,pos,height):
        print(height)
        if height > 0: #Off the floor
            for j in range(0, 5):
                self.boxes.add(Box((pos + BOX_SIZE * j,
                                    self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height)))
            if height >= 1:
                for j in range(0, 5):
                    self.spikes.add(Lava((pos + BOX_SIZE * j, self.ground_level)))

        self.spikes.add(
            Spike((pos + BOX_SIZE,
                   self.ground_level - BOX_SIZE - BOX_SIZE / 2 + 2 - BOX_SIZE * height)))

        self.spikes.add(
            Spike((pos + BOX_SIZE * 2,
                   self.ground_level - BOX_SIZE - BOX_SIZE / 2 + 2 - BOX_SIZE * height)))

        self.spikes.add(
            Spike((pos + BOX_SIZE * 3,
                   self.ground_level - BOX_SIZE - BOX_SIZE / 2 + 2 - BOX_SIZE * height)))

    def flat_jump_lava(self,pos,height):
        self.boxes.add(Box((pos, self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height)))
        self.boxes.add(Box((pos + BOX_SIZE * 4, self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height)))
        self.spikes.add(Lava((pos + BOX_SIZE, self.ground_level)))
        self.spikes.add(Lava((pos + BOX_SIZE * 2, self.ground_level)))
        self.spikes.add(Lava((pos + BOX_SIZE * 3, self.ground_level)))
        if height > 0:
            self.spikes.add(Lava((pos, self.ground_level)))
            self.spikes.add(Lava((pos + BOX_SIZE * 4, self.ground_level)))

    def generate_rhythm(self):
        for b in self.beat_times: #Generates actions for the times of the beats
            if random.uniform(0,1) > 0.7:
                self.action_list += [NO_ACTION]
            else:
                self.action_list += [JUMP]
        return

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

    def add_jump_up_one(self, pos, height):
        #jump_up_one | jump_up_two
        return

    def add_jump_up_one(self, pos, height):
        return

    def add_jump_up_two(self, pos, height):
        return

    def add_jump_down(self, pos, height):
        return

    def add_jump_flat(self, pos, height):
        if height == 0:
            for j in range(0, 5):
                self.boxes.add(
                    Box((pos + BOX_SIZE * j, self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height)))
        if height > 0:
            for j in range(0, 5):
                self.boxes.add(
                    Box((pos + BOX_SIZE * j, self.ground_level - BOX_SIZE / 2 - BOX_SIZE * height)))
            for j in range(0, 5):
                self.spikes.add(Lava((pos + BOX_SIZE * j, self.ground_level)))
        return

    def add_no_jump_up(self, pos, height):
        return

    def add_no_jump_down(self, pos, height):
        return

    def add_no_jump_flat(self, pos, height):
        return
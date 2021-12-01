import math

import librosa
from pyAudioAnalysis import audioTrainTest as att
import numpy as np


class Song:

    def __init__(self, file_name, analyse):
        if file_name is None:
            print("NO FILENAME GIVEN")
        else:

            self.file_name = file_name  # Path to the music file
            self.y, self.sampling_rate = librosa.load(self.file_name)  # Audio time series and sampling rate of the song
            self.song_duration = librosa.get_duration(y=self.y, sr=self.sampling_rate)  # Time in s
            self.tempo, self.beat_frames = librosa.beat.beat_track(y=self.y, sr=self.sampling_rate)
            self.bps = self.tempo / 60  # beats per second

            self.spb = 1 / self.bps  # Seconds per beat

            self.beat_times = range(0, len(self.beat_frames))
            self.beat_times *= self.spb

            if analyse:
                class_id, probability, classes = att.file_classification(self.file_name,
                                                                         "res/svm_rbf_musical_genre_6",
                                                                         "svm")
                print("DONE CLASSIFYING SONG: " + classes[int(class_id)])
                self.genre = classes[int(class_id)]

                self.notes = []
                self.value = 0

                self.f0, voiced_flag, voiced_probs = librosa.pyin(self.y, fmin=librosa.note_to_hz('C2'),
                                                                  fmax=librosa.note_to_hz('C7'))
                self.times_f0 = librosa.times_like(self.f0)

                f0_notes = []
                self.height_notes = []

                print("HEIGHT NOTES")
                old_p = 400  # starting value
                for bt in self.beat_times:
                    # min(self.times_f0, key=lambda x: abs(x - bt))
                    f0_notes += [self.f0[np.where(self.times_f0 == min(self.times_f0, key=lambda x: abs(x - bt)))]]
                    p = self.detect_pitch(bt)
                    if math.isnan(p):
                        self.notes += [librosa.hz_to_note(old_p)]
                    else:
                        self.notes += [librosa.hz_to_note(p)]
                        old_p = p

                height = 0
                old_f = None
                for f in f0_notes:
                    if old_f is None:
                        old_f = f
                    if f > old_f:
                        height += 1
                    elif f < old_f:
                        height -= 1
                    height = max(0, height)
                    self.height_notes += [height]
                    old_f = f


    def detect_pitch(self, t):
        i = len(self.times_f0) - 1
        note = 0
        while t < self.times_f0[i]:
            note = self.f0[i]
            i -= 1
        return note
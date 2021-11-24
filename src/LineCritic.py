import math

import librosa
import numpy as np

from src.Critic import Critic


class LineCritic(Critic):
    def __init__(self, y, beat_frames, spb):
        self.beat_times = range(0, len(beat_frames))
        self.beat_times *= spb
        self.notes = []
        self.value = 0
        print("PYIN")
        self.f0, voiced_flag, voiced_probs = librosa.pyin(y, fmin=librosa.note_to_hz('C2'),
                                                     fmax=librosa.note_to_hz('C7'))
        self.times_f0 = librosa.times_like(self.f0)
        #D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
        #print(D)
        #fig, ax = plt.subplots()
        #img = librosa.display.specshow(D, x_axis='time', y_axis='log', ax=ax)
        #print(img)
        #ax.set(title='pYIN fundamental frequency estimation')
        #fig.colorbar(img, ax=ax, format="%+2.f dB")
        #ax.plot(times, f0, label='f0', color='cyan', linewidth=3)
        #ax.legend(loc='upper right')
        #plt.show()
        #print(len(self.f0))
        #print(self.times_f0)
        #print(self.beat_times)

        f0_notes = []
        self.height_notes = []

        print("HEIGHT NOTES")
        old_p = 400 #tarting value
        for bt in self.beat_times:
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
            height = max(0,height)
            self.height_notes += [height]
            old_f = f





    def critique(self, lvl):
        #Returns a score between 0-1 based on the particular critics scope
        print(lvl.height_line)
        print(self.height_notes)
        array1 = np.array(lvl.height_line)
        array2 = np.array(self.height_notes)
        subtracted_array = np.subtract(array1, array2)
        subtracted = list(subtracted_array)
        print(subtracted)
        return -np.sum(np.square(subtracted)) #sum Squared difference

    def detect_pitch(self, t):
        i = len(self.times_f0) - 1
        note = 0
        while t < self.times_f0[i]:
            note = self.f0[i]
            i -= 1
        return note
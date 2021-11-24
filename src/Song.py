import librosa


class Song:

    def __init__(self, file_name):
        if file_name is None:
            print("NO FILENAME GIVEN")
        else:
            self.file_name = file_name  # Path to the music file
            self.y, self.sampling_rate = librosa.load(self.file_name)  # Audio time series and sampling rate of the song
            self.song_duration = librosa.get_duration(y=self.y, sr=self.sampling_rate)  # Time in s
            self.tempo, self.beat_frames = librosa.beat.beat_track(y=self.y, sr=self.sampling_rate)
            self.bps = self.tempo / 60  # beats per second

            self.spb = 1 / self.bps  # Seconds per beat
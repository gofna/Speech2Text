from pydub import AudioSegment
import math


class SplitWavAudioMubin():
    def __init__(self, folder, filename, savePath):
        self.folder = folder
        self.filename = filename
        self.filepath = folder + '\\' + filename
        self.savePath = savePath

        self.audio = AudioSegment.from_wav(self.filepath)

    def get_duration(self):
        return self.audio.duration_seconds

    def single_split(self, from_min, to_min, split_filename):
        t1 = from_min * 1000
        t2 = to_min * 1000
        split_audio = self.audio[t1:t2]
        split_audio.export(self.savePath + '\\' + split_filename, format="wav")

    def multiple_split(self, min_per_split):
        total_mins = math.ceil(self.get_duration())
        for i in range(0, total_mins, min_per_split):
            split_fn = str(i) + '_' + self.filename
            self.single_split(i, i + min_per_split, split_fn)
            print(str(i) + ' Done')
            if i == total_mins - min_per_split:
                print('All splited successfully')


# folder = 'C:\\Users\\Maor\\PycharmProjects\\speech2text\\audios'
# file = 'Bdb001.interaction.wav'
# split_wav = SplitWavAudioMubin(folder, file)
# split_wav.multiple_split(min_per_split=10)

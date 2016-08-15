# import winsound


class Audio(object):
    def __init__(self):
        self.is_playing = False

    def play(self):
        # winsound.MessageBeep(winsound.MB_OK)
        # winsound.Beep(600, duration)
        # winsound.PlaySound('SystemAsterisk', winsound.SND_ALIAS|winsound.SND_ASYNC)
        if not self.is_playing:
            print('Audio.play')
        self.is_playing = True

    def stop(self):
        # winsound.PlaySound(None, 0)
        if self.is_playing:
            print('Audio.stop')

player = Audio()

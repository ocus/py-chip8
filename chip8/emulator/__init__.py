from chip8.emulator.Input import Input
from chip8.emulator.Chip8Utils import Chip8Utils


class Emulator(object):
    STOPPED = 'stopped',
    RUNNING = 'running',
    PAUSED = 'paused',
    TERMINATED = 'terminated',

    def __init__(self, rom_path=None, auto_start=False, debug=False, kb_input=None):
        self.chip8 = None
        self.rom_path = rom_path
        self.status = self.STOPPED
        self.step_counter = 0
        if not kb_input:
            kb_input = Input()
        self.kb_input = kb_input
        if debug:
            debug = True
        self.debug = debug

        if auto_start:
            self._loop()

    def _loop(self):
        try:
            while True:
                step_counter = self.step_counter
                while self.get_status() in [self.STOPPED, self.PAUSED] and step_counter == self.step_counter:
                    continue
                if self.status == self.TERMINATED:
                    break
                if self.chip8:  # might not be available already on STARTED
                    self._before_cycle(self.chip8.get_cycle_counter())
                    counter = self.chip8.cycle()
                    self._after_cycle(counter)
        except Exception as e:
            self._change_status(self.STOPPED)
            self._on_crash(e)
            raise e
            # print('Emulator crashed !', file=o)
            # print('  %s: %s' % (e.__class__.__name__, e), file=o)S
            # self.chip8.debug_dump(file=o)

    def get_status(self):
        return self.status

    def start(self):
        if self._change_status(self.RUNNING):
            self.chip8 = Chip8Utils.create_from_rom(path=self.rom_path, input_kb=self.kb_input)
            self._on_start()

    def un_pause(self):
        if self._change_status(self.RUNNING):
            self._on_un_pause()

    def toggle_pause(self):
        if self.status == self.PAUSED:
            self.un_pause()
        else:
            self.pause()

    def stop(self):
        if self._change_status(self.STOPPED):
            self._on_stop()

    def pause(self):
        if self.status != self.PAUSED and self._change_status(self.PAUSED):
            self._on_pause()

    def terminate(self):
        if self._change_status(self.TERMINATED):
            self._on_stop()
            self._on_terminate()

    def step(self):
        self.step_counter += 1

    def _change_status(self, status):
        if self.status == status:
            return False
        print('new status', status)
        self.status = status
        return True

    def _before_cycle(self, counter):
        pass

    def _after_cycle(self, counter):
        pass

    def _on_start(self):
        pass

    def _on_stop(self):
        pass

    def _on_pause(self):
        pass

    def _on_terminate(self):
        pass

    def _on_un_pause(self):
        pass

    def _on_crash(self, e):
        pass

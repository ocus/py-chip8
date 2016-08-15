from distutils.cmd import Command
from distutils.errors import DistutilsOptionError

from chip8.emulator import Emulator
from chip8.emulator.TkEmulator import TkEmulator


class RunEmulatorCommand(Command):
    description = 'run a Chip8 emulator'
    user_options = [
        ('rom=', None, 'path to the ROM file'),
        ('debug', None, 'enable debug'),
        ('emulator=', None, 'the emulator class (default: emulator)'),
    ]

    emulators = {
        'emulator': Emulator,
        'tk': TkEmulator,
    }

    def __init__(self, dist):
        Command.__init__(self, dist)
        self.rom = None
        self.debug = False
        self.emulator = 'emulator'

    def initialize_options(self):
        pass

    def finalize_options(self):
        if self.rom:
            self.ensure_filename('rom')
        if not self.emulator or self.emulator not in self.emulators:
            raise DistutilsOptionError('Emulator "{}" does not exist'.format(self.emulator))

    def run(self):
        e = self.emulators[self.emulator](rom_path=self.rom, auto_start=True, debug=self.debug)

import os
import unittest

from chip8.emulator.Chip8Utils import Chip8Utils


class TimersTest(unittest.TestCase):
    """
    Until now we have only executed instructions manually. Eventually for a
    working virtual machine we will need to load a program from an external
    source.

    This provided Chip8Utils class has utility methods for creating a Chip8
    system with memory loaded from a file.
    """

    def setUp(self):
        path = os.path.join(os.path.dirname(__file__), 'resources', 'E05TimerLoop.ch8')
        self.chip8 = Chip8Utils.create_from_rom(path)
        self.chip8.execute(0x6064)
        self.chip8.execute(0x6127)
        self.chip8.execute(0x6212)
        self.chip8.execute(0x63AE)
        self.chip8.execute(0x64FF)
        self.chip8.execute(0x65B4)
        self.chip8.execute(0x6642)
        self.chip8.execute(0x6F25)

    def testDelayTimerOpcodes(self):
        """
        As documented in clock_execution_and_memory_test.py, we will modify the cycle method to count down the
        delay timer.

        There are also timer instructions to set the timer to begin a countdown.

        FX15 Set the timer to VX FX07 Store the value of the timer to VX

        The timer works on a 60 hertz cycle. IE if you set the timer to 60 it
        will countdown to 0 over the course of a second.
        """
        self.chip8.execute(0xF015)  # Set timer to 0x64
        self.chip8.execute(0xF107)  # Read timer into V1
        self.assertEquals(0x64, self.chip8.get_v1())

    # @timeout_decorator.timeout(300, use_signals=False)
    def testDelayTimerCountdown(self):
        while self.chip8.get_v5() != 255:
            self.chip8.cycle()

    def testSoundTimer(self):
        self.chip8.execute(0xF018)  # Set timer to 0x64
        self.chip8.cycle()

    def testEmitSoundTimer(self):
        path = os.path.join(os.path.dirname(__file__), 'resources', 'E05SoundLoop.ch8')
        chip8 = Chip8Utils.create_from_rom(path)
        while chip8.get_v5() != 255:
            chip8.cycle()

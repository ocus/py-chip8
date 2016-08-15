import os
import unittest

from chip8.Chip8Utils import Chip8Utils


class ClockExecutionAndMemoryTest(unittest.TestCase):
    """
    Until now we have only executed instructions manually. Eventually for a
    working virtual machine we will need to load a program from an external
    source.

    This provided Chip8Utils class has utility methods for creating a Chip8
    system with memory loaded from a file.
    """

    def setUp(self):
        self.chip8 = Chip8Utils.create_from_rom(os.path.join(os.path.dirname(__file__), 'resources', 'E03TestRom.ch8'))

    def testCycle(self):
        """
        A cycle loop of the chip8 processor should

        fetch the instruction pointed at by the PC
        increment the PC
        decode the instruction
        execute the instruction
        repeat

        This will be modified slightly in timers_test.py to update timers as well.

        Some notes, an instruction is two bytes, however the memory is addressed
        as bytes.  This means you will need to load two bytes and combine them
        into a single instruction.
        """
        self.chip8.cycle()
        self.chip8.cycle()
        self.chip8.cycle()
        self.chip8.cycle()
        self.assertEquals(0x15, self.chip8.get_v0())
        self.assertEquals(0x20, self.chip8.get_v1())
        self.assertEquals(0x25, self.chip8.get_v2())
        self.assertEquals(0x30, self.chip8.get_v3())
        self.assertEquals(0x208, self.chip8.get_pc())

import os
import unittest

from chip8.emulator.Chip8Utils import Chip8Utils
from chip8.emulator.Input import Input


class KeypadInputTest(unittest.TestCase):
    """
    Chip-8 has support for a 16 button keypad input. The keys are assigned values
    from 0x0 - 0xF. The mapping from your keyboard/input device to chip8
    shouldn't matter for these tests.
    """

    def setUp(self):
        self.input = Input()
        path = os.path.join(os.path.dirname(__file__), 'resources', 'E06KeypadLoop.ch8')
        self.chip8 = Chip8Utils.create_from_rom(path, input_kb=self.input)
        self.chip8.execute(0x6064)
        self.chip8.execute(0x6127)
        self.chip8.execute(0x6212)
        self.chip8.execute(0x63AE)
        self.chip8.execute(0x64FF)
        self.chip8.execute(0x65B4)
        self.chip8.execute(0x6642)
        self.chip8.execute(0x6F25)

    def tearDown(self):
        self.input.unpress()

    def testChip8WaitsForKeyboardInput(self):
        """
        The opcode FX0A will wait for a key press and store its value into
        register VX.
         
        This test will execute the opcode and then call cycle several times.  As
        long as the program counter does not increment we will assume that chip8
        is not executing.
        """
        pc = self.chip8.get_pc()
        self.chip8.cycle()
        self.chip8.cycle()
        self.chip8.cycle()
        self.chip8.cycle()
        self.assertEquals(pc, self.chip8.get_pc())

    def testChip8ContinuesAfterKeyboardInput(self):
        pc = self.chip8.get_pc()
        self.chip8.cycle()
        self.chip8.cycle()
        self.assertEquals(pc, self.chip8.get_pc())
        
        self.input.press(0xA)
        self.chip8.cycle()
        self.chip8.cycle()
        self.assertEquals(0xA, self.chip8.get_v6())

    def skipIfPressed(self):
        """
        The next opcode will skip the next instruction until the keypress matches
        a value in a certain register.
         
        EX9E : Skip the next instruction of the key corresponding to the value in
        VX is pressed.
        """
        self.input.press(0x1)
        self.chip8.execute(0x6002)  # Store 0x02 into V0
        self.chip8.execute(0xE09E)  # Skip if 0x02 is pressed (it isn't)
        self.assertEquals(0x200, self.chip8.get_pc())
        
        self.input.press(0x2)
        self.chip8.execute(0x6002)  # Store 0x02 into V0
        self.chip8.execute(0xE09E)  # Skip if 0x02 is pressed (it is)
        self.assertEquals(0x202, self.chip8.get_pc())

    def skipIfNotPressed(self):
        """
        The next opcode will not skip the next instruction if the keypress
        matches a value in a certain register.

        EXA1 : Skip the next instruction of the key corresponding to the value in
        VX is not pressed.
        """
        self.input.press(0x1)
        self.chip8.execute(0x6002)  # Store 0x02 into V0
        self.chip8.execute(0xE0A1)  # Skip if 0x02 is not pressed (it isn't)
        self.assertEquals(0x202, self.chip8.get_pc())
        
        self.input.press(0x2)
        self.chip8.execute(0x6002)  # Store 0x02 into V0
        self.chip8.execute(0xE0A1)  # Skip if 0x02 is pressed (it is)
        self.assertEquals(0x202, self.chip8.get_pc())

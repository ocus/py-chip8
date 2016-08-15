import unittest

from chip8.emulator.Chip8 import Chip8


class UtilitiesTest(unittest.TestCase):
    """
    Chip 8 has a few opcodes which are convenient utility methods.
    """

    def setUp(self):
        self.chip8 = Chip8()
        self.chip8.execute(0x6064)
        self.chip8.execute(0x6127)
        self.chip8.execute(0x6212)
        self.chip8.execute(0x63AE)
        self.chip8.execute(0x64FF)
        self.chip8.execute(0x65B4)
        self.chip8.execute(0x6642)
        self.chip8.execute(0x6F25)

    def testBCD(self):
        """
        FX33 : Convert the value in VX to decimal and store each digit in I, I+1,
        and I+2 along with any leading 0s.
        """
        self.chip8.execute(0xA200)

        self.chip8.execute(0xF033)
        memory = self.chip8.get_memory()
        self.assertEquals(1, memory[0x200])
        self.assertEquals(0, memory[0x201])
        self.assertEquals(0, memory[0x202])

        self.chip8.execute(0xF133)
        memory = self.chip8.get_memory()
        self.assertEquals(0, memory[0x200])
        self.assertEquals(3, memory[0x201])
        self.assertEquals(9, memory[0x202])

        self.chip8.execute(0xF433)
        memory = self.chip8.get_memory()
        self.assertEquals(2, memory[0x200])
        self.assertEquals(5, memory[0x201])
        self.assertEquals(5, memory[0x202])

    def copyToMemory(self):
        """
        Chip8 has the ability to copy a range of registers to memory.
        FX55 : Store the values of registers V0 -> VX to memory addresses I -> I + X.
        Set I to I + X + 1 afterward.
        """
        self.chip8.execute(0xA200)
        self.chip8.execute(0xF355)
        
        memory = self.chip8.get_memory()
        
        self.assertEquals(0x64, memory[0x200])
        self.assertEquals(0x27, memory[0x201])
        self.assertEquals(0x12, memory[0x202])
        self.assertEquals(0xAE, memory[0x203])
        self.assertEquals(0x204, self.chip8.get_i_register())

    def copyFromMemory(self):
        """
        Chip8 has the ability to copy a range of memory to registers.
        FX65 : Store the values of memory addresses I -> I + X to registers V0 -> VX.
        Set I to I + X + 1 afterward.
        """
        self.chip8.execute(0xA200)
        self.chip8.execute(0xF355)
        
        memory = self.chip8.get_memory()
        
        self.assertEquals(0x64, memory[0x200])
        self.assertEquals(0x27, memory[0x201])
        self.assertEquals(0x12, memory[0x202])
        self.assertEquals(0xAE, memory[0x203])
        self.assertEquals(0x204, self.chip8.get_i_register())
        
        self.chip8.execute(0xA200)
        self.chip8.execute(0x6000)
        self.chip8.execute(0x6100)
        self.chip8.execute(0x6200)
        self.chip8.execute(0x6300)
        self.chip8.execute(0xF365)

        self.assertEquals(0x64, self.chip8.get_v0())
        self.assertEquals(0x27, self.chip8.get_v1())
        self.assertEquals(0x12, self.chip8.get_v2())
        self.assertEquals(0xAE, self.chip8.get_v3())
        self.assertEquals(0x204, self.chip8.get_i_register())


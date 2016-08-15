import unittest

from chip8.Chip8 import Chip8


class ClockExecutionAndMemoryTest(unittest.TestCase):
    """
    This test suite will work with flow control op codes. They will adjust the
    program counter to change the next command which will be executed.
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

    def testJump(self):
        """
        Jump instructions are the most basic flow control. They simply tell the
        processor to start executing programs from a different area of memory.

        Chip-8 has two jump instructions : 1NNN This instruction sets the program
        counter to execute from memory address NNN BNNN This instruction sets the
        program counter to execute from memory address (NNN + V0)
        """
        self.chip8.execute(0x1DAE)
        self.assertEquals(0xDAE, self.chip8.get_pc())

        self.chip8.execute(0xB432)
        self.assertEquals(1174, self.chip8.get_pc())

    def testSubroutines(self):
        """
        Chip8 has build in support for subroutines.

        There are two subroutine opcodes :
        2NNN start executing subroutine at NNN
        00EE return from the subroutine

        For this we will have to do manipulations to the stack. 2NNN should write
        the current instruction address to the stack and increment the stack
        pointer. Most chip8 systems support 16 entries in the stack pointer.
        """
        self.chip8.execute(0x2DAE)
        self.assertEquals(0xDAE, self.chip8.get_pc())

        self.chip8.execute(0x00EE)
        self.assertEquals(0x200, self.chip8.get_pc())

    def testEqualJumps(self):
        """
        We will now implement conditional skipping. Conditional skips are
        basically jumps if some condition is met like a register having a value.

        Opcodes :
        3XNN : Skip the next instruction if the value in Vx equals NN
        5XY0 : Skip the next instruction if the value in Vx equals Vy
        4XNN : Skip the next instruction if the value in Vx does not equal NN
        9XY0 : Skip the next instruction if the value in Vx does not equal Vy

        This test will be running the program counter forward so it will also test that
        we aren't doing anything too wrong with it.
        """
        self.chip8.execute(0x3064)  # Skip if V0 == 0x64
        self.assertEquals(0x202, self.chip8.get_pc())  # Increment the PC by 2

        self.chip8.execute(0x3164)  # Skip if V1 == 0x64, doesn't skip because V1 == 0x27
        self.assertEquals(0x202, self.chip8.get_pc())  # Do not increment the PC

        self.chip8.execute(0x6764)  # Set V7 to 64
        self.chip8.execute(0x5070)  # Skip if V0 == V7
        self.assertEquals(0x204, self.chip8.get_pc())  # Increment the PC by 2

        self.chip8.execute(0x5170)  # Skip if V1 == V7 (It doesn't)
        self.assertEquals(0x204, self.chip8.get_pc())  # Increment the PC by 2

    def testNonEqualJumps(self):
        self.chip8.execute(0x4064)  # Skip if V0 != 0x64 (it won't skip)
        self.assertEquals(0x200, self.chip8.get_pc())  # Increment the PC by 2

        self.chip8.execute(0x4164)  # Skip if V1 == 0x64, skips because V1 == 0x27
        self.assertEquals(0x202, self.chip8.get_pc())  # Do not increment the PC

        self.chip8.execute(0x6764)  # Set V7 to 64
        self.chip8.execute(0x9070)  # Skip if V0 != V7(It won't skip)
        self.assertEquals(0x202, self.chip8.get_pc())  # Increment the PC by 2

        self.chip8.execute(0x9170)  # Skip if V1 != V7
        self.assertEquals(0x204, self.chip8.get_pc())  # Increment the PC by 2

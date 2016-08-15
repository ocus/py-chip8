import unittest

from chip8.emulator.Chip8 import Chip8


class ArithmeticOpCodeTest(unittest.TestCase):
    """
    The first part of writing a Chip-8 emulator is setting up the main memory
    correctly.

    Specifically there are several constants which are found below 0x0200 and
    programs typically start at 0x0200
    """

    def setUp(self):
        self.chip8 = Chip8()

    def tearDown(self):
        pass

    def testPCInitializedTo0x0200(self):
        """
        This chip 8 program counter starts at 0x200. This seems like an obvious
        first test.
        """
        self.assertEquals(0x0200, self.chip8.get_pc())

    def testDataRegistersInitializedTo0(self):
        """
        CHIP-8 has 16 8 bit data registers numbered V0 - VF.

        The next few tests test the initial values of the registers and several
        simple opcodes.
        """
        self.assertEquals(0x0, self.chip8.get_v0())  # Test initialized to 0
        self.assertEquals(0x0, self.chip8.get_v1())  # Test initialized to 0
        self.assertEquals(0x0, self.chip8.get_v2())  # Test initialized to 0
        self.assertEquals(0x0, self.chip8.get_v3())  # Test initialized to 0
        self.assertEquals(0x0, self.chip8.get_v4())  # Test initialized to 0
        self.assertEquals(0x0, self.chip8.get_v5())  # Test initialized to 0
        self.assertEquals(0x0, self.chip8.get_v6())  # Test initialized to 0
        self.assertEquals(0x0, self.chip8.get_v7())  # Test initialized to 0
        self.assertEquals(0x0, self.chip8.get_v8())  # Test initialized to 0
        self.assertEquals(0x0, self.chip8.get_v9())  # Test initialized to 0
        self.assertEquals(0x0, self.chip8.get_va())  # Test initialized to 0
        self.assertEquals(0x0, self.chip8.get_vb())  # Test initialized to 0
        self.assertEquals(0x0, self.chip8.get_vc())  # Test initialized to 0
        self.assertEquals(0x0, self.chip8.get_vd())  # Test initialized to 0
        self.assertEquals(0x0, self.chip8.get_ve())  # Test initialized to 0
        self.assertEquals(0x0, self.chip8.get_vf())  # Test initialized to 0

    def testLoadConstant(self):
        """
        The opcode 0x6XNN stores the constant NN into register VX.

        IE 0x6A42 would store 42 into register VA. It should be noted at this
        point that CHIP-8 is big-endian.
        """
        self.chip8.execute(0x6015)
        self.assertEquals(0x15, self.chip8.get_v0())  # Test loads 15 to V0

        self.chip8.execute(0x6120)
        self.assertEquals(0x20, self.chip8.get_v1())  # etc

        self.chip8.execute(0x6225)
        self.assertEquals(0x25, self.chip8.get_v2())

        self.chip8.execute(0x6330)
        self.assertEquals(0x30, self.chip8.get_v3())

        self.chip8.execute(0x6435)
        self.assertEquals(0x35, self.chip8.get_v4())

        self.chip8.execute(0x6540)
        self.assertEquals(0x40, self.chip8.get_v5())

        self.chip8.execute(0x6645)
        self.assertEquals(0x45, self.chip8.get_v6())

        self.chip8.execute(0x6750)
        self.assertEquals(0x50, self.chip8.get_v7())

        self.chip8.execute(0x6855)
        self.assertEquals(0x55, self.chip8.get_v8())

        self.chip8.execute(0x6960)
        self.assertEquals(0x60, self.chip8.get_v9())

        self.chip8.execute(0x6A65)
        self.assertEquals(0x65, self.chip8.get_va())

        self.chip8.execute(0x6B70)
        self.assertEquals(0x70, self.chip8.get_vb())

        self.chip8.execute(0x6C75)
        self.assertEquals(0x75, self.chip8.get_vc())

        self.chip8.execute(0x6D80)
        self.assertEquals(0x80, self.chip8.get_vd())

        self.chip8.execute(0x6E85)
        self.assertEquals(0x85, self.chip8.get_ve())

        self.chip8.execute(0x6F90)
        self.assertEquals(0x90, self.chip8.get_vf())

    def testAddConstant(self):
        """
        The opcode 0x7XNN adds the constant NN into the value of register VX.

        IE 0x6A42 0x7A42

        would store 42 into register VA and then add 42 to get 84.

        A special note, registers are 8 bit and should overflow appropriately.

        We will use fewer tests now, but feel free to add more to test edge cases
        and other questions you might have about your code.
        """
        self.chip8.execute(0x6015)
        self.chip8.execute(0x7015)
        self.assertEquals(0x2A, self.chip8.get_v0())

        self.chip8.execute(0x6A42)
        self.chip8.execute(0x7A42)
        self.assertEquals(0x84, self.chip8.get_va())  # Test loads 15 to V0

        self.chip8.execute(0x6EFF)
        self.chip8.execute(0x7E01)
        self.assertEquals(0x0, self.chip8.get_ve())  # Test Overflow

    def testCopyRegister(self):
        """
        The opcode 8XY0 stores the value of register VY into VX

        IE 0x6A42 0x8EA0

        would store 42 into register VA and then copy it to register VE.
        """
        self.chip8.execute(0x6A42)
        self.chip8.execute(0x8EA0)
        self.assertEquals(0x42, self.chip8.get_va())
        self.assertEquals(0x42, self.chip8.get_ve())

        self.chip8.execute(0x6ADE)
        self.chip8.execute(0x8FA0)
        self.assertEquals(0x42, self.chip8.get_ve())
        self.assertEquals(0xDE, self.chip8.get_vf())

    def testAddRegister(self):
        """
        The opcode 8XY4 adds the value of register VY to VX

        IE 0x6A42 0x6E42 0x8EA4

        would store 42 into register VA and VE and then add VA into register VE.
        This instruction will modify register VF. If there is an overflow then VF
        will be set to 01. If there is not an overflow it will be set to 00.

        This means that VF is always modified.
        """
        self.chip8.execute(0x6A42)
        self.chip8.execute(0x6E42)
        self.chip8.execute(0x8FA0)
        self.chip8.execute(0x8EA4)
        self.assertEquals(0x42, self.chip8.get_va())
        self.assertEquals(0x84, self.chip8.get_ve())
        self.assertEquals(0x00, self.chip8.get_vf())

        self.chip8.execute(0x6AF0)
        self.chip8.execute(0x6E42)
        self.chip8.execute(0x8FA0)
        self.chip8.execute(0x8EA4)
        self.assertEquals(0xF0, self.chip8.get_va())
        self.assertEquals(0x32, self.chip8.get_ve())
        self.assertEquals(0x01, self.chip8.get_vf())

    def testSubtractRegister(self):
        """
        The opcodes 8XY5 and 8XY7 perform subtraction operations and set VF to
        indicate a borrow.

        8XY5 sets VX to VX - VY
        8XY7 sets VX to VY - VX

        IE 0x6B84 0x6D25 0x8DB5

        would store 84 into register VB and 25 into VD. Then VD would be set to
        (25 - 84) which would underflow to xxx. Additionally VF would be set to
        0x00 to indicate the borrow.

        IE 0x6B84 0x6D25 0x8DB7

        would store 84 into register VB and 25 into VD. Then VD would be set to
        (84 - 25) which would be 59. Additionally VF would be set to 0x01 to
        indicate there was no borrow.
        """
        self.chip8.execute(0x6B84)  # Set Register B to 0x84
        self.chip8.execute(0x6F84)  # Set Register F to 0x84 (this tests carry)
        self.chip8.execute(0x6D25)  # Set Register D to 0x25
        self.chip8.execute(0x8DB5)  # Set Register D to 0x25 - 0x84. This underflows and forces a carry

        self.assertEquals(0x84, self.chip8.get_vb())
        self.assertEquals(161, self.chip8.get_vd())
        self.assertEquals(0x00, self.chip8.get_vf())

        self.chip8.execute(0x6B84)
        self.chip8.execute(0x6F84)
        self.chip8.execute(0x6D25)
        self.chip8.execute(0x8DB7)

        self.assertEquals(0x84, self.chip8.get_vb())
        self.assertEquals(95, self.chip8.get_vd())
        self.assertEquals(0x01, self.chip8.get_vf())

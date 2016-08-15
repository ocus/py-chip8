import os
import unittest

from chip8.Chip8Utils import Chip8Utils


class KeypadInputTest(unittest.TestCase):
    """
    Chip-8 has support for a 16 button keypad input. The keys are assigned values
    from 0x0 - 0xF. The mapping from your keyboard/input device to self.chip8
    shouldn't matter for these tests.
    """

    def setUp(self):
        path = os.path.join(os.path.dirname(__file__), 'resources', 'E07GraphicsRom.ch8')
        self.chip8 = Chip8Utils.create_from_rom(path)
        self.chip8.execute(0x6064)
        self.chip8.execute(0x6127)
        self.chip8.execute(0x6212)
        self.chip8.execute(0x63AE)
        self.chip8.execute(0x64FF)
        self.chip8.execute(0x65B4)
        self.chip8.execute(0x6642)
        self.chip8.execute(0x673F)
        self.chip8.execute(0x681F)
        self.chip8.execute(0x6F25)

    def testIRegister(self):
        """
        The I Register holds memory addresses. A program can not read the value
        currently set in the I register but may only set it.
        
        There are two opcodes for the IRegister : ANNN : Stores in the I register
        the address 0xNNN FX1E : Adds to the value in the I-Register the value of
        VX.
        """
        self.chip8.execute(0xA123)
        self.assertEquals(0x123, self.chip8.get_i_register())

        self.chip8.execute(0xF11E)
        self.assertEquals(0x123 + 0x27, self.chip8.get_i_register())

    def testDrawSprite(self):
        """
        Sprites in self.chip8 are represented in memory as columns of 8 bits with a
        variable number of rows. The 8 bits each correspond to a pixel with 1
        being toggled and 0 being transparent. The sprites are accessed starting
        at the memory address pointed to by the I register.

        Sprites are XOR drawn. This means that a 1 will flip that particular
        pixel. If a pixel is unset by this operation then the register VF is set
        to 1. Otherwise it is 0.

        DXYN : Draw a Sprite of N rows at position VX,VY with the data pointed to
        by the I register.
        """
        self.chip8.execute(0xA202)
        self.chip8.execute(0xD122)  # Draw Sprite at 39, 18
        self.assertEquals(0, self.chip8.get_vf())

        video = self.chip8.get_screen()
        self.assertEquals(1, video[39 + 64 * 18])
        self.assertEquals(1, video[40 + 64 * 18])
        self.assertEquals(1, video[41 + 64 * 18])
        self.assertEquals(1, video[42 + 64 * 18])
        self.assertEquals(1, video[43 + 64 * 18])
        self.assertEquals(1, video[44 + 64 * 18])
        self.assertEquals(1, video[45 + 64 * 18])
        self.assertEquals(1, video[46 + 64 * 18])

        self.assertEquals(0, video[39 + 64 * 19])
        self.assertEquals(0, video[40 + 64 * 19])
        self.assertEquals(1, video[41 + 64 * 19])
        self.assertEquals(1, video[42 + 64 * 19])
        self.assertEquals(1, video[43 + 64 * 19])
        self.assertEquals(1, video[44 + 64 * 19])
        self.assertEquals(0, video[45 + 64 * 19])
        self.assertEquals(0, video[46 + 64 * 19])

        self.chip8.execute(0xD122)  # Draw Sprite at 39,18
        self.assertEquals(1, self.chip8.get_vf())

        video = self.chip8.get_screen()
        self.assertEquals(0, video[39 + 64 * 18])
        self.assertEquals(0, video[40 + 64 * 18])
        self.assertEquals(0, video[41 + 64 * 18])
        self.assertEquals(0, video[42 + 64 * 18])
        self.assertEquals(0, video[43 + 64 * 18])
        self.assertEquals(0, video[44 + 64 * 18])
        self.assertEquals(0, video[45 + 64 * 18])
        self.assertEquals(0, video[46 + 64 * 18])

        self.assertEquals(0, video[39 + 64 * 19])
        self.assertEquals(0, video[40 + 64 * 19])
        self.assertEquals(0, video[41 + 64 * 19])
        self.assertEquals(0, video[42 + 64 * 19])
        self.assertEquals(0, video[43 + 64 * 19])
        self.assertEquals(0, video[44 + 64 * 19])
        self.assertEquals(0, video[45 + 64 * 19])
        self.assertEquals(0, video[46 + 64 * 19])

    def drawSpriteBottomRightEdgeTests(self):
        """
        Sprites wrap around on their axis. IE If you draw to X 65 it will wrap to
        position 1.
        """
        self.chip8.execute(0xA202)
        self.chip8.execute(0xD781)
        self.chip8.execute(0xD871)
        self.chip8.execute(0xD781)
        self.chip8.execute(0xD871)

    def testClearVideo(self):
        """
        The opcode 00E0 clears the screen.
        """
        self.chip8.execute(0xA202)
        self.chip8.execute(0xD212)  # Draw Sprite at 18, 7 (39 wraps to 7)
        self.chip8.execute(0x00E0)

        video = self.chip8.get_screen()

        self.assertEquals(0, video[18 + 64 * 7])
        self.assertEquals(0, video[19 + 64 * 7])
        self.assertEquals(0, video[20 + 64 * 7])
        self.assertEquals(0, video[21 + 64 * 7])
        self.assertEquals(0, video[22 + 64 * 7])
        self.assertEquals(0, video[23 + 64 * 7])
        self.assertEquals(0, video[24 + 64 * 7])
        self.assertEquals(0, video[25 + 64 * 7])

    def testHexFonts(self):
        """
        Chip 8 has build in hexadecimal fonts. These fonts are stored in the 200
        bytes of reserved data and accessed using a special opcode.

        FX29 : Set the I register to the address of the sprite corresponding to
        the hex digit stored in VX.
        """
        self.chip8.execute(0x6100)  # Store 00 in V1
        self.chip8.execute(0x6200)  # Store 00 in V2

        for i in range(0, 0xf):
            self.chip8.execute(0x6000 + i)  # Store 00 in V0
            self.chip8.execute(0xF029)  # Set I to the memory address of the font sprite in V0
            self.chip8.execute(0xD125)  # Draw all 5 lines of the sprite at 0, 0.

            self.checkGraphics(i)  # Test for being drawn.
            self.chip8.execute(0x00E0)  # Clear Screen

    def checkGraphics(self, i):
        if i == 0:
            self.assertEquals(0xF0, self.chip8._get_sprite(0, 0))
            self.assertEquals(0x90, self.chip8._get_sprite(0, 1))
            self.assertEquals(0x90, self.chip8._get_sprite(0, 2))
            self.assertEquals(0x90, self.chip8._get_sprite(0, 3))
            self.assertEquals(0xF0, self.chip8._get_sprite(0, 4))
        elif i == 1:
            self.assertEquals(0x20, self.chip8._get_sprite(0, 0))
            self.assertEquals(0x60, self.chip8._get_sprite(0, 1))
            self.assertEquals(0x20, self.chip8._get_sprite(0, 2))
            self.assertEquals(0x20, self.chip8._get_sprite(0, 3))
            self.assertEquals(0x70, self.chip8._get_sprite(0, 4))
        elif i == 2:
            self.assertEquals(0xF0, self.chip8._get_sprite(0, 0))
            self.assertEquals(0x10, self.chip8._get_sprite(0, 1))
            self.assertEquals(0xF0, self.chip8._get_sprite(0, 2))
            self.assertEquals(0x80, self.chip8._get_sprite(0, 3))
            self.assertEquals(0xF0, self.chip8._get_sprite(0, 4))
        elif i == 3:
            self.assertEquals(0xF0, self.chip8._get_sprite(0, 0))
            self.assertEquals(0x10, self.chip8._get_sprite(0, 1))
            self.assertEquals(0xF0, self.chip8._get_sprite(0, 2))
            self.assertEquals(0x10, self.chip8._get_sprite(0, 3))
            self.assertEquals(0xF0, self.chip8._get_sprite(0, 4))
        elif i == 4:
            self.assertEquals(0x90, self.chip8._get_sprite(0, 0))
            self.assertEquals(0x90, self.chip8._get_sprite(0, 1))
            self.assertEquals(0xF0, self.chip8._get_sprite(0, 2))
            self.assertEquals(0x10, self.chip8._get_sprite(0, 3))
            self.assertEquals(0x10, self.chip8._get_sprite(0, 4))
        elif i == 5:
            self.assertEquals(0xF0, self.chip8._get_sprite(0, 0))
            self.assertEquals(0x80, self.chip8._get_sprite(0, 1))
            self.assertEquals(0xF0, self.chip8._get_sprite(0, 2))
            self.assertEquals(0x10, self.chip8._get_sprite(0, 3))
            self.assertEquals(0xF0, self.chip8._get_sprite(0, 4))
        elif i == 6:
            self.assertEquals(0xF0, self.chip8._get_sprite(0, 0))
            self.assertEquals(0x80, self.chip8._get_sprite(0, 1))
            self.assertEquals(0xF0, self.chip8._get_sprite(0, 2))
            self.assertEquals(0x90, self.chip8._get_sprite(0, 3))
            self.assertEquals(0xF0, self.chip8._get_sprite(0, 4))
        elif i == 7:
            self.assertEquals(0xF0, self.chip8._get_sprite(0, 0))
            self.assertEquals(0x10, self.chip8._get_sprite(0, 1))
            self.assertEquals(0x20, self.chip8._get_sprite(0, 2))
            self.assertEquals(0x40, self.chip8._get_sprite(0, 3))
            self.assertEquals(0x40, self.chip8._get_sprite(0, 4))
        elif i == 8:
            self.assertEquals(0xF0, self.chip8._get_sprite(0, 0))
            self.assertEquals(0x90, self.chip8._get_sprite(0, 1))
            self.assertEquals(0xF0, self.chip8._get_sprite(0, 2))
            self.assertEquals(0x90, self.chip8._get_sprite(0, 3))
            self.assertEquals(0xF0, self.chip8._get_sprite(0, 4))
        elif i == 9:
            self.assertEquals(0xF0, self.chip8._get_sprite(0, 0))
            self.assertEquals(0x90, self.chip8._get_sprite(0, 1))
            self.assertEquals(0xF0, self.chip8._get_sprite(0, 2))
            self.assertEquals(0x10, self.chip8._get_sprite(0, 3))
            self.assertEquals(0xF0, self.chip8._get_sprite(0, 4))
        elif i == 0xA:
            self.assertEquals(0xF0, self.chip8._get_sprite(0, 0))
            self.assertEquals(0x90, self.chip8._get_sprite(0, 1))
            self.assertEquals(0xF0, self.chip8._get_sprite(0, 2))
            self.assertEquals(0x90, self.chip8._get_sprite(0, 3))
            self.assertEquals(0x90, self.chip8._get_sprite(0, 4))
        elif i == 0xB:
            self.assertEquals(0xE0, self.chip8._get_sprite(0, 0))
            self.assertEquals(0x90, self.chip8._get_sprite(0, 1))
            self.assertEquals(0xE0, self.chip8._get_sprite(0, 2))
            self.assertEquals(0x90, self.chip8._get_sprite(0, 3))
            self.assertEquals(0xE0, self.chip8._get_sprite(0, 4))
        elif i == 0xC:
            self.assertEquals(0xF0, self.chip8._get_sprite(0, 0))
            self.assertEquals(0x80, self.chip8._get_sprite(0, 1))
            self.assertEquals(0x80, self.chip8._get_sprite(0, 2))
            self.assertEquals(0x80, self.chip8._get_sprite(0, 3))
            self.assertEquals(0xF0, self.chip8._get_sprite(0, 4))
        elif i == 0xD:
            self.assertEquals(0xE0, self.chip8._get_sprite(0, 0))
            self.assertEquals(0x90, self.chip8._get_sprite(0, 1))
            self.assertEquals(0x90, self.chip8._get_sprite(0, 2))
            self.assertEquals(0x90, self.chip8._get_sprite(0, 3))
            self.assertEquals(0xE0, self.chip8._get_sprite(0, 4))
        elif i == 0xE:
            self.assertEquals(0xF0, self.chip8._get_sprite(0, 0))
            self.assertEquals(0x80, self.chip8._get_sprite(0, 1))
            self.assertEquals(0xF0, self.chip8._get_sprite(0, 2))
            self.assertEquals(0x80, self.chip8._get_sprite(0, 3))
            self.assertEquals(0xF0, self.chip8._get_sprite(0, 4))
        elif i == 0xF:
            self.assertEquals(0xF0, self.chip8._get_sprite(0, 0))
            self.assertEquals(0x80, self.chip8._get_sprite(0, 1))
            self.assertEquals(0xF0, self.chip8._get_sprite(0, 2))
            self.assertEquals(0x80, self.chip8._get_sprite(0, 3))
            self.assertEquals(0x80, self.chip8._get_sprite(0, 4))

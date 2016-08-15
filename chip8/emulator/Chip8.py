from __future__ import print_function

import array
import random
import sys
import time

from chip8.emulator.Audio import player as audio_player
from chip8.emulator.Input import Input


# : main
# loop
#   vb := 0
#   loop
#     va := 0
#     loop
#       v0 := va
#       v1 := vb
#       v9 := 0
#       loop
#         i := hex v9
#         sprite v0 v1 5
#         v9 += 1
#         v0 += 5
#         if
#           v9 == 8
#         begin
#           v0 := va
#           v1 += 6
#         end
#         if
#           v9 < 16
#         begin
#           again
#         end
#         v7 := 255 loop v7 += -1 if v7 > -128 then again
#         clear
#     va += 1
#     if
#       va < 27
#     then
#       again
#   vb += 1
#   if
#     vb < 22
#   then
#     again
# again


class Chip8(object):
    MEMORY_SIZE = 0x1000
    FONTS = [
        0xF0, 0x90, 0x90, 0x90, 0xF0,
        0x20, 0x60, 0x20, 0x20, 0x70,
        0xF0, 0x10, 0xF0, 0x80, 0xF0,
        0xF0, 0x10, 0xF0, 0x10, 0xF0,
        0x90, 0x90, 0xF0, 0x10, 0x10,
        0xF0, 0x80, 0xF0, 0x10, 0xF0,
        0xF0, 0x80, 0xF0, 0x90, 0xF0,
        0xF0, 0x10, 0x20, 0x40, 0x40,
        0xF0, 0x90, 0xF0, 0x90, 0xF0,
        0xF0, 0x90, 0xF0, 0x10, 0xF0,
        0xF0, 0x90, 0xF0, 0x90, 0x90,
        0xE0, 0x90, 0xE0, 0x90, 0xE0,
        0xF0, 0x80, 0x80, 0x80, 0xF0,
        0xE0, 0x90, 0x90, 0x90, 0xE0,
        0xF0, 0x80, 0xF0, 0x80, 0xF0,
        0xF0, 0x80, 0xF0, 0x80, 0x80,
    ]

    def __init__(self, memory=None, input_kb=None):
        if not memory:
            memory = bytearray(self.MEMORY_SIZE)
        if not isinstance(memory, bytearray):
            raise TypeError('Memory must be a %s (given: %s' % (bytearray, type(memory)))

        if not input_kb:
            input_kb = Input()

        self._cycle_counter = 0
        self.pc = 0x0200
        self.memory = self._load_fonts(memory)
        self.input = input_kb
        self.video = bytearray(64 * 32)

        self.registers = [
            0x0,
            0x0,
            0x0,
            0x0,
            0x0,
            0x0,
            0x0,
            0x0,
            0x0,
            0x0,
            0x0,
            0x0,
            0x0,
            0x0,
            0x0,
            0x0,
        ]
        self.i_register = 0x0

        self.sp = 0
        self.stack = array.array('i', (0 for _ in range(0, 16)))  # 0-filled

        self.delay_timer = 0
        self.sound_timer = 0

        self.next_timer = 0

    def cycle(self):
        self._cycle_counter += 1
        instruction = self.get_current_instruction()
        self.pc += 0x2
        current_time = time.time() * 1000.0
        if current_time > self.next_timer:
            self._count_down_timers()
            self.next_timer = current_time + (1000.0 / 60.0)
        self.execute(instruction)
        return self._cycle_counter

    def get_cycle_counter(self):
        return self._cycle_counter

    def _count_down_timers(self):
        if self.delay_timer > 0:
            self.delay_timer -= 1
        if self.sound_timer > 0:
            audio_player.play()
        else:
            audio_player.stop()

    def get_current_instruction(self):
        return ((self.memory[self.pc] << 8) & 0xff00) | (self.memory[self.pc + 1] & 0xff)

    def execute(self, instruction):
        # 00E0 Clears the screen.
        if instruction == 0x00e0:
            self.video = bytearray(64 * 32)
        # 00EE Returns from a subroutine.
        elif instruction == 0x00ee:
            self.sp -= 1
            self.pc = self.stack[self.sp]
        # 1NNN Jumps to address NNN.
        elif instruction >> 12 == 0x1:
            nnn = instruction & 0x0fff
            self.pc = nnn
        # 2NNN Calls subroutine at NNN.
        elif instruction >> 12 == 0x2:
            self.stack[self.sp] = self.pc
            self.sp += 1
            nnn = instruction & 0x0fff
            self.pc = nnn
        # 3XNN Skips the next instruction if VX equals NN.
        elif instruction >> 12 == 0x3:
            x = (instruction & 0x0f00) >> 8
            nn = instruction & 0x0fff
            if self._get_v(x) == nn:
                self.pc += 2
        # 4XNN Skips the next instruction if VX doesn't equal NN.
        elif instruction >> 12 == 0x4:
            x = (instruction & 0x0f00) >> 8
            nn = instruction & 0x0fff
            if self._get_v(x) != nn:
                self.pc += 2
        # 5XYN
        elif instruction >> 12 == 0x5:
            x = (instruction & 0x0f00) >> 8
            y = (instruction & 0x00f0) >> 4
            n = instruction & 0x000f
            # 5XY0 Skips the next instruction if VX equals VY.
            if n == 0x0:
                if self._get_v(x) == self._get_v(y):
                    self.pc += 2
            else:
                self._unsupported_instruction(instruction)
        # 6XNN Sets VX to NN.
        elif instruction >> 12 == 0x6:
            x = (instruction & 0x0f00) >> 8
            nn = instruction & 0x00ff
            self._set_v(x, nn)
        # 7XNN Adds NN to VX.
        elif instruction >> 12 == 0x7:
            x = (instruction & 0x0f00) >> 8
            nn = instruction & 0x00ff
            self._set_v(x, self._get_v(x) + nn)
        # 8XYN
        elif instruction >> 12 == 0x8:
            x = (instruction & 0x0f00) >> 8
            y = (instruction & 0x00f0) >> 4
            n = instruction & 0x000f
            # 8XY0 Sets VX to the value of VY.
            if n == 0x0:
                self._set_v(x, self._get_v(y))
            # 8XY1 Sets VX to VX or VY.
            elif n == 0x1:
                self._set_v(x, self._get_v(x) | self._get_v(y))
            # 8XY2 Sets VX to VX and VY.
            elif n == 0x2:
                self._set_v(x, self._get_v(x) & self._get_v(y))
            # 8XY3 Sets VX to VX xor VY.
            elif n == 0x3:
                self._set_v(x, self._get_v(x) ^ self._get_v(y))
            # 8XY4 Adds VY to VX. VF is set to 1 when there's a carry, and to 0 when there isn't.
            elif n == 0x4:
                overflow = self._set_v(x, self._get_v(x) + self._get_v(y))
                self._set_v(0xf, 1 if overflow else 0)
            # 8XY5 VY is subtracted from VX. VF is set to 0 when there's a borrow, and 1 when there isn't.
            elif n == 0x5:
                underflow = self._set_v(x, self._get_v(x) - self._get_v(y))
                self._set_v(0xf, 0 if underflow else 1)
            # 8XY6 Shifts VX right by one. VF is set to the value of the least significant bit of VX before the shift.
            elif n == 0x6:
                vx = self._get_v(x)
                self._set_v(0xf, vx & 0x1)
                self._set_v(x, vx >> 1)
            # 8XY7 Sets VX to VY minus VX. VF is set to 0 when there's a borrow, and 1 when there isn't.
            elif n == 0x7:
                underflow = self._set_v(x, self._get_v(y) - self._get_v(x))
                self._set_v(0xf, 0 if underflow else 1)
            # 8XYE Shifts VX left by one. VF is set to the value of the most significant bit of VX before the shift.
            elif n == 0xe:
                vx = self._get_v(x)
                self._set_v(0xf, (vx >> 7) & 0x1)
                self._set_v(x, vx << 1)
            else:
                self._unsupported_instruction(instruction)
        # 9XYN
        elif instruction >> 12 == 0x9:
            x = (instruction & 0x0f00) >> 8
            y = (instruction & 0x00f0) >> 4
            n = instruction & 0x000f
            # 9XY0 Skips the next instruction if VX doesn't equal VY.
            if n == 0x0:
                if self._get_v(x) != self._get_v(y):
                    self.pc += 2
            else:
                self._unsupported_instruction(instruction)
        # ANNN Sets I to the address NNN.
        elif instruction >> 12 == 0xa:
            nnn = instruction & 0x0fff
            self.i_register = nnn
        # BNNN Jumps to the address NNN plus V0.
        elif instruction >> 12 == 0xb:
            nnn = instruction & 0x0fff
            self.pc = nnn + self.get_v0()
        # CXNN Sets VX to the result of a bitwise and operation on a random number and NN.
        elif instruction >> 12 == 0xc:
            x = (instruction & 0x0f00) >> 8
            nn = instruction & 0x00ff
            self._set_v(x, random.randint(0x0, 0xff) & nn)
        # DXYN Draws a sprite at coordinate (VX, VY) that has a width of 8 pixels and a height of N pixels.
        #  Each row of 8 pixels is read as bit-coded starting from memory location I;
        #  I value doesn't change after the execution of this instruction.
        #  VF is set to 1 if any screen pixels are flipped from set to unset when the sprite is drawn,
        #  and to 0 if that doesn't happen
        elif instruction >> 12 == 0xd:
            x = (instruction & 0x0f00) >> 8
            y = (instruction & 0x00f0) >> 4
            n = instruction & 0x000f
            sx = self._get_v(x)
            sy = self._get_v(y)
            self._set_v(0xf, 0x0)
            for i in range(0, n):
                old_sprite = self._get_sprite(sx, sy + i)
                self._write_sprite(sx, sy + i, self.memory[self.i_register + i])
                if (self.memory[self.i_register + i] & old_sprite) != 0:
                    self._set_v(0xf, 0x1)
        # EXNN
        elif instruction >> 12 == 0xe:
            x = (instruction & 0x0f00) >> 8
            nn = instruction & 0xff
            # EX9E Skips the next instruction if the key stored in VX is pressed.
            if nn == 0x9e:
                if self.input.read() == self._get_v(x):
                    self.pc += 0x02
            # EXA1 Skips the next instruction if the key stored in VX isn't pressed.
            elif nn == 0xa1:
                if self.input.read() != self._get_v(x):
                    self.pc += 0x02
            else:
                self._unsupported_instruction(instruction)
        # FXNN
        elif instruction >> 12 == 0xf:
            x = (instruction & 0x0f00) >> 8
            nn = instruction & 0x00ff
            # FX07 Sets VX to the value of the delay timer.
            if nn == 0x07:
                self._set_v(x, self.delay_timer)
            # FX0A A key press is awaited, and then stored in VX.
            elif nn == 0x0a:
                i = self.input.read()
                if i is None:
                    self.pc -= 2  # wait
                else:
                    self._set_v(x, i)
            # FX15 Sets the delay timer to VX.
            elif nn == 0x15:
                self.delay_timer = self._get_v(x)
            # FX18 Sets the sound timer to VX.
            elif nn == 0x18:
                self.sound_timer = self._get_v(x)
            # FX1E Adds VX to I.
            elif nn == 0x1e:
                self.i_register += self._get_v(x)
            # FX29 Sets I to the location of the sprite for the character in VX.
            #  Characters 0-F (in hexadecimal) are represented by a 4x5 font.
            elif nn == 0x29:
                self.i_register = self._get_v(x) * 5
            # FX33 Stores the binary-coded decimal representation of VX,
            #  with the most significant of three digits at the address in I,
            #  the middle digit at I plus 1, and the least significant digit at I plus 2.
            #  (In other words, take the decimal representation of VX,
            #  place the hundreds digit in memory at location in I,
            #  the tens digit at location I+1, and the ones digit at location I+2.)
            elif nn == 0x33:
                vx = self._get_v(x)
                self.memory[self.i_register] = int(vx / 100)
                self.memory[self.i_register + 1] = int((vx % 100) / 10)
                self.memory[self.i_register + 2] = int(vx % 10)
            # FX55 Stores V0 to VX (including VX) in memory starting at address I.
            elif nn == 0x55:
                self._unsupported_instruction(instruction)  # TODO
            # FX65 Fills V0 to VX (including VX) with values from memory starting at address I.
            elif nn == 0x65:
                self._unsupported_instruction(instruction)  # TODO
            else:
                self._unsupported_instruction(instruction)
        else:
            self._unsupported_instruction(instruction)

    def _set_v(self, r, val):
        """
        Sets the value of a register

        :param r: Register index (0x0 to 0xf)
        :param val: Value of the register (0x00 to 0xff)
        :return: True if underflow (val < 0x00) or overflow (val > 0xff)
        """
        self._ensure_register(r)
        self.registers[r] = val & 0xff
        return (val < 0x00) or (val | 0xff > 0xff)

    def _get_v(self, r):
        self._ensure_register(r)
        return self.registers[r]

    def get_v0(self):
        return self._get_v(0x0)

    def get_v1(self):
        return self._get_v(0x1)

    def get_v2(self):
        return self._get_v(0x2)

    def get_v3(self):
        return self._get_v(0x3)

    def get_v4(self):
        return self._get_v(0x4)

    def get_v5(self):
        return self._get_v(0x5)

    def get_v6(self):
        return self._get_v(0x6)

    def get_v7(self):
        return self._get_v(0x7)

    def get_v8(self):
        return self._get_v(0x8)

    def get_v9(self):
        return self._get_v(0x9)

    def get_va(self):
        return self._get_v(0xa)

    def get_vb(self):
        return self._get_v(0xb)

    def get_vc(self):
        return self._get_v(0xc)

    def get_vd(self):
        return self._get_v(0xd)

    def get_ve(self):
        return self._get_v(0xe)

    def get_vf(self):
        return self._get_v(0xf)

    def get_i_register(self):
        return self.i_register

    def get_pc(self):
        return self.pc

    def _get_sprite(self, x, y):
        index = (x % 64) + (y % 32) * 64
        sprite_bits = self.video[index:index + 8]
        # pack as byte
        return reduce(lambda n, i: n | (i[1] << (7 - i[0])), zip(range(0, 8), sprite_bits), 0)

    def _write_sprite(self, x, y, sprite):
        index = (x % 64) + (y % 32) * 64
        self.video[0 + index] ^= (sprite & 0b10000000) >> 7
        self.video[1 + index] ^= (sprite & 0b01000000) >> 6
        self.video[2 + index] ^= (sprite & 0b00100000) >> 5
        self.video[3 + index] ^= (sprite & 0b00010000) >> 4
        self.video[4 + index] ^= (sprite & 0b00001000) >> 3
        self.video[5 + index] ^= (sprite & 0b00000100) >> 2
        self.video[6 + index] ^= (sprite & 0b00000010) >> 1
        self.video[7 + index] ^= (sprite & 0b00000001)

    def get_screen(self):
        return self.video[:]

    def get_memory(self):
        return self.memory[:]

    def _dump_screen(self, label='', file=sys.stderr):
        self._print('dumping screen %s' % label, file=file)
        for y in range(0, 31):
            index = y * 64
            row = self.video[index:index + 64]
            self._print(' '.join(['@' if b else '.' for b in row]), file=file)

    def debug_dump(self, file=sys.stderr, **kwargs):
        def dump(*args):
            self._print(*args, file=file, **kwargs)

        dump('===== Chip8 debug dump =====')
        dump('cycle: {:d}'.format(self._cycle_counter))
        dump('pc: 0x{:04X}'.format(self.pc))
        dump('i:  0x{:04X}'.format(self.i_register))
        for r, v in enumerate(self.registers):
            dump('v{}: 0x{:02X}'.format(hex(r)[2:].upper(), v))
        dump('stack:', ' '.join(['{:04X}'.format(v) for v in self.stack]))
        dump('memory:')
        blocks = 32 * 2
        for i in range(0, len(self.memory) / blocks):
            addr = i * blocks
            e_addr = addr + blocks
            mem = self.memory[addr:e_addr]
            # dump(' '.join(['{:02d}{:02d}'.format(i*2, (2*i)+1) for i, m in enumerate(mem[0::2])]))
            dump(' ',
                 (' 0x{:04X} =>' if (addr <= self.pc < e_addr) else '          ').format(self.pc),
                 '0x%04X:' % addr,
                 ''.join(
                     [('[{:04X}]' if addr + (2 * i) == self.pc else ' {:04X} ').format((v << 8) | mem[(2 * i) + 1])
                      for i, v in enumerate(mem[0::2])])
                 )
        dump('============================')

    def _load_fonts(self, memory):
        for i, c in enumerate(self.FONTS):
            memory[i] = c
        return memory

    @staticmethod
    def _print(*args, **kwargs):
        print(*args, **kwargs)

    @staticmethod
    def _ensure_register(r):
        if r < 0x0 or r > 0xf:
            raise IndexError('Register %d does not exist' % r)

    @staticmethod
    def _unsupported_instruction(instruction):
        raise NotImplementedError('Instruction "0x%04X" is not supported' % instruction)

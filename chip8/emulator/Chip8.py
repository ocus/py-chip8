import array
import random
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
        instruction = self.get_current_instruction()
        self.pc += 0x2
        current_time = time.time() * 1000.0
        if current_time > self.next_timer:
            self._count_down_timers()
            self.next_timer = current_time + (1000.0 / 60.0)
        self.execute(instruction)

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
        # 00E0
        if instruction == 0x00e0:
            self.video = bytearray(64 * 32)
        # 00EE
        elif instruction == 0x00ee:
            self.sp -= 1
            self.pc = self.stack[self.sp]
        # 1NNN
        elif instruction >> 12 == 0x1:
            nnn = instruction & 0x0fff
            self.pc = nnn
        # 2NNN
        elif instruction >> 12 == 0x2:
            self.stack[self.sp] = self.pc
            self.sp += 1
            nnn = instruction & 0x0fff
            self.pc = nnn
        # 3XNN
        elif instruction >> 12 == 0x3:
            x = (instruction & 0x0f00) >> 8
            nn = instruction & 0x0fff
            if self._get_v(x) == nn:
                self.pc += 2
        # 4XNN
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
            # 5XY0
            if n == 0x0:
                if self._get_v(x) == self._get_v(y):
                    self.pc += 2
            else:
                self._unsupported_instruction(instruction)
        # 6XNN
        elif instruction >> 12 == 0x6:
            x = (instruction & 0x0f00) >> 8
            nn = instruction & 0x00ff
            self._set_v(x, nn)
        # 7XNN
        elif instruction >> 12 == 0x7:
            x = (instruction & 0x0f00) >> 8
            nn = instruction & 0x00ff
            self._set_v(x, self._get_v(x) + nn)
        # 8XYN
        elif instruction >> 12 == 0x8:
            x = (instruction & 0x0f00) >> 8
            y = (instruction & 0x00f0) >> 4
            n = instruction & 0x000f
            # 8XY0
            if n == 0x0:
                self._set_v(x, self._get_v(y))
            # 8XY1
            elif n == 0x1:
                self._set_v(x, self._get_v(x) | self._get_v(y))
            # 8XY2
            elif n == 0x2:
                self._set_v(x, self._get_v(x) & self._get_v(y))
            # 8XY3
            elif n == 0x3:
                self._set_v(x, self._get_v(x) ^ self._get_v(y))
            # 8XY4
            elif n == 0x4:
                overflow = self._set_v(x, self._get_v(x) + self._get_v(y))
                self._set_v(0xf, 1 if overflow else 0)
            # 8XY5
            elif n == 0x5:
                underflow = self._set_v(x, self._get_v(x) - self._get_v(y))
                self._set_v(0xf, 0 if underflow else 1)
            # 8XY6
            elif n == 0x6:
                vx = self._get_v(x)
                self._set_v(0xf, vx & 0x1)
                self._set_v(x, vx >> 1)
            # 8XY7
            elif n == 0x7:
                underflow = self._set_v(x, self._get_v(y) - self._get_v(x))
                self._set_v(0xf, 0 if underflow else 1)
            # 8XYE
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
            if n == 0x0:
                if self._get_v(x) != self._get_v(y):
                    self.pc += 2
            else:
                self._unsupported_instruction(instruction)
        # ANNN
        elif instruction >> 12 == 0xa:
            nnn = instruction & 0x0fff
            self.i_register = nnn
        # BNNN
        elif instruction >> 12 == 0xb:
            nnn = instruction & 0x0fff
            self.pc = nnn + self.get_v0()
        # CXNN
        elif instruction >> 12 == 0xc:
            x = (instruction & 0x0f00) >> 8
            nn = instruction & 0x00ff
            self._set_v(x, random.randint(0x0, 0xff) & nn)
        # DXYN
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
        # FXNN
        elif instruction >> 12 == 0xf:
            x = (instruction & 0x0f00) >> 8
            nn = instruction & 0x00ff
            # FX07
            if nn == 0x07:
                self._set_v(x, self.delay_timer)
            # FX0A
            elif nn == 0x0a:
                i = self.input.read()
                if i is None:
                    self.pc -= 2  # wait
                else:
                    self._set_v(x, i)
            # FX15
            elif nn == 0x15:
                self.delay_timer = self._get_v(x)
            # FX18
            elif nn == 0x18:
                self.sound_timer = self._get_v(x)
            # FX29
            elif nn == 0x29:
                self.i_register = self._get_v(x) * 5
            # FX33
            elif nn == 0x33:
                vx = self._get_v(x)
                self.memory[self.i_register] = int(vx / 100)
                self.memory[self.i_register + 1] = int((vx % 100) / 10)
                self.memory[self.i_register + 2] = int(vx % 10)
            # FX1E
            elif nn == 0x1e:
                self.i_register += self._get_v(x)
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

    def _dump_screen(self, label=''):
        print('dumping screen %s' % label)
        for y in range(0, 31):
            index = y * 64
            row = self.video[index:index + 64]
            print(' '.join(['@' if b else '.' for b in row]))

    def _load_fonts(self, memory):
        for i, c in enumerate(self.FONTS):
            memory[i] = c
        return memory

    @staticmethod
    def _ensure_register(r):
        if r < 0x0 or r > 0xf:
            raise IndexError('Register %d does not exist' % r)

    @staticmethod
    def _unsupported_instruction(instruction):
        raise NotImplementedError('Instruction "%s" is not supported' % hex(instruction))

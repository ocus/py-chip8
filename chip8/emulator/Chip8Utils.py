import mmap
import os

from chip8.emulator.Chip8 import Chip8


class Chip8Utils(object):
    @staticmethod
    def create_from_rom(path, input_kb=None):
        if not os.path.isfile(path):
            raise RuntimeError('File "%s" does not exist' % path)

        with open(path, 'rb') as rom_file:
            rom = mmap.mmap(rom_file.fileno(), 0, access=mmap.ACCESS_READ)

        memory = bytearray(Chip8.MEMORY_SIZE)
        if rom:
            for index, b in enumerate(rom):
                # https://en.wikipedia.org/wiki/CHIP-8#Memory
                # Real Chip8 memory would have its first 512 (0x0200) bytes
                # occupied by the interpreter itself
                memory[0x0200 + index] = b

        return Chip8(memory=memory, input_kb=input_kb)

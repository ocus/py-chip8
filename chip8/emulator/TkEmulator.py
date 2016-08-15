from __future__ import print_function

from StringIO import StringIO
from Tkinter import Tk, Frame, BOTH, RAISED, LEFT, RIGHT, Button, Canvas, CENTER
from threading import Thread
from ttk import Style

from chip8.emulator import Emulator


# http://zetcode.com/gui/tkinter/layout/


class TkEmulator(Emulator):
    def __init__(self, *args, **kwargs):
        kwargs['auto_start'] = False
        super(TkEmulator, self).__init__(*args, **kwargs)

        self.tk_root = Tk()
        self.tk_frame = TkEmulatorFrame(self.tk_root, self)

        self._loop()

    def _before_cycle(self, counter):
        # print('cycle {:d}'.format(counter))
        out = StringIO()
        self.chip8.debug_dump(file=out)
        # print(len(out.getvalue()))

    def _after_cycle(self, counter):
        self.tk_frame.update_pixels(self.chip8.get_screen())
        # self.chip8._dump_screen()

    def _on_crash(self, e):
        print(e)

    def _loop(self):
        thread = Thread(name='Emulator-Thread', target=super(TkEmulator, self)._loop)
        thread.start()

        # self.tk_root.geometry()
        self.tk_root.update()
        self.tk_root.minsize(800, 500)

        self.tk_root.mainloop()
        print('Tk Stopped')
        self.terminate()

# import pillow

class TkEmulatorFrame(Frame):
    screen_scale = int(10),

    def __init__(self, parent, emulator):
        Frame.__init__(self, parent)
        self.emulator = emulator
        self.parent = parent

        self.screen_scale = 10

        self.parent.title("Chip-8: Emulator")
        self.style = Style()
        self.style.theme_use("default")

        # self.pixel_frames = [None for _ in range(0, 64*32)]

        # pixels_frame = Frame(self, relief=RAISED, borderwidth=1)
        #
        # for y in range(0, 32):
        #     pixels_frame.rowconfigure(y, weight=1)
        #     for x in range(0, 64):
        #         if y == 0:
        #             pixels_frame.columnconfigure(x, weight=1)
        #         index = 64 * y + x
        #         pixel_frame = Frame(pixels_frame, background='red')
        #         pixel_frame.grid(row=y, column=x, sticky=W + E + N + S)
        #         self.pixel_frames[index] = pixel_frame
        #         print(index, self.pixel_frames[index])

        # pixels_frame.pack(fill=BOTH, expand=True)
        self.main_frame = Frame(self, relief=RAISED, borderwidth=1)
        self.main_frame.configure(background='blue')

        w = 64 * self.screen_scale
        h = 32 * self.screen_scale
        self.screen_canvas = Canvas(self.main_frame, width=w, height=h)
        self.screen_canvas.configure(background='red')
        self.screen_canvas.place_configure(anchor=CENTER, relx=.5, rely=.5)

        self.main_frame.pack(fill=BOTH, expand=True)
        self.pack(fill=BOTH, expand=True)

        start_button = Button(self, text="Start", command=self.emulator.start)
        start_button.pack(side=LEFT, padx=5, pady=5)

        pause_button = Button(self, text="Pause", command=self.emulator.toggle_pause)
        pause_button.pack(side=LEFT, padx=5, pady=5)

        step_button = Button(self, text="Step", command=self.emulator.step)
        step_button.pack(side=LEFT, padx=5, pady=5)

        stop_button = Button(self, text="Stop", command=self.emulator.stop)
        stop_button.pack(side=LEFT, padx=5, pady=5)

        x5_button = Button(self, text="5", command=lambda: self.emulator.kb_input.press(5))
        x5_button.pack(side=LEFT, padx=5, pady=5)

        quit_button = Button(self, text="Quit", command=self.quit)
        quit_button.pack(side=RIGHT, padx=5, pady=5)

    def update_pixels(self, screen):
        for i, p in enumerate(screen):
            px = i % 64
            py = (i - px) / 64
            x1 = px * self.screen_scale
            y1 = py * self.screen_scale
            x2 = x1 + self.screen_scale
            y2 = y1 + self.screen_scale
            # self.screen_canvas.create_rectangle(x1, y1, x2, y2, fill='black' if p else 'white')
            # frame = self.pixel_frames[i]
            # frame.configure(background='black' if p else 'white')

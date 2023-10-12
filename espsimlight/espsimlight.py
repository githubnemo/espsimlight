#!/usr/bin/env python
import re
import numpy as np


number_pattern = re.compile(r'\b[0-9]+\b')


def effect_fn(iterator, current_color, static={}):
    for i, c in enumerate(iterator):
        c.r = 255
        c.g = 255
        c.b = 255


class Color:
    r = 0
    g = 0
    b = 0

    def __init__(self, r=0, g=0, b=0):
        self.r = r
        self.g = g
        self.b = b

    def __repr__(self):
        return f'#{self.r:>02x}{self.g:>02x}{self.b:>02x}'

    def to_rgb(self):
        r, g, b = self.r, self.g, self.b
        return (r & 0xff) << 16 | (g & 0xff) << 8 | (b & 0xff)

    def from_color(self, c):
        self.r = c.r
        self.g = c.g
        self.b = c.b

    @classmethod
    def from_rgb(cls, v):
        c = cls()
        c.r = v >> 16 & 0xff
        c.g = v >>  8 & 0xff
        c.b = v & 0xff
        return c


def get_canvas_dimensions(canvas):
    canvas_lines = canvas.split('\n')
    height = len(canvas_lines)
    width = max(len(n) for n in canvas_lines)
    return height, width


def render(canvas, height, width, colors):
    canvas_lines = canvas.split('\n')
    pixel_canvas = np.zeros((height, width), dtype='uint32')

    for line_idx, canvas_line in enumerate(canvas_lines):
        offset = 0
        for number_match in number_pattern.finditer(canvas_line):
            start_idx, end_idx = number_match.span()
            color_idx = int(number_match.group())

            start_idx -= offset
            pixel_canvas[line_idx, start_idx] = colors[color_idx].to_rgb()

            # numbers on the canvas can have multiple digits but we don't
            # want the digits influence the indices, therefore we go from
            # left to right and remember the number of superfluous digits
            # so that we can remove them from the start index of the next
            #offset += max(1, len(number_match.group()) - 1)

    return pixel_canvas


class State:
    def __init__(self, length):
        self.colors = [Color() for _ in range(length)]
        self.current_color = Color()

    def set_current_color(self, new_color):
        self.current_color = new_color
        for c in self.colors:
            c.from_color(new_color)


def run_simulation(canvas, display_dims, state):
    try:
        effect_fn(iter(state.colors), state.current_color)
    except Exception as e:
        print('Error while executing effect fn')
        print(e)

    return render(canvas, *display_dims, state.colors)


def gameloop(canvas, strip_length, observer):
    import pygame

    pygame.init()

    display_dims = get_canvas_dimensions(canvas)
    scaling_factor = 8
    window = pygame.display.set_mode((display_dims[1] * scaling_factor, display_dims[0] * scaling_factor))

    state = State(strip_length)
    state.set_current_color(Color(255, 0, 255))

    run = True
    i = 0
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        print(f'tick {i}', end='\r')
        i = (i % 1024) + 1

        window.fill(0)
        image_data = run_simulation(canvas, display_dims, state)

        simulation_surface = pygame.Surface((display_dims[1], display_dims[0]))

        for y in range(image_data.shape[0]):
            for x in range(image_data.shape[1]):
                color = Color.from_rgb(image_data[y, x])
                simulation_surface.set_at((x, y), (color.r, color.g, color.b))

        simulation_surface = pygame.transform.scale_by(simulation_surface, scaling_factor)
        window.blit(simulation_surface, (0,0))

        pygame.display.flip()
        pygame.time.wait(15)

    pygame.quit()



def load_effect_fn_from_file(path):
    print('Reloading effect function...')
    with open(path, 'r') as f:
        try:
            _globals = None
            _locals = {}
            effect_fn = exec(f.read(), _globals, _locals)
            return _locals['effect_fn']
        except Exception as e:
            print(f'Failure parsing effect: {e}')
    return None


def reload_effect_fn(path):
    global effect_fn

    fn = load_effect_fn_from_file(path)
    if not fn:
        return False
    effect_fn = fn
    return True


def get_length_from_canvas(canvas):
    all_numbers = number_pattern.findall(canvas)
    all_numbers = [int(n) for n in all_numbers]
    all_numbers = set(all_numbers)

    ref_numbers = set(range(len(all_numbers)))

    if all_numbers != ref_numbers:
        raise ValueError(
            "Your shape file does not use continuous numbers - this tool "
            "assumes they are, please check your shape file or fix this tool. "
            "Missing: " + str(ref_numbers.difference(all_numbers))
        )
    return len(all_numbers)


if __name__ == "__main__":
    import sys
    from os.path import dirname
    import argparse
    import pathlib
    import watchdog
    import watchdog.events
    import watchdog.observers

    class CodeFileEventHandler(watchdog.events.FileSystemEventHandler):
        def __init__(self, code_file_path):
            self.code_file_path = code_file_path
        def on_modified(self, event):
            event_path = pathlib.Path(event.src_path)
            file_path = pathlib.Path(self.code_file_path)
            if event_path.absolute() == file_path.absolute():
                reload_effect_fn(event.src_path)

    parser = argparse.ArgumentParser()
    parser.add_argument('shape_file', type=str,
            help='Shape file. Basically a text file that contains a '
                 'whitespace separated number for each LED.')
    parser.add_argument('code_file', type=str,
            help='Code file. The code definition for the effect function '
                 'is stored here.')

    args = parser.parse_args()

    with open(args.shape_file, 'r') as f:
        canvas = ''.join(f.readlines())

    strip_length = get_length_from_canvas(canvas)
    print(f'Found {strip_length} number of LEDs in shape file.')

    if not reload_effect_fn(args.code_file):
        sys.exit(1)

    fs_event_handler = CodeFileEventHandler(args.code_file)

    observer = watchdog.observers.Observer()
    observer.schedule(fs_event_handler, dirname(args.code_file) or '.', recursive=False)
    observer.start()

    try:
        gameloop(canvas, strip_length, observer)
    finally:
        observer.stop()
        observer.join()



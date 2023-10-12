def effect_fn(iterator, current_color, static={}):
    running_idx = static.get('running_idx', 0)

    for i, c in enumerate(iterator):
        i += running_idx

        c.r = int((i / 72) * 255)
        c.g = int((i / 72) * 255)
        c.b = int((i / 72) * 255)

        static['running_idx'] = (running_idx + 1) % 72

def effect_fn(iterator, current_color):
    def scale_color(c, f):
        c.r = int(current_color.r * f)
        c.g = int(current_color.g * f)
        c.b = int(current_color.b * f)

    for i, c in enumerate(iterator):
        c.from_color(current_color)

        if 3 <= i <= 5:
            scale_color(c, 0.2)
        if (
            (62 <= i <= 65)
            or (67 <= i <= 70)
            or (0 <= i <= 2)
            or (6 <= i <= 8)
            or (14 <= i <= 17)
        ):
            scale_color(c, 0.4)
        if (55 <= i <= 61) or (66 <= i <= 66) or (9 <= i <= 13) or (18 <= i <= 20):
            scale_color(c, 0.6)

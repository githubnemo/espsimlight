def effect_fn(iterator, current_color):
    for i, c in enumerate(iterator):
        c.from_color(current_color)

        if 65 <= i <= 70:
            iterator[i] = current_color.fade_to_black(int(0.7 * 255))
        if (
            (55 <= i <= 58) or
            (61 <= i <= 67) or
            ( 0 <= i <= 11)
        ):
            iterator[i] = current_color.fade_to_black(int(0.55 * 255))
        if ((49 <= i <= 54) or
            (59 <= i <= 60) or
            ( 4 <= i <=  7) or
            (12 <= i <= 14)):
            iterator[i] = current_color.fade_to_black(int(0.4 * 255))

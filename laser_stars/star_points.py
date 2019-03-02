


CORNER_OFFSET = 277.0

STAR_OFFSET = 200.0

STARS = 6


total_len = CORNER_OFFSET * 2 + STAR_OFFSET * (STARS -1)

for i in range(STARS):
    for k in range(STARS):
        x = i * STAR_OFFSET + CORNER_OFFSET
        x = x / total_len - .5
        y = k * STAR_OFFSET + CORNER_OFFSET
        y = y / total_len - .5
        print('MoveTo {} {} 0.1'.format(x, y))

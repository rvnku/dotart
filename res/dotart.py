import sys
import random
import requests
import bs4
import termios
import tty


ALLOWED = ''\
    + ''.join(chr(i) for i in range(0x2800, 0x2900))\
    + ''.join(chr(i) for i in range(0x2580, 0x25B0))\
    + '❤️🧡💛💚💙💜🖤🤍🤎💔💕💖💗💘💞💓💟🩷'\
    + '🟥🟧🟨🟩🟦🟪🟫⬛⬜'\
    + '🔴🟠🟡🟢🔵🟣🟤⚫⚪'

OPTIONS = {
    '-c': 'create art by yourself',
    '-i': 'interactive mode',
    '-r': 'reverse color',
    '-t': 'set threshold',
    '-x': 'set width',
    '-y': 'set height',
}

BRAILLE_BITS = [
    (0, 0, 0x01), (0, 1, 0x02), (0, 2, 0x04), (0, 3, 0x40),
    (1, 0, 0x08), (1, 1, 0x10), (1, 2, 0x20), (1, 3, 0x80),
]


def check(text: str) -> bool:
    if text.count('\n') < 2:
        return False
    if sum(1 for c in text if c in ALLOWED) < 25:
        return False
    return True


def read_key():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        if (ch := sys.stdin.read(1)) == '\x1b':
            ch += sys.stdin.read(2)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def invert_braile(text: str) -> str:
    result = []
    for char in text:
        code = ord(char)
        if 0x2800 <= code <= 0x28FF:
            dots = code - 0x2800
            inverted = dots ^ 0xFF
            result.append(chr(0x2800 + inverted))
        else:
            result.append(char)
    return ''.join(result)


def show(bd: list, index: int, hint: bool = False, reverse: bool = False) -> int:
    text = bd[index]
    if reverse:
        text = invert_braile(text)
    print('\033[97m' + text + '\033[0m',
          f'Art: {index+1} / {len(bd)}', sep='\n')
    if hint:
        print('[←→ move | r reverse | enter exit]')
    return len(bd[index].split('\n')) + 1 + hint


def get_arts(query: str) -> list[str]:
    url = f'https://emojicombos.com/{query}'
    response = requests.get(url)
    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    divs = soup.find_all(class_='emojis')
    return list(t for t in [e.contents[0].text for e in divs] if check(t))


def img2braile(path: str, cols: int = None, rows: int = None, threshold: int = None, reverse: bool = False) -> str:
    from PIL import Image, ImageOps

    img = Image.open(path).convert('L')
    if reverse:
        img = ImageOps.invert(img)

    x, y = img.size
    ratio = x / y

    if cols:
        rows = rows or int(cols / ratio / 2)
    else:
        cols = int((rows or (rows := 25)) * ratio * 2)

    img = img.resize((cols * 2, rows * 4))
    pixels = img.load()

    threshold = threshold or sum(img.getdata()) // (cols * rows * 8)

    art = []
    for y in range(0, img.height, 4):
        line = ''
        for x in range(0, img.width, 2):
            code = 0x2800
            for dx, dy, bit in BRAILLE_BITS:
                if pixels[x + dx, y + dy] < threshold:
                    code |= bit
            line += chr(code)
        art.append(line)

    return '\n'.join(art), cols, rows, threshold


def create(path: str, cols: int = None, rows: int = None, threshold: int = None, reverse: bool = False):
    while 1:
        art, cols, rows, threshold = img2braile(path, cols, rows, threshold, reverse)
        sys.stdout.write('\033[H\033[J')
        print(art)
        print(f'Threshold: {threshold} | Size: {cols}x{rows}')
        print('[←→ threshold | ↑↓ size | r reverse | enter exit]')

        key = read_key()

        if key == '\x1b[D':
            threshold = max(5, threshold - 5)
        elif key == '\x1b[C':
            threshold = min(255, threshold + 5)
        elif key == '\x1b[A':
            cols, rows = None, min(100, rows + 1)
        elif key == '\x1b[B':
            cols, rows = None, max(5, rows - 1)
        elif key == 'r':
            reverse = not reverse
            threshold = 255 - threshold
        elif key == '\r':
            break


args, opts = sys.argv[1:], []
while args[0][:2] in OPTIONS:
    opts.append(args.pop(0))


if '-c' in opts:
    path = args[0]
    
    t = next((int(o[3:]) for o in opts if o.startswith('-t=')), None)
    x = next((int(o[3:]) for o in opts if o.startswith('-x=')), None)
    y = next((int(o[3:]) for o in opts if o.startswith('-y=')), None)
    r = next((True for o in opts if o == '-r'), None)

    if '-i' in opts:
        create(path, x, y, t, r)
    else:
        art, *_ = img2braile(path, x, y, t, r)
        print(art)

elif arts := get_arts('-'.join(args)):
    if '-i' in opts:
        lines, number = -1, 0
        reverse = '-r' in opts
        while 1:
            sys.stdout.write(f'\033[{lines}A')
            for _ in range(lines):
                sys.stdout.write('\033[2K')
                sys.stdout.write('\033[1B')
            sys.stdout.write(f'\033[{lines}A')
            sys.stdout.flush()
            
            lines = show(arts, number, True, reverse)
            key = read_key()
            if key == '\x1b[D':
                number -= number > 0
            if key == '\x1b[C':
                number += number < (len(arts) - 1)
            if key == 'r':
                reverse = not reverse
            if key == '\r':
                break
    else:
        number = random.randrange(len(arts))
        show(arts, number, False, '-r' in opts)
else:
    print('No art found v_v')

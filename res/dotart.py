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
    '-i': 'interactive mode'
}


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


def show(bd: list, index: int, hint: bool = False) -> int:
    print('\033[97m' + bd[index] + '\033[0m',
          f'Art: {index+1} / {len(bd)}', sep='\n')
    if hint:
        print('[←→ to move, enter to exit]')
    return len(bd[index].split('\n')) + 1 + hint


query = sys.argv[1:]
args = query.pop(0) if query[0] in OPTIONS else None
url = f'https://emojicombos.com/{'-'.join(query)}'
response = requests.get(url)
soup = bs4.BeautifulSoup(response.text, 'html.parser')
divs = soup.find_all(class_='emojis')
if arts := [t for t in [e.contents[0].text for e in divs] if check(t)]:
    match args:
        case '-i':
            lines, number = -1, 0
            while 1:
                sys.stdout.write(f'\033[{lines}A')
                for _ in range(lines):
                    sys.stdout.write('\033[2K')
                    sys.stdout.write('\033[1B')
                sys.stdout.write(f'\033[{lines}A')
                sys.stdout.flush()
                
                lines = show(arts, number, True)
                key = read_key()
                if key == '\x1b[D':
                    number -= number > 0
                if key == '\x1b[C':
                    number += number < (len(arts) - 1)
                if key == '\r':
                    break
        case _:
            number = random.randrange(len(arts))
            show(arts, number)
else:
    print('No art found v_v')

import sys
import random
import requests
import bs4

ALLOWED = ''\
    + ''.join(chr(i) for i in range(0x2800, 0x2900))\
    + ''.join(chr(i) for i in range(0x2580, 0x25B0))\
    + '❤️🧡💛💚💙💜🖤🤍🤎💔💕💖💗💘💞💓💟🩷'\
    + '🟥🟧🟨🟩🟦🟪🟫⬛⬜'\
    + '🔴🟠🟡🟢🔵🟣🟤⚫⚪'


def check(text: str) -> bool:
    if text.count('\n') < 2:
        return False
    if sum(1 for c in text if c in ALLOWED) < 25:
        return False
    return True
    

url = f'https://emojicombos.com/{'-'.join(sys.argv[1:])}'
response = requests.get(url)
soup = bs4.BeautifulSoup(response.text, 'html.parser')
divs = soup.find_all(class_='emojis')
if arts := [t for t in [e.contents[0].text for e in divs] if check(t)]:
    print('\033[97m', random.choice(arts), '\033[0m', sep='')

# Rematch: the FAME CHECKER becomes a book of tonight's reunion. For the 13 people at the party, their note
# ("From: X To: {PLAYER}") quotes a line they say tonight, and their second entry says where they were tonight.
# Writes data/text/fame_checker.inc in place (only those labels). Safe to run again.
import re, os
G = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = f'{G}/data/text/fame_checker.inc'
PEOPLE = [  # label, display name, female?, quote, where tonight, place
 ('ProfOak', 'PROF. OAK', False, "Give a child a POKéMON and a map, and get out of the way. It worked for you!", "The café, arguing with BLAINE about the new kids.", "REUNION CAFé"),
 ('Brock', 'BROCK', False, "Healing turned out to be harder than any GYM battle ever was.", "The rocky hollow in the garden, with ONIX.", "REUNION GARDEN"),
 ('Misty', 'MISTY', True, "Truth is, I trained harder after you left than I ever had before.", "Fishing at the garden pond. The fish were winning.", "REUNION GARDEN"),
 ('LtSurge', 'LT. SURGE', False, "Today I'm the one digging through junk. Elbow-deep in wires!", "The POWER PLANT, getting the lights back on.", "POWER PLANT"),
 ('Erika', 'ERIKA', True, "They grew back twice as lovely. Please tell it I forgave it long ago.", "Asleep among the flowers by the fountain.", "REUNION GARDEN"),
 ('Koga', 'KOGA', False, "My daughter runs the GYM now. She added even more walls.", "Hiding in a dark cave. Found, twice.", "DARK CAVE"),
 ('Sabrina', 'SABRINA', True, "I did not sense that I would lose. I've treasured it ever since.", "Her quiet house. She knew you were coming.", "SABRINA'S HOUSE"),
 ('Blaine', 'BLAINE', False, "Fire is easy. Patience is the hard part!", "The café, quizzing anyone who'd listen.", "REUNION CAFé"),
 ('Lorelei', 'LORELEI', True, "Ice melts. I never told them it was two kids from PALLET TOWN who taught me that.", "The tower. Still waiting for her scarf.", "THE TOWER"),
 ('Bruno', 'BRUNO', False, "One day, that trainer will come back. Today is that day!", "The tower, flexing with MACHOKE.", "THE TOWER"),
 ('Agatha', 'AGATHA', True, "It's good to see you. Look how you've grown.", "The tower, pretending not to be happy.", "THE TOWER"),
 ('Lance', 'LANCE', False, "You never traded them away for something flashier. That's real strength.", "The tower, with DRAGONITE.", "THE TOWER"),
 ('Giovanni', 'GIOVANNI', False, "It's been a long time since anyone held a door open for me.", "The harbor, with his old friends and MEOWTH.", "HARBOR"),
]
WIDTH = 30
def wrap(text):
    words, lines, cur = text.split(), [], ''
    for w in words:
        if len(cur) + len(w) + (1 if cur else 0) > WIDTH: lines.append(cur); cur = w
        else: cur = (cur + ' ' + w) if cur else w
    return lines + [cur]
def quote_lines(text):        # two lines per page
    lines = wrap(text); out = []
    for i, l in enumerate(lines):
        last = i == len(lines) - 1
        out.append(l + ('$' if last else ('\\n' if i % 2 == 0 else '\\p')))
    return out
def scroll_lines(text):       # first line, then scrolling lines
    lines = wrap(text)
    return [l + ('$' if i == len(lines) - 1 else ('\\n' if i == 0 else '\\l')) for i, l in enumerate(lines)]
def block(label, lines):
    return f'{label}::\n' + ''.join(f'\t.string "{l}"\n' for l in lines)
def replace(src, label, new):
    m = re.search(r'^%s::.*?(?=^\S|\Z)' % re.escape(label), src, re.S | re.M)
    assert m, label
    return src[:m.start()] + new + '\n' + src[m.end():].lstrip('\n') if not src[m.end():].startswith('\n') else src[:m.start()] + new + src[m.end():]
s = open(P).read()
for lab, name, female, quote, where, place in PEOPLE:
    font = '{FONT_FEMALE}' if female else '{FONT_MALE}'
    q = quote_lines(quote)
    q[0] = font + '{COLOR DARK_GRAY}{SHADOW LIGHT_GRAY}' + q[0]
    s = replace(s, f'gFameCheckerPersonQuote_{lab}', block(f'gFameCheckerPersonQuote_{lab}',
        ['{COLOR BLUE}{SHADOW LIGHT_BLUE}From: ' + name + '\\n', 'To: {PLAYER}\\p'] + q))
    w = scroll_lines(where); w[0] = '{COLOR DARK_GRAY}{SHADOW LIGHT_GRAY}' + w[0]
    s = replace(s, f'gFameCheckerFlavorText_{lab}1', block(f'gFameCheckerFlavorText_{lab}1',
        ['{COLOR BLUE}{SHADOW LIGHT_BLUE}Where were they tonight?\\p'] + w))
    s = replace(s, f'gFameCheckerFlavorTextOriginLocation_{lab}1', block(f'gFameCheckerFlavorTextOriginLocation_{lab}1', [place + '$']))
    s = replace(s, f'gFameCheckerFlavorTextOriginObjectName_{lab}1', block(f'gFameCheckerFlavorTextOriginObjectName_{lab}1', [name + '$']))
open(P, 'w').write(s)
print('fame checker texts:', len(PEOPLE))

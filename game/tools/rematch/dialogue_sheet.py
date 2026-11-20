# Builds docs/dialogue.md: every line of Rematch dialogue, grouped by place (in story order) and script.
# Run from anywhere: python3 game/tools/rematch/dialogue_sheet.py
import os, re
G = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
OUT = os.path.join(G, '..', 'docs', 'dialogue.md')
ORDER = [('Home (Mom)', 'data/scripts/rematch/house.pory'),
         ('Arrival harbor', 'data/maps/RematchHarbor/scripts.pory'),
         ('Café', 'data/maps/RematchHall/scripts.pory'),
         ('Garden', 'data/maps/RematchGarden/scripts.pory'),
         ('Pokémon Center', 'data/maps/RematchPokemonCenter/scripts.pory'),
         ('Mart', 'data/maps/RematchMart/scripts.pory'),
         ("Sabrina's room", 'data/maps/RematchSabrina/scripts.pory'),
         ("Koga's cave", 'data/maps/RematchKogaCave/scripts.pory'),
         ("Lt. Surge's Power Plant", 'data/maps/RematchPowerPlant/scripts.pory'),
         ('Elite Four tower', 'data/maps/RematchArena/scripts.pory'),
         ("Creator's room", 'data/maps/RematchCreator/scripts.pory')]
TEXT = re.compile(r'(msgbox|message)\(\s*format\("((?:[^"\\]|\\.)*)"\)|"((?:[^"\\]|\\.)*\\n(?:[^"\\]|\\.)*)"')
def clean(t):
    return (t.replace('\\p', '\n\n').replace('\\n', ' ').replace('\\l', ' ').replace('“', '"').replace('”', '"'))
out = ['# Rematch: all dialogue', '',
       'Generated from the game scripts by `game/tools/rematch/dialogue_sheet.py`. Each box is one message window '
       'sequence; blank lines are page breaks (the player presses A). Variables: `{PLAYER}` (default RED), `{RIVAL}` (BLUE), `{BORN_YEAR}` (1993), `{PLAY_YEAR}` (2007); derived from them and '
       'the current year: `{AGE_THEN}` (age when they played), `{AGE_NOW}`, `{YEARS_AGO}` (years since they played).', '']
for place, path in ORDER:
    src = open(os.path.join(G, path), encoding='utf-8').read()
    out += [f'## {place}', '']
    for m in re.finditer(r'script (\w+) \{(.*?)\n\}', src, re.S):
        name, body = m.group(1), m.group(2)
        lines = []
        for t in TEXT.finditer(body):
            txt = t.group(2) if t.group(2) is not None else t.group(3)
            if txt: lines.append(clean(txt))
        if not lines: continue
        who = re.sub(r'^Rematch_\w+?_EventScript_', '', name)
        out += [f'### {who}', '']
        for l in lines:
            out += ['> ' + p if p else '>' for p in l.split('\n')] + ['']
open(OUT, 'w', encoding='utf-8').write('\n'.join(out))
print(OUT, sum(1 for l in out if l.startswith('### ')), 'scripts')

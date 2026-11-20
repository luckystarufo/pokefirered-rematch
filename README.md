# Pokémon FireRed: Rematch

*A fan-made, one-evening reunion for everyone who once left Pallet Town with a map and a dream.*

> A letter arrives with no name on it.
> *"Tonight, everyone from that journey is gathering one more time."*

<p align="center">
  <img src="docs/screenshots/01-the-letter.png" width="400" alt="Mom reads the letter at home">
  <img src="docs/screenshots/02-welcome-back.png" width="400" alt="The rival waits in the garden">
  <br>
  <img src="docs/screenshots/03-side-by-side.png" width="400" alt="Red and Blue, side by side against Lorelei">
  <img src="docs/screenshots/04-one-more-time.png" width="400" alt="In 2007, a 14-year-old named RED set off with a dream">
</p>

Years later, you take the ferry back. The Gym Leaders are scattered around a garden by the sea, still
themselves, just a little older. Your rival is waiting on the steps, pretending it's the sea breeze in his
eyes. And the Elite Four have one last rematch planned, but this time he fights beside you.

It takes an hour or two. There is no saving: like the night itself, it happens once.

## Build it

You don't need an original ROM. Everything builds from source, thanks to the
[pret/pokefirered](https://github.com/pret/pokefirered) decompilation this project is based on.

1. Install [Docker](https://www.docker.com/).
2. From the repository root, run:
   ```sh
   tools/rom-builder/make.sh
   ```
   The first run builds the toolchain image (agbcc, Poryscript), which takes a few minutes.
3. Open `game/pokefirered.gba` in an emulator such as [mGBA](https://mgba.io/downloads.html).
   On a recent macOS, if you hear sound but see a black screen, set
   **Settings → Display → Display driver** to **Software**.

To make it someone's own night, change the names and years in `game/src/rematch_block.c`
(by default: RED, his rival BLUE, born 1993, played in 2007) and build again.

## What's inside

| Path | What it is |
|---|---|
| `game/` | The fork of pret/pokefirered. Our maps are `data/maps/Rematch*`, our C code `src/rematch*.c`, our map and sprite generators `tools/rematch/` |
| `tools/rom-builder/` | The Docker toolchain behind `make.sh` |
| `docs/dialogue.md` | The whole script of the night, every line |

## Fan-made, with love

This is an unofficial, non-commercial fan project. It is not affiliated with, endorsed by, or connected to
Nintendo, Game Freak, Creatures Inc. or The Pokémon Company. Pokémon and all related names are trademarks of
their respective owners. No ROM is distributed here: you build your own from source. Please support the
official games.

Built on the work of [pret](https://github.com/pret), [agbcc](https://github.com/pret/agbcc) and
[Poryscript](https://github.com/huderlem/poryscript).

*Thank you for playing, one more time.*

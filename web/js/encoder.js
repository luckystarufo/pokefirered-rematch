// The personalization block: the "API contract" between this page and the game.
// Layout v1 (game/include/rematch.h): 128 bytes, little-endian, text in the Gen 3 charset (EOS = 0xFF).
//   0x00 magic "RMCH" | 0x04 u16 version | 0x06 u16 size | 0x08 playerName[8] | 0x10 rivalName[8]
//   0x18 u8 gender | 0x19 u8 flags (bit 0: hold at THE END) | 0x1A u16 yearPlayed | 0x1C u16 birthYear | 0x1E u16 currentYear | rest: zero

// Characters a name may use, and their Gen 3 codes (from game/charmap.txt)
export const CHARSET = {"A": 187, "B": 188, "C": 189, "D": 190, "E": 191, "F": 192, "G": 193, "H": 194, "I": 195, "J": 196, "K": 197, "L": 198, "M": 199, "N": 200, "O": 201, "P": 202, "Q": 203, "R": 204, "S": 205, "T": 206, "U": 207, "V": 208, "W": 209, "X": 210, "Y": 211, "Z": 212, "a": 213, "b": 214, "c": 215, "d": 216, "e": 217, "f": 218, "g": 219, "h": 220, "i": 221, "j": 222, "k": 223, "l": 224, "m": 225, "n": 226, "o": 227, "p": 228, "q": 229, "r": 230, "s": 231, "t": 232, "u": 233, "v": 234, "w": 235, "x": 236, "y": 237, "z": 238, "0": 161, "1": 162, "2": 163, "3": 164, "4": 165, "5": 166, "6": 167, "7": 168, "8": 169, "9": 170, " ": 0, ".": 173, ",": 184, "!": 171, "?": 172, "-": 174, "'": 180, "é": 27};
const EOS = 0xff;
export const NAME_MAX = 7;
export const BLOCK_VERSION = 1;
export const BLOCK_SIZE = 128;

export function nameError(name) {
  if (!name) return "can't be empty";
  if (name.length > NAME_MAX) return `${NAME_MAX} letters at most`;
  for (const c of name) if (!(c in CHARSET)) return `"${c}" isn't in the GBA's alphabet`;
  return null;
}

function writeName(view, offset, name) {
  for (let i = 0; i < NAME_MAX + 1; i++) view.setUint8(offset + i, EOS);
  [...name].forEach((c, i) => view.setUint8(offset + i, CHARSET[c]));
}

// answers: { playerName, rivalName, gender: 0 boy / 1 girl, birthYear, yearPlayed, currentYear }
export function encodeBlock(a) {
  const bytes = new Uint8Array(BLOCK_SIZE);
  const view = new DataView(bytes.buffer);
  "RMCH".split("").forEach((c, i) => view.setUint8(i, c.charCodeAt(0)));
  view.setUint16(0x04, BLOCK_VERSION, true);
  view.setUint16(0x06, BLOCK_SIZE, true);
  writeName(view, 0x08, a.playerName);
  writeName(view, 0x10, a.rivalName);
  view.setUint8(0x18, a.gender);
  view.setUint8(0x19, a.holdAtTheEnd ? 1 : 0);
  view.setUint16(0x1a, a.yearPlayed, true);
  view.setUint16(0x1c, a.birthYear, true);
  view.setUint16(0x1e, a.currentYear, true);
  return bytes;
}

// Writes the block into a copy of the ROM at the offset the build reported, after checking it's really there.
export function patchRom(rom, manifest, answers) {
  const off = manifest.block.romOffset;
  const magic = String.fromCharCode(...rom.slice(off, off + 4));
  if (magic !== manifest.block.magic) throw new Error(`No personalization block at ${off} (found "${magic}")`);
  const out = new Uint8Array(rom);
  out.set(encodeBlock(answers), off);
  return out;
}

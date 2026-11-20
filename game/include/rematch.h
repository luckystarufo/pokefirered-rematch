#ifndef GUARD_REMATCH_H
#define GUARD_REMATCH_H

// ---------------------------------------------------------------------------
// Rematch personalization block — the "API contract" between the web page
// and the game (see CLAUDE.md §3).
//
// The block lives at a FIXED ROM address (REMATCH_BLOCK_ADDR, placed by the
// `.rematch_block` section in ld_script.ld). The browser overwrites these
// bytes in its in-memory copy of the ROM before booting. The build emits
// rom-manifest.json describing where it is.
//
// Layout v1 (128 bytes, little-endian, text in the Gen 3 charset with EOS=0xFF):
//   0x00 magic[4]        "RMCH" (plain ASCII)
//   0x04 u16 version     REMATCH_BLOCK_VERSION
//   0x06 u16 size        sizeof(struct RematchBlock) = 128
//   0x08 playerName[8]   up to 7 chars + EOS
//   0x10 rivalName[8]    up to 7 chars + EOS
//   0x18 u8  gender      0 = boy, 1 = girl
//   0x19 u8  reserved0
//   0x1A u16 yearPlayed  e.g. 2007
//   0x1C u16 birthYear   e.g. 1993
//   0x1E u16 currentYear filled by the browser (the GBA has no clock here)
//   0x20 mons[3]         24 bytes each (see struct RematchMon) - UNUSED since the teams are fixed (src/rematch.c)
//   0x68 reserved[24]
//
// Step 2.1 moves this definition into contract/schema.json and generates it.
// ---------------------------------------------------------------------------

#define REMATCH_BLOCK_ADDR     0x08FFF000
#define REMATCH_BLOCK_VERSION  1
#define REMATCH_BLOCK_SIZE     128
#define REMATCH_PARTY_SIZE     3

// RAM marker the web page polls to detect the ending (address in the manifest).
#define REMATCH_MARKER_NONE           0
#define REMATCH_MARKER_ENDING_STARTED 0x524D0001 // ending scene began
#define REMATCH_MARKER_THE_END        0x524D0002 // credits reached "THE END"

struct RematchMon
{
    /*0x00*/ u16 species;                       // internal species ID (SPECIES_*)
    /*0x02*/ u16 moves[MAX_MON_MOVES];          // MOVE_*; MOVE_NONE = empty slot
    /*0x0A*/ u8 level;                          // 1..100
    /*0x0B*/ u8 nickname[POKEMON_NAME_LENGTH + 1]; // EOS-terminated; empty = species name
    /*0x16*/ u8 reserved[2];
}; // 24 bytes

struct RematchBlock
{
    /*0x00*/ u8 magic[4];
    /*0x04*/ u16 version;
    /*0x06*/ u16 size;
    /*0x08*/ u8 playerName[PLAYER_NAME_LENGTH + 1];
    /*0x10*/ u8 rivalName[PLAYER_NAME_LENGTH + 1];
    /*0x18*/ u8 gender;
    /*0x19*/ u8 reserved0;
    /*0x1A*/ u16 yearPlayed;
    /*0x1C*/ u16 birthYear;
    /*0x1E*/ u16 currentYear;
    /*0x20*/ struct RematchMon mons[REMATCH_PARTY_SIZE];
    /*0x68*/ u8 reserved[24];
}; // 128 bytes

STATIC_ASSERT(sizeof(struct RematchMon) == 24, RematchMonSize)
STATIC_ASSERT(sizeof(struct RematchBlock) == REMATCH_BLOCK_SIZE, RematchBlockSize)

extern const struct RematchBlock gRematchBlock;
extern u32 gRematchEndMarker;

// The block to use: gRematchBlock if its magic/version are valid, otherwise
// built-in fallback values (so a bad patch still boots a playable game).
const struct RematchBlock *Rematch_GetBlock(void);

void Rematch_OnNewGame(void);
void Rematch_SetEndMarker(u32 value);
void Rematch_GivePlayerTeam(void);
void Rematch_UnlockFamePage(void);
void Rematch_OpenTeam(void);   // src/party_menu.c
void Rematch_OpenBag(void);    // src/item_menu.c
void Rematch_DoTheEnd(void);   // src/credits.c: straight to "THE END" after the dinner finale
void Rematch_LendRivalMon(void);
void Rematch_ReturnRivalMon(void);

// Text placeholder expanders (see string_util.c / charmap.txt)
u8 *Rematch_ExpandFav1(void);
u8 *Rematch_ExpandFav2(void);
u8 *Rematch_ExpandFav3(void);
u8 *Rematch_ExpandAgeThen(void);
u8 *Rematch_ExpandYearsAgo(void);
u8 *Rematch_ExpandYearThen(void);
u8 *Rematch_ExpandAgeNow(void);
u8 *Rematch_ExpandBornYear(void);

#endif // GUARD_REMATCH_H

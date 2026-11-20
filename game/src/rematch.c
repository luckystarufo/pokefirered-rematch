#include "global.h"
#include "rematch.h"
#include "data.h"
#include "event_data.h"
#include "pokedex.h"
#include "pokemon.h"
#include "script.h"
#include "string_util.h"
#include "text.h"
#include "constants/species.h"
#include "constants/fame_checker.h"
#include "constants/moves.h"
#include "constants/region_map_sections.h"

// ---------------------------------------------------------------------------
// Rematch: everything the game does with the personalization block.
//   - New Game: name, gender, rival, the 3 POKéMON, starting flags (step 1.8)
//   - Text placeholders {FAV1} {AGE_THEN} {YEARS_AGO} ... (step 1.9)
//   - The RAM marker the web page polls for the ending (step 1.12)
// ---------------------------------------------------------------------------

extern const u8 Rematch_EventScript_NewGame[];

// RAM marker polled by the web page. Its address is written to
// rom-manifest.json at build time (looked up from the linked ELF).
EWRAM_DATA u32 gRematchEndMarker = 0;

// Scratch buffer for expanded placeholders. StringExpandPlaceholders copies
// each expansion out immediately, so one buffer can be reused.
static EWRAM_DATA u8 sPlaceholderBuf[POKEMON_NAME_LENGTH + 1] = {0};

// Used if the block in ROM is missing or corrupt (bad magic/version/size):
// the game still boots into a playable tour instead of crashing.
static const struct RematchBlock sFallbackBlock =
{
    .magic = {'R', 'M', 'C', 'H'},
    .version = REMATCH_BLOCK_VERSION,
    .size = REMATCH_BLOCK_SIZE,
    .playerName = _("RED"),
    .rivalName = _("BLUE"),
    .gender = MALE,
    .yearPlayed = 2007,
    .birthYear = 1993,
    .currentYear = 2026,
    .mons =
    {
        { .species = SPECIES_PIKACHU, .moves = {MOVE_THUNDERBOLT, MOVE_QUICK_ATTACK, MOVE_IRON_TAIL, MOVE_THUNDER_WAVE}, .level = 60, .nickname = _("") },
        { .species = SPECIES_NONE },
        { .species = SPECIES_NONE },
    },
};

const struct RematchBlock *Rematch_GetBlock(void)
{
    const struct RematchBlock *b = &gRematchBlock;

    if (b->magic[0] == 'R' && b->magic[1] == 'M' && b->magic[2] == 'C' && b->magic[3] == 'H'
     && b->version == REMATCH_BLOCK_VERSION && b->size == REMATCH_BLOCK_SIZE)
        return b;
    return &sFallbackBlock;
}

// Copy a Gen 3 string of at most maxLen chars, always EOS-terminated, even if
// the source is missing its terminator. Returns the number of chars copied.
static u8 CopyBoundedString(u8 *dest, const u8 *src, u8 maxLen)
{
    u8 i;

    for (i = 0; i < maxLen && src[i] != EOS; i++)
        dest[i] = src[i];
    dest[i] = EOS;
    return i;
}

static bool8 IsValidSpecies(u16 species)
{
    if (species == SPECIES_NONE || species >= NUM_SPECIES)
        return FALSE;
    if (species >= SPECIES_OLD_UNOWN_B && species <= SPECIES_OLD_UNOWN_Z)
        return FALSE; // the 25 empty Gen 2 -> 3 filler slots
    return TRUE;
}

static void GiveRematchMon(const struct RematchMon *src)
{
    struct Pokemon mon;
    u8 nickname[POKEMON_NAME_LENGTH + 1];
    u8 level, i, slot;
    u8 friendship = MAX_FRIENDSHIP;
    bool8 hasCustomMoves = FALSE;

    if (!IsValidSpecies(src->species))
        return;

    level = src->level;
    if (level < 1 || level > MAX_LEVEL)
        level = 50;

    // Perfect IVs: these are the player's old champions.
    CreateMon(&mon, src->species, level, MAX_PER_STAT_IVS, FALSE, 0, OT_ID_PLAYER_ID, 0);

    for (i = 0; i < MAX_MON_MOVES; i++)
    {
        if (src->moves[i] != MOVE_NONE && src->moves[i] < MOVES_COUNT)
            hasCustomMoves = TRUE;
    }
    // If no valid moves were chosen, keep the level-up moves CreateMon picked.
    if (hasCustomMoves)
    {
        for (i = 0; i < MAX_MON_MOVES; i++)
            SetMonMoveSlot(&mon, MOVE_NONE, i);
        for (i = 0, slot = 0; i < MAX_MON_MOVES; i++)
        {
            if (src->moves[i] != MOVE_NONE && src->moves[i] < MOVES_COUNT)
                SetMonMoveSlot(&mon, src->moves[i], slot++);
        }
    }

    if (CopyBoundedString(nickname, src->nickname, POKEMON_NAME_LENGTH) > 0)
        SetMonData(&mon, MON_DATA_NICKNAME, nickname);
    SetMonData(&mon, MON_DATA_FRIENDSHIP, &friendship);

    GiveMonToPlayer(&mon);
    GetSetPokedexFlag(SpeciesToNationalPokedexNum(src->species), FLAG_SET_SEEN);
    GetSetPokedexFlag(SpeciesToNationalPokedexNum(src->species), FLAG_SET_CAUGHT);
}

// The teams are fixed (decided 2026-11-17): the player always brings CHARIZARD, PIKACHU and LAPRAS
// (they carry CUT, FLASH and SURF), and the rival brings BLASTOISE, SNORLAX and ALAKAZAM to the ELITE
// FOUR. 24 different moves across the six, each POKéMON playing to its type. The favourites in the
// personalization block are no longer used for the party or for {FAV1}..{FAV3}.
#define REMATCH_TEAM_LEVEL 60
static const struct RematchMon sPlayerTeam[REMATCH_PARTY_SIZE] = {
    { .species = SPECIES_CHARIZARD, .moves = {MOVE_FLAMETHROWER, MOVE_CUT, MOVE_DRAGON_CLAW, MOVE_AERIAL_ACE}, .level = REMATCH_TEAM_LEVEL, .nickname = _("") },
    { .species = SPECIES_PIKACHU,   .moves = {MOVE_THUNDERBOLT, MOVE_FLASH, MOVE_QUICK_ATTACK, MOVE_IRON_TAIL}, .level = REMATCH_TEAM_LEVEL, .nickname = _("") },
    { .species = SPECIES_LAPRAS,    .moves = {MOVE_SURF, MOVE_ICE_BEAM, MOVE_BLIZZARD, MOVE_SING},              .level = REMATCH_TEAM_LEVEL, .nickname = _("") },
};
static const struct RematchMon sRivalTeam[3] = {
    { .species = SPECIES_BLASTOISE, .moves = {MOVE_HYDRO_PUMP, MOVE_BITE, MOVE_BRICK_BREAK, MOVE_PROTECT},      .level = REMATCH_TEAM_LEVEL },
    { .species = SPECIES_SNORLAX,   .moves = {MOVE_BODY_SLAM, MOVE_ROCK_SLIDE, MOVE_SHADOW_BALL, MOVE_AMNESIA}, .level = REMATCH_TEAM_LEVEL },
    { .species = SPECIES_ALAKAZAM,  .moves = {MOVE_PSYCHIC, MOVE_CALM_MIND, MOVE_RECOVER, MOVE_REFLECT},       .level = REMATCH_TEAM_LEVEL },
};

// Called at the end of NewGameInitData() (src/new_game.c), i.e. after the
// vanilla new-game reset, instead of Professor Oak's intro speech.
void Rematch_OnNewGame(void)
{
    const struct RematchBlock *b = Rematch_GetBlock();

    gSaveBlock2Ptr->playerGender = (b->gender == FEMALE) ? FEMALE : MALE;
    if (CopyBoundedString(gSaveBlock2Ptr->playerName, b->playerName, PLAYER_NAME_LENGTH) == 0)
        CopyBoundedString(gSaveBlock2Ptr->playerName, sFallbackBlock.playerName, PLAYER_NAME_LENGTH);
    if (CopyBoundedString(gSaveBlock1Ptr->rivalName, b->rivalName, PLAYER_NAME_LENGTH) == 0)
        CopyBoundedString(gSaveBlock1Ptr->rivalName, sFallbackBlock.rivalName, PLAYER_NAME_LENGTH);

    // Friends shouldn't have to dig through the OPTIONS menu.
    gSaveBlock2Ptr->optionsTextSpeed = OPTIONS_TEXT_SPEED_FAST;

    // The team joins later, when MOM tells you to take them (special Rematch_GivePlayerTeam).

    gRematchEndMarker = REMATCH_MARKER_NONE;

    // Story flags, items, map state: data/scripts/rematch/new_game.pory
    RunScriptImmediately(Rematch_EventScript_NewGame);
}

// special Rematch_GivePlayerTeam: MOM's "Take them with you" (data/scripts/rematch/house.pory)
void Rematch_GivePlayerTeam(void)
{
    u8 i;

    for (i = 0; i < REMATCH_PARTY_SIZE; i++)
        GiveRematchMon(&sPlayerTeam[i]);
}

// special Rematch_UnlockFamePage (VAR_0x8009 = FAMECHECKER_*): the person's page in the FAME CHECKER, as a
// book of tonight's reunion: their note (in color) and the "where were they tonight" entry (index 1;
// texts: tools/rematch/fame_checker_texts.py)
void Rematch_UnlockFamePage(void)
{
    if (gSpecialVar_0x8009 < NUM_FAMECHECKER_PERSONS)
    {
        gSaveBlock1Ptr->fameChecker[gSpecialVar_0x8009].flavorTextFlags |= 1 << 1;
        gSaveBlock1Ptr->fameChecker[gSpecialVar_0x8009].pickState = FCPICKSTATE_COLORED;
    }
}

void Rematch_SetEndMarker(u32 value)
{
    gRematchEndMarker = value;
}

// The rival teams up with the player for the ELITE FOUR double battles: his BLASTOISE, SNORLAX and
// ALAKAZAM join the player's party (BLASTOISE in slot 2, so it fights next to CHARIZARD; the other two
// after the player's own) and leave again afterwards. They count as the player's own POKéMON, otherwise
// Lv 60 traded POKéMON could disobey.
static bool8 IsRivalMon(struct Pokemon *mon)
{
    u8 i;
    u16 species = GetMonData(mon, MON_DATA_SPECIES);

    if (GetMonData(mon, MON_DATA_MET_LEVEL) != REMATCH_TEAM_LEVEL
     || GetMonData(mon, MON_DATA_MET_LOCATION) != METLOC_FATEFUL_ENCOUNTER)
        return FALSE;
    for (i = 0; i < ARRAY_COUNT(sRivalTeam); i++)
        if (species == sRivalTeam[i].species)
            return TRUE;
    return FALSE;
}

static void InsertRivalMon(const struct RematchMon *src, u8 slot)
{
    struct Pokemon mon;
    u8 i, metLevel = REMATCH_TEAM_LEVEL, metLocation = METLOC_FATEFUL_ENCOUNTER;

    if (gPlayerPartyCount >= PARTY_SIZE)
        return;
    if (slot > gPlayerPartyCount)
        slot = gPlayerPartyCount;
    CreateMon(&mon, src->species, src->level, MAX_PER_STAT_IVS, FALSE, 0, OT_ID_PLAYER_ID, 0);
    for (i = 0; i < MAX_MON_MOVES; i++)
        SetMonMoveSlot(&mon, src->moves[i], i);
    SetMonData(&mon, MON_DATA_MET_LEVEL, &metLevel);
    SetMonData(&mon, MON_DATA_MET_LOCATION, &metLocation);
    for (i = gPlayerPartyCount; i > slot; i--)
        gPlayerParty[i] = gPlayerParty[i - 1];
    gPlayerParty[slot] = mon;
    CalculatePlayerPartyCount();
}

// special Rematch_LendRivalMon
void Rematch_LendRivalMon(void)
{
    u8 i;

    for (i = 0; i < gPlayerPartyCount; i++)
        if (IsRivalMon(&gPlayerParty[i]))
            return; // already with the player
    InsertRivalMon(&sRivalTeam[0], 1);
    InsertRivalMon(&sRivalTeam[1], PARTY_SIZE);
    InsertRivalMon(&sRivalTeam[2], PARTY_SIZE);
}

// special Rematch_ReturnRivalMon
void Rematch_ReturnRivalMon(void)
{
    u8 i, j;

    for (i = 0; i < gPlayerPartyCount; )
    {
        if (IsRivalMon(&gPlayerParty[i]))
        {
            for (j = i; j < PARTY_SIZE - 1; j++)
                gPlayerParty[j] = gPlayerParty[j + 1];
            ZeroMonData(&gPlayerParty[PARTY_SIZE - 1]);
            CalculatePlayerPartyCount();
        }
        else
        {
            i++;
        }
    }
}

// special Rematch_MarkEndingStarted (called from the ending script)
void Rematch_MarkEndingStarted(void)
{
    Rematch_SetEndMarker(REMATCH_MARKER_ENDING_STARTED);
}

// ---------------------------------------------------------------------------
// Placeholders
// ---------------------------------------------------------------------------

static u8 *ExpandFav(u8 i)
{
    CopyBoundedString(sPlaceholderBuf, gSpeciesNames[sPlayerTeam[i].species], POKEMON_NAME_LENGTH);
    return sPlaceholderBuf;
}

// Prints a small non-negative number; "?" if the inputs make no sense
// (e.g. a birth year after the year they played).
static u8 *ExpandNumber(s32 value, u8 maxDigits)
{
    if (value < 0 || value > 9999)
    {
        sPlaceholderBuf[0] = CHAR_QUESTION_MARK;
        sPlaceholderBuf[1] = EOS;
    }
    else
    {
        ConvertIntToDecimalStringN(sPlaceholderBuf, value, STR_CONV_MODE_LEFT_ALIGN, maxDigits);
    }
    return sPlaceholderBuf;
}

u8 *Rematch_ExpandFav1(void) { return ExpandFav(0); }
u8 *Rematch_ExpandFav2(void) { return ExpandFav(1); }
u8 *Rematch_ExpandFav3(void) { return ExpandFav(2); }

u8 *Rematch_ExpandAgeThen(void)
{
    const struct RematchBlock *b = Rematch_GetBlock();
    return ExpandNumber((s32)b->yearPlayed - b->birthYear, 3);
}

u8 *Rematch_ExpandYearsAgo(void)
{
    const struct RematchBlock *b = Rematch_GetBlock();
    return ExpandNumber((s32)b->currentYear - b->yearPlayed, 3);
}

u8 *Rematch_ExpandYearThen(void)
{
    return ExpandNumber(Rematch_GetBlock()->yearPlayed, 4);
}

u8 *Rematch_ExpandBornYear(void)
{
    return ExpandNumber(Rematch_GetBlock()->birthYear, 4);
}

u8 *Rematch_ExpandAgeNow(void)
{
    const struct RematchBlock *b = Rematch_GetBlock();
    return ExpandNumber((s32)b->currentYear - b->birthYear, 3);
}

#include "global.h"
#include "rematch.h"
#include "constants/species.h"
#include "constants/moves.h"

// The personalization block itself. It is the ONLY thing in the
// `.rematch_block` section, which ld_script.ld pins to REMATCH_BLOCK_ADDR.
//
// These are the "dev" defaults used when the ROM is played unpatched (e.g. in
// mGBA desktop). The web page overwrites all 128 bytes before booting.
//
// It lives in its own file on purpose: code in other files reads it through
// an `extern` declaration, so the compiler can never "bake in" these default
// values — every read really goes to the ROM address the browser patched.
const struct RematchBlock gRematchBlock __attribute__((section(".rematch_block"))) =
{
    .magic = {'R', 'M', 'C', 'H'},
    .version = REMATCH_BLOCK_VERSION,
    .size = REMATCH_BLOCK_SIZE,
    .playerName = _("RED"),
    .rivalName = _("BLUE"),
    .gender = MALE,
    .yearPlayed = 2007,
    .birthYear = 1993,
    .currentYear = 2026, // the web page writes the real current year (browser clock); the GBA has no clock
    .mons =
    {
        {
            .species = SPECIES_CHARIZARD,
            .moves = {MOVE_FLAMETHROWER, MOVE_DRAGON_CLAW, MOVE_WING_ATTACK, MOVE_EARTHQUAKE},
            .level = 60,
            .nickname = _(""),
        },
        {
            .species = SPECIES_PIKACHU,
            .moves = {MOVE_THUNDERBOLT, MOVE_QUICK_ATTACK, MOVE_IRON_TAIL, MOVE_THUNDER_WAVE},
            .level = 60,
            .nickname = _("SPARKY"),
        },
        {
            .species = SPECIES_LAPRAS,
            .moves = {MOVE_SURF, MOVE_ICE_BEAM, MOVE_BODY_SLAM, MOVE_CONFUSE_RAY},
            .level = 60,
            .nickname = _(""),
        },
    },
};

// Rematch: the page. Answers -> personalization block -> patched ROM (in memory only) -> EmulatorJS.
// Nothing is stored: no cookies, no localStorage, no saves. Reloading starts over.
import { nameError, patchRom } from "./encoder.js";

const EMULATORJS = "emulator/"; // our own copy of EmulatorJS 4.2.3 (tools/fetch-web-vendor.sh)
const CLOSING_MESSAGE =
  "Thank you for coming back.\n\nEveryone was so happy to see you.\n\n— with love";

const $ = (id) => document.getElementById(id);
const show = (id) => ["gate", "intro", "play", "closing"].forEach((s) => ($(s).hidden = s !== id));

// AWS only lets CloudFront sign a request body to the API if the page says what the body's SHA-256 is
// (x-amz-content-sha256); anything that doesn't match is refused before the API runs.
async function postJson(url, body) {
  const text = JSON.stringify(body);
  const hash = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text));
  const hex = [...new Uint8Array(hash)].map((b) => b.toString(16).padStart(2, "0")).join("");
  return fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json", "x-amz-content-sha256": hex },
    body: text,
  });
}

// --- The gate -----------------------------------------------------------------------------------------
// The server keeps the rules (in AWS: Lambda + CloudFront; locally: tools/serve-web.py). A code is good for
// 24 hours from the first time it's entered; the session is an HttpOnly cookie the page never touches.
function welcome(name) {
  $("welcome").textContent = name ? `Welcome back, ${name}.` : "";
  $("welcome").hidden = !name;
  show("intro");
}

async function checkSession() {
  try {
    const r = await fetch("api/session");
    if (r.ok) return welcome((await r.json()).name);
  } catch {}
  show("gate");
}

$("code-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const code = $("code").value.trim();
  $("code-error").textContent = "";
  if (!code) { $("code-error").textContent = "Enter the code from your letter."; return; }
  $("code-go").disabled = true;
  try {
    const r = await postJson("api/invite", { code });
    if (r.ok) return welcome((await r.json()).name);
    $("code-error").textContent = r.status === 410
      ? "This invitation has expired. Ask the host for a fresh one."
      : r.status === 429
        ? "Too many tries from here. Take a break and try again in an hour."
        : "That code doesn't match any letter. Check it and try again.";
  } catch {
    $("code-error").textContent = "Couldn't reach the host just now. Try again in a moment.";
  } finally {
    $("code-go").disabled = false;
  }
});

$("request-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const email = $("req-email").value.trim();
  const why = $("req-why").value.trim();
  $("request-error").textContent = "";
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email) || !why) {
    $("request-error").textContent = "Tell us where to send the letter, and a few words about your journey.";
    return;
  }
  $("request-send").disabled = true;
  try {
    const r = await postJson("api/invite-requests", { email, why, website: e.target.website.value });
    if (r.status === 429) throw new Error("Too many requests from here. Try again in an hour.");
    if (!r.ok) throw new Error("Couldn't send it just now. Your words are still here: try again in a moment.");
    $("request-form").hidden = true;
    $("request-done").textContent =
      `Your request is on its way. If a letter comes, it'll arrive at ${email}. Until then, keep your POKéMON healthy.`;
    $("request-done").hidden = false;
  } catch (err) {
    $("request-error").textContent = err.message;
    $("request-send").disabled = false;
  }
});

checkSession();

function readAnswers(form) {
  const f = new FormData(form);
  const currentYear = new Date().getFullYear();
  const a = {
    playerName: f.get("playerName").trim(),
    rivalName: f.get("rivalName").trim(),
    gender: Number(f.get("gender")),
    birthYear: Number(f.get("birthYear")),
    yearPlayed: Number(f.get("yearPlayed")),
    currentYear,
  };
  const problems = [];
  const pe = nameError(a.playerName); if (pe) problems.push(`Your name: ${pe}.`);
  const re = nameError(a.rivalName); if (re) problems.push(`Rival's name: ${re}.`);
  if (!(a.birthYear >= 1940 && a.birthYear <= currentYear - 3)) problems.push("Birth year looks off.");
  if (!(a.yearPlayed >= 1996 && a.yearPlayed <= currentYear)) problems.push("The year you played should be 1996 or later.");
  else if (a.yearPlayed < a.birthYear + 3) problems.push("You'd have been a bit young to play that year!");
  return { answers: a, problems };
}

async function start(answers) {
  // ?rom=test loads a local test build (rom/test.gba + rom/test-manifest.json), for development only
  const test = new URLSearchParams(location.search).get("rom") === "test";
  const get = async (url) => {
    const r = await fetch(url);
    if (r.status === 401) { show("gate"); throw new Error("Your invitation has expired. Ask the host for a fresh one."); }
    if (!r.ok) throw new Error("HTTP " + r.status);
    return r;
  };
  const [manifest, rom] = await Promise.all([
    get(test ? "rom/test-manifest.json" : "rom/rom-manifest.json").then((r) => r.json()),
    get(test ? "rom/test.gba" : "rom/pokefirered.gba").then((r) => r.arrayBuffer()),
  ]);
  // the web page takes over after THE END: the game holds there with music instead of looping
  const patched = patchRom(new Uint8Array(rom), manifest, { ...answers, holdAtTheEnd: true });
  window.rematchAnswers = answers; // sent along with the message to the creator
  const romUrl = URL.createObjectURL(new Blob([patched], { type: "application/octet-stream" }));

  show("play");
  // Closing or reloading mid-game loses the night: ask first. Registered (capture phase) before
  // EmulatorJS loads, because EmulatorJS's own beforeunload handler shuts the core down right away,
  // even when the player then clicks Cancel. Ours runs first and stops it from running.
  window.addEventListener("beforeunload", warnBeforeLeaving, { capture: true });

  Object.assign(window, {
    EJS_player: "#game",
    EJS_core: "gba",
    EJS_gameUrl: romUrl,
    EJS_gameName: "Rematch",
    EJS_pathtodata: EMULATORJS,
    EJS_startOnLoaded: true,
    EJS_color: "#5b4fa3",
    EJS_disableLocalStorage: true,
    EJS_disableDatabases: true, // no caching the core (or anything) in the browser's IndexedDB
    EJS_disableAutoLang: false, // (sic: false = don't fetch a translation of the emulator's menus by browser locale)
    // one night, one run: no save states, no save files, no cheats
    EJS_Buttons: {
      saveState: false, loadState: false, quickSave: false, quickLoad: false,
      saveSavFiles: false, loadSavFiles: false, cheat: false, screenRecord: false,
    },
    // Same keys as mGBA desktop (also printed under the game). Libretro ids: 0 B, 2 SELECT, 3 START,
    // 4-7 D-pad, 8 A, 10 L, 11 R; 27 is EmulatorJS's fast-forward. Leaves out its 1/2/3 save-state hotkeys.
    EJS_defaultControls: {
      0: {
        0: { value: "z", value2: "BUTTON_2" }, 2: { value: "backspace", value2: "SELECT" },
        3: { value: "enter", value2: "START" }, 4: { value: "up arrow", value2: "DPAD_UP" },
        5: { value: "down arrow", value2: "DPAD_DOWN" }, 6: { value: "left arrow", value2: "DPAD_LEFT" },
        7: { value: "right arrow", value2: "DPAD_RIGHT" }, 8: { value: "x", value2: "BUTTON_1" },
        10: { value: "a", value2: "LEFT_TOP_SHOULDER" }, 11: { value: "s", value2: "RIGHT_TOP_SHOULDER" },
        27: { value: "tab" }, // hold to fast-forward, like mGBA
      },
      1: {}, 2: {}, 3: {},
    },
    EJS_defaultOptions: { "ff-ratio": "2.0" }, // mGBA's fast-forward speed
    EJS_onGameStart: () => watchForTheEnd(manifest),
  });
  // EmulatorJS keeps the game's battery save in an IndexedDB database ("/data/saves") no matter what.
  // Clear it before every boot, so each visit really starts fresh (one night, no saves).
  await clearEmulatorSaves();
  const s = document.createElement("script");
  s.src = EMULATORJS + "loader.js";
  document.body.appendChild(s);
}

function clearEmulatorSaves() {
  return new Promise((resolve) => {
    try {
      const req = indexedDB.deleteDatabase("/data/saves");
      req.onsuccess = req.onerror = req.onblocked = () => resolve();
    } catch { resolve(); }
  });
}

function warnBeforeLeaving(e) {
  e.stopImmediatePropagation(); // keep EmulatorJS from shutting the game down before the player answers
  e.preventDefault();
  e.returnValue = "";
}

// The game writes a marker to a known RAM address when it reaches THE END (rom-manifest.json).
// EmulatorJS has no documented way to read memory, so this is best effort; the button is the fallback.
function watchForTheEnd(manifest) {
  $("finished").hidden = false;
  const read = makeMarkerReader(manifest);
  if (!read) return;
  const timer = setInterval(() => {
    let v; try { v = read(); } catch { return; }
    // "THE END" is on screen: let it sit a moment, then the closing message
    if (v === manifest.endMarker.values.theEnd) { clearInterval(timer); setTimeout(() => theEnd(true), 3000); }
  }, 1000);
}

// How: EmulatorJS can hand us a save state (gameManager.getState). It's a RetroArch "RASTATE" file whose
// "MEM " chunk is mGBA's own snapshot, which keeps the GBA's 256 KiB work RAM (EWRAM, 0x02000000) at
// offset 0x21000 (mgba include/mgba/internal/gba/serialize.h). Checked against the game's symbol map.
const MGBA_EWRAM_OFFSET = 0x21000;
const EWRAM_BASE = 0x02000000;

function makeMarkerReader(manifest) {
  const gm = window.EJS_emulator && window.EJS_emulator.gameManager;
  if (!gm || typeof gm.getState !== "function") return null;
  const ewramOffset = parseInt(manifest.endMarker.address, 16) - EWRAM_BASE;
  return () => {
    const st = gm.getState();
    const dv = new DataView(st.buffer, st.byteOffset, st.byteLength);
    let o = 8; // after "RASTATE\x01"
    while (o + 8 <= st.length) {
      const id = String.fromCharCode(st[o], st[o + 1], st[o + 2], st[o + 3]);
      const size = dv.getUint32(o + 4, true);
      if (id === "MEM ") {
        const mem = o + 8;
        if ((dv.getUint32(mem, true) >>> 24) !== 0x01) return undefined; // not an mGBA GBA snapshot
        return dv.getUint32(mem + MGBA_EWRAM_OFFSET + ewramOffset, true);
      }
      if (id === "END ") break;
      o = (o + 8 + size + 7) & ~7;
    }
    return undefined;
  };
}

// reachedTheEnd: the game itself got there. It then holds on THE END (block flag) and keeps the music
// going, so the emulator keeps running, just out of sight. From the fallback button, it's paused instead.
function theEnd(reachedTheEnd) {
  window.removeEventListener("beforeunload", warnBeforeLeaving, { capture: true });
  if (reachedTheEnd !== true) {
    try { window.EJS_emulator && window.EJS_emulator.pause && window.EJS_emulator.pause(); } catch {}
  }
  $("closing-text").textContent = CLOSING_MESSAGE;
  show("closing");
}

// The message to the creator. POST /api/messages: locally tools/serve-web.py appends it to a file;
// once deployed, the AWS backend stores it.
const MESSAGE_MAX = 2000;
async function sendNote(e) {
  e.preventDefault();
  const text = $("note").value.trim();
  $("note-error").textContent = "";
  if (!text) { $("note-error").textContent = "Write a few words first."; return; }
  const a = window.rematchAnswers || {};
  $("note-send").disabled = true;
  $("note-send").textContent = "SENDING…";
  try {
    const r = await postJson("api/messages", {
      message: text.slice(0, MESSAGE_MAX),
      trainerName: a.playerName, rivalName: a.rivalName, yearPlayed: a.yearPlayed,
    });
    if (!r.ok) throw new Error("HTTP " + r.status);
    showThanks();
  } catch (err) {
    console.error(err);
    $("note-error").textContent = "Couldn't send it just now. Your words are still here: try again in a moment.";
    $("note-send").disabled = false;
    $("note-send").textContent = "LEAVE YOUR WORDS";
  }
}

function shareUrl() {
  return location.origin + location.pathname; // without dev query strings like ?rom=test
}

function showThanks() {
  $("thanks-name").textContent = (window.rematchAnswers || {}).playerName || "friend";
  $("note-form").hidden = true;
  $("note-thanks").hidden = false;
  $("share-url").value = shareUrl();
  if (navigator.share) $("share-native").hidden = false;
}

$("share-copy").addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(shareUrl());
  } catch {
    $("share-url").select(); document.execCommand("copy"); // older browsers
  }
  $("share-done").textContent = "Link copied.";
});
$("share-native").addEventListener("click", () => {
  navigator.share({ title: "Rematch", text: "One more time, back to Kanto.", url: shareUrl() }).catch(() => {});
});
$("note-form").addEventListener("submit", sendNote);

$("finished").addEventListener("click", theEnd);
$("form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const { answers, problems } = readAnswers(e.target);
  $("error").textContent = problems.join(" ");
  if (problems.length) return;
  $("start").disabled = true;
  $("start").textContent = "LOADING…";
  try {
    await start(answers);
  } catch (err) {
    console.error(err);
    window.removeEventListener("beforeunload", warnBeforeLeaving, { capture: true });
    if (!$("gate").hidden) { $("code-error").textContent = err.message; }
    else { show("intro"); $("error").textContent = "Couldn't load the game. " + err.message; }
    $("start").disabled = false;
    $("start").textContent = "START";
  }
});

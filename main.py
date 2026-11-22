# news-image-20261122 -- one 1024x1024 image summing up the world news of
# Sunday 22 November 2026: 48 sourced stories across 7 regions, 3 lead
# stories, a UTC timeline, a numbers band and a date check.
#
# Pure Python 3 standard library only: a hand-typed 5x7 pixel font and a
# small PNG encoder written here. No fonts, no images, no network, no clock,
# no randomness -- two runs write byte-identical files.
#
# Run:  mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
BG      = (13, 21, 38)     # deep navy page
PANEL   = (16, 29, 51)     # panel navy
PANEL2  = (21, 36, 63)     # lighter panel
GOLD    = (245, 184, 29)   # lead gold
WHITE   = (242, 245, 249)
MUTED   = (159, 176, 199)
FAINT   = (120, 136, 160)
RED     = (235, 87, 87)
GREEN   = (86, 204, 132)
BLUE    = (96, 165, 250)
ORANGE  = (251, 146, 60)
PURPLE  = (192, 132, 252)
TEAL    = (45, 212, 191)
PINK    = (244, 114, 182)

REGION_COLORS = {
    "NORTH AMERICA": BLUE,
    "LATIN AMERICA": GREEN,
    "EUROPE": GOLD,
    "AFRICA": ORANGE,
    "MIDDLE EAST": RED,
    "ASIA-PACIFIC": TEAL,
    "GLOBAL": PURPLE,
}

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 pixels, '#' = on, '.' = off.
FONT = {
    "A": ("..#..", ".#.#.", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", ".#.#.", "..#..", "..#..", "..#..", ".#.#.", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "/": ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "%": ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"),
    "&": (".##..", "#..#.", "#..#.", ".#...", "#.#.#", "#..#.", ".##.#"),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    "$": ("..#..", ".####", "#.#.#", ".###.", "..#.#", "####.", "..#.."),
    "*": (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    "#": (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
    "_": (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
}

# ---------------------------------------------------------------- canvas
px = bytearray(W * H * 3)


def fill_rect(x, y, w, h, color):
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(W, x + w)
    y1 = min(H, y + h)
    r, g, b = color
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        for xx in range(x0, x1):
            i = base + (xx - x0) * 3
            px[i] = r
            px[i + 1] = g
            px[i + 2] = b


def set_px(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        px[i], px[i + 1], px[i + 2] = color


def draw_text(x, y, text, color, scale=1):
    """Uppercase-only 5x7 font. Returns width drawn."""
    cx = x
    for ch in text.upper():
        glyph = FONT.get(ch, FONT[" "])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == "#":
                    if scale == 1:
                        set_px(cx + col, y + row, color)
                    else:
                        fill_rect(cx + col * scale, y + row * scale,
                                  scale, scale, color)
        cx += 6 * scale
    return cx - x


def text_w(text, scale=1):
    return len(text) * 6 * scale - scale


def wrap(text, max_chars):
    words = text.split(" ")
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if len(trial) <= max_chars:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- data
# (region, headline, source, confidence) -- confidence HIGH: wire service or
# major outlet (AP, AFP, Reuters, NYT, CNN, WSJ, BBC); MED: any other outlet.
STORIES = [
    ("NORTH AMERICA",
     "US flights resume after FAA ground stop of 4+ hours, longest since 9/11; router upgrade blamed",
     "AP", "HIGH"),
    ("NORTH AMERICA",
     "Microsoft 365 fully restored Saturday after global Outlook and Teams outage",
     "AP", "HIGH"),
    ("NORTH AMERICA",
     "Trump warns US firms building AI data centres abroad face a tremendous tax",
     "REUTERS", "HIGH"),
    ("NORTH AMERICA",
     "Trump calls Putin a friend; Zelensky calls Putin a killer as peace row deepens",
     "BBC", "HIGH"),
    ("NORTH AMERICA",
     "Court approves $7.25bn Bayer Roundup payout over cancer claims",
     "REUTERS", "HIGH"),
    ("NORTH AMERICA",
     "Palisades fire: man convicted of starting one of California's deadliest blazes",
     "BBC", "HIGH"),
    ("NORTH AMERICA",
     "Mamdani reveals plan to close New York's Rikers Island jail",
     "BBC", "MED"),
    ("LATIN AMERICA",
     "Chapo Isidro, FBI top-ten cartel kingpin, captured in Mexico army raid",
     "NYPOST", "HIGH"),
    ("LATIN AMERICA",
     "Cartel gunfight in Guasave forces baseball game cancelled; helicopters fire on gang",
     "AP", "HIGH"),
    ("LATIN AMERICA",
     "Peru M6.9 quake shakes Andes, felt in Lima; no casualties reported",
     "AP", "HIGH"),
    ("LATIN AMERICA",
     "Landslides and rockfalls reported on Andean slopes after Peru quake",
     "SPIEGEL", "MED"),
    ("LATIN AMERICA",
     "Flash flooding traps drivers in northwest Puerto Rico",
     "NWS", "MED"),
    ("EUROPE",
     "COP31 in overtime in Antalya; draft drops fossil fuels; EU: good deal or no deal",
     "REUTERS", "HIGH"),
    ("EUROPE",
     "Denmark accuses Russia of plot to kill rapper Kyivstoner; expels defence attache",
     "WSJ", "HIGH"),
    ("EUROPE",
     "Estonia to shut all road borders with Russia from Dec 1 after GRU arson claim",
     "REUTERS", "HIGH"),
    ("EUROPE",
     "Poland: Russian missiles landed on its soil; Tusk calls it intentional provocation",
     "AP", "HIGH"),
    ("EUROPE",
     "Russia fired 400 drones and 110+ missiles at Ukraine over Crimea bridge strikes",
     "AP", "HIGH"),
    ("EUROPE",
     "Zelensky: Crimea bridge strikes a fair response",
     "BBC", "HIGH"),
    ("EUROPE",
     "UK-EU reset: Miliband says deal not tied to tuition fees",
     "BBC", "HIGH"),
    ("EUROPE",
     "Leeds beat Chelsea 4-1, first win at Stamford Bridge since 1999",
     "BBC", "HIGH"),
    ("EUROPE",
     "Spitting Image co-creator Peter Fluck dies aged 85",
     "BBC", "HIGH"),
    ("EUROPE",
     "Trafalgar Square Christmas tree sets off from Oslo to London",
     "BBC", "MED"),
    ("AFRICA",
     "Kenyan firms lose email and meetings in global Microsoft outage",
     "NATION", "MED"),
    ("AFRICA",
     "South Africa: hung councils race to form coalitions as 14-day deadline lands",
     "IEC", "MED"),
    ("AFRICA",
     "ANC at 30.8% in local polls, worst result since 1994; DA leads five metros",
     "IEC", "MED"),
    ("AFRICA",
     "MK Party tops eThekwini with 38% in Durban, knocking ANC off top spot",
     "IEC", "MED"),
    ("AFRICA",
     "COP32 to be held in Addis Ababa, Ethiopia, in November 2027",
     "AP", "HIGH"),
    ("MIDDLE EAST",
     "Gulf on edge as US and Iran trade tit-for-tat strikes",
     "AP", "HIGH"),
    ("MIDDLE EAST",
     "Mideast nations race to avert all-out war as Israel urges Iran strikes",
     "AP", "HIGH"),
    ("MIDDLE EAST",
     "Saudi defences intercept two Houthi cruise missiles aimed at Riyadh",
     "AP", "HIGH"),
    ("MIDDLE EAST",
     "Bahrain intercepts Iranian attacks; sirens sound as 5th Fleet on alert",
     "AP", "HIGH"),
    ("MIDDLE EAST",
     "Kuwait air base hit 30+ times in war; 15 hangars damaged or destroyed",
     "AP", "HIGH"),
    ("MIDDLE EAST",
     "Qatar mediation on Iran diplomacy stalls despite intensified efforts",
     "AP", "MED"),
    ("ASIA-PACIFIC",
     "Modi opens Nitish Setu, 9.76km Ganga bridge; projects worth Rs34,470 crore",
     "ZEE", "MED"),
    ("ASIA-PACIFIC",
     "Cyclone Akvan: 370,000 moved to safety; landfall near Gopalpur",
     "JAGRAN", "MED"),
    ("ASIA-PACIFIC",
     "Japanese forces to use Indian facilities for live-fire training, a first",
     "JAGRAN", "MED"),
    ("ASIA-PACIFIC",
     "Nepal PM Balendra Shah to meet Modi on first bilateral visit",
     "BBC", "MED"),
    ("ASIA-PACIFIC",
     "Leapmotor Q3 profit plunges 73% despite record global deliveries",
     "BIZBUZZ", "MED"),
    ("ASIA-PACIFIC",
     "Foreign investment in China tech rises 31%",
     "BIZBUZZ", "MED"),
    ("ASIA-PACIFIC",
     "BYD and Huawei unveil new SUVs; BYD foldable wheel stows in 10 seconds",
     "BIZBUZZ", "MED"),
    ("ASIA-PACIFIC",
     "Australia breaks England's seven-match T20 streak",
     "SBS", "MED"),
    ("ASIA-PACIFIC",
     "Pat Cummins keeps Cricket Australia backing as Test captain",
     "JAGRAN", "MED"),
    ("GLOBAL",
     "GTA VI: $3.79bn day-one sales, biggest entertainment launch ever",
     "CNN", "HIGH"),
    ("GLOBAL",
     "Tech rout: Nasdaq -5.28% in a week; Nvidia -14%; Anthropic -9% after IPO",
     "WSJ", "HIGH"),
    ("GLOBAL",
     "UN Geneva: AI killer-robot talks extended two years, no binding rules",
     "AP", "HIGH"),
    ("GLOBAL",
     "October 2026 was 1.8C warmer than the mid-1800s",
     "BERKELEY", "MED"),
    ("GLOBAL",
     "Earth gains a temporary mini-moon",
     "NASA", "MED"),
    ("GLOBAL",
     "Lauren Price becomes undisputed welterweight champion",
     "BBC", "HIGH"),
]

LEADS = [
    ("1  COP31 ON THE BRINK", "Climate talks in overtime in Antalya: draft drops fossil fuels, EU warns good deal or no deal. REUTERS"),
    ("2  CHAPO ISIDRO CAUGHT", "FBI top-ten cartel kingpin captured in Mexico raid as gunfight erupts in Guasave. NYPOST"),
    ("3  GTA VI: $3.79BN IN A DAY", "Biggest entertainment launch ever: 32.5m pre-orders, 99 on Metacritic. CNN"),
]

TIMELINE = [
    ("FRI 20 NOV 19:09 LIMA", "Peru M6.9 quake shakes Andes"),
    ("FRI 21 NOV 15:54 ET", "FAA orders nationwide ground stop"),
    ("SAT 21 NOV 08:13 IST", "Modi opens Nitish Setu bridge"),
    ("SAT 21 NOV 14:00 ANTALYA", "COP31 stretches into overtime"),
    ("SAT 21 NOV 20:00 MEXICO", "Chapo Isidro capture announced"),
]

NUMBERS = [
    ("48", "STORIES"),
    ("7", "REGIONS"),
    ("$3.79BN", "GTA VI DAY ONE"),
    ("M6.9", "PERU QUAKE"),
    ("400+", "DRONES AT UKRAINE"),
    ("$7.25BN", "BAYER PAYOUT"),
    ("32.5M", "GTA PRE-ORDERS"),
    ("52%", "SA TURNOUT"),
]

# ---------------------------------------------------------------- layout
def draw_header():
    fill_rect(0, 0, W, 104, PANEL)
    fill_rect(0, 104, W, 4, GOLD)
    draw_text(16, 14, "WORLD NEWS", GOLD, scale=3)
    draw_text(16, 50, "SUNDAY 22 NOVEMBER 2026", WHITE, scale=2)
    draw_text(16, 78, "48 SOURCED STORIES  -  7 REGIONS  -  EVERY STORY MARKED WITH SOURCE AND CONFIDENCE",
              MUTED, scale=1)
    # date-check box, right side
    fill_rect(724, 14, 284, 76, PANEL2)
    draw_text(736, 22, "DATE CHECK", GOLD, scale=1)
    draw_text(736, 36, "SUNDAY 22 NOV 2026", WHITE, scale=1)
    draw_text(736, 50, "DAY 326 OF 2026 - 39 DAYS LEFT", WHITE, scale=1)
    draw_text(736, 64, "EVENTS OF 20-22 NOV, REPORTED 22 NOV", FAINT, scale=1)


def draw_leads():
    y = 116
    draw_text(16, y, "THE DAY IN THREE STORIES", GOLD, scale=1)
    y += 18
    col_w = 328
    for i, (title, body) in enumerate(LEADS):
        x = 16 + i * (col_w + 8)
        fill_rect(x, y, col_w, 62, PANEL2)
        fill_rect(x, y, 4, 62, GOLD)
        draw_text(x + 12, y + 8, title, GOLD, scale=1)
        for j, line in enumerate(wrap(body, 52)):
            draw_text(x + 12, y + 22 + j * 10, line, WHITE, scale=1)
    return y + 62


def draw_stories(top):
    left_regions = ["NORTH AMERICA", "LATIN AMERICA", "EUROPE"]
    right_regions = ["AFRICA", "MIDDLE EAST", "ASIA-PACIFIC", "GLOBAL"]
    col_x = [16, 524]
    col_w = 484
    max_chars = 78
    bottoms = []
    for ci, regions in enumerate((left_regions, right_regions)):
        x = col_x[ci]
        y = top
        for region in regions:
            color = REGION_COLORS[region]
            count = sum(1 for s in STORIES if s[0] == region)
            fill_rect(x, y, col_w, 16, PANEL)
            fill_rect(x, y, 4, 16, color)
            draw_text(x + 10, y + 4, "%s  (%d)" % (region, count), color, scale=1)
            y += 18
            for (reg, headline, source, conf) in STORIES:
                if reg != region:
                    continue
                tag = " [%s - %s]" % (source, conf[0])
                lines = wrap(headline, max_chars)
                lines = lines[:2]
                if len(lines) == 2:
                    # squeeze the source tag onto line 2 when it fits
                    room = max_chars - len(lines[1])
                    if len(tag) <= room:
                        lines[1] = lines[1] + tag
                    else:
                        lines[1] = lines[1][: max_chars - len(tag)] + tag
                else:
                    lines.append("%s - %s" % (source, conf))
                draw_text(x + 2, y, lines[0], WHITE, scale=1)
                if len(lines) > 1:
                    draw_text(x + 2, y + 10, lines[1], MUTED, scale=1)
                y += 21
            y += 2
        bottoms.append(y)
    return max(bottoms)


def draw_timeline(top):
    y = top + 6
    fill_rect(0, y, W, 4, GOLD)
    y += 12
    draw_text(16, y, "UTC TIMELINE  -  20-22 NOVEMBER 2026", GOLD, scale=1)
    y += 18
    col_w = 200
    for i, (when, what) in enumerate(TIMELINE):
        x = 16 + i * (col_w + 4)
        draw_text(x, y, when, WHITE, scale=1)
        for j, line in enumerate(wrap(what, 30)):
            draw_text(x, y + 10 + j * 10, line, MUTED, scale=1)
    return y + 30


def draw_numbers(top):
    y = top + 4
    fill_rect(16, y, 992, 46, PANEL2)
    x = 28
    for value, label in NUMBERS:
        draw_text(x, y + 6, value, GOLD, scale=2)
        draw_text(x, y + 28, label, MUTED, scale=1)
        x += max(text_w(value, 2), text_w(label, 1)) + 30
    return y + 46


def draw_footer(top):
    y = top + 6
    draw_text(16, y, "SOURCES: AP, AFP, REUTERS, NYT, CNN, WSJ, BBC, NYPOST, ZEE, SBS, NATION, IEC, NASA, BERKELEY EARTH",
              FAINT, scale=1)
    draw_text(16, y + 11,
              "CONFIDENCE: HIGH = WIRE SERVICE OR MAJOR OUTLET. MED = OTHER OUTLET. NUMBERS AS REPORTED 22 NOV 2026.",
              FAINT, scale=1)
    draw_text(16, y + 22, "PROGRAM-GENERATED IMAGE  -  NO PHOTOS  -  NEWS-IMAGE-20261122  -  MAKE.FUN",
              GOLD, scale=1)


# ---------------------------------------------------------------- PNG
def chunk(typ, data):
    out = struct.pack(">I", len(data)) + typ + data
    out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
    return out


def encode_png():
    raw = bytearray()
    for yy in range(H):
        raw.append(0)  # filter: none
        raw += px[yy * W * 3:(yy + 1) * W * 3]
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    data = b"\x89PNG\r\n\x1a\n"
    data += chunk(b"IHDR", ihdr)
    data += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    data += chunk(b"IEND", b"")
    return data


def main():
    fill_rect(0, 0, W, H, BG)
    draw_header()
    y = draw_leads()
    y = draw_stories(y + 8)
    y = draw_timeline(y)
    y = draw_numbers(y)
    draw_footer(y)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(encode_png())
    print("wrote %s (%dx%d)" % (path, W, H))


if __name__ == "__main__":
    main()

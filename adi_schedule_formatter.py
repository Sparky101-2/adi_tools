#!/usr/bin/env python3
"""
schedule_formatter.py
=====================

Formats a list of dates and times according to the agreed spec, which is
reproduced in full below. The code that follows implements it section by
section.

=========================================================================
BUSINESS RULES / SPECIFICATION
=========================================================================

PURPOSE
This tool operates in three modes depending on the format of the input:

  MODE 1 – SCHEDULE FORMATTER
  When given a list of dates and times, format them into a clean,
  fixed-width layout ready to paste into WhatsApp or SMS.
  Note: the use of triple-backticks (```) is to preserve formatting
  when copying and pasting into a Whatsapp message.

  MODE 2 – PRACTICAL TEST DATE MODE
  Start your input with "TD DDMM" (e.g. TD 0408) to calculate the list of
  dates 12, 10, 8, 6 and 4 weeks before a practical test date. Useful to
  setup a future-reminder for yourself to keep in touch with students at
  these times (in case you think there is a risk that they may not be test
  ready you may want to offer more lessons...) Any lines after the first
  are ignored.

  MODE 3 – FILE INPUT
  Instead of typing or pasting input directly, reference a UTF-8 text file
  using TXT_INPUT, or open it for editing first using TXT_EDIT. See the
  INPUT OPTIONS section for full syntax and default-path rules.
  Arrow-key shortcuts at the input prompt: ↑ TXT_INPUT  ↓ TXT_EDIT
  Native only (Windows/Mac/Linux) - unavailable on web. See ENVIRONMENT
  DETECTION.

  MISC FEATURES (interactive mode only)
  - VER         Display the current git version of this script.
                Native only - see ENVIRONMENT DETECTION below.

==============================
ENVIRONMENT DETECTION (WEB VS NATIVE)
==============================
This tool can run two ways: natively (Windows/Mac/Linux, launched from a
terminal) or in a browser via Pyodide (e.g. hosted on GitHub Pages). The
web build has no real filesystem and cannot spawn subprocesses (Notepad,
git), so file-based and subprocess-based features must be disabled there.

DETECTION
- Web (Pyodide) is detected via sys.platform == "emscripten".
- Everywhere else (Windows, Mac, Linux) is treated as "native" and keeps
  every feature exactly as documented elsewhere in this spec.

FEATURES DISABLED ON WEB
- MODE 3 - FILE INPUT (TXT_INPUT, TXT_EDIT) - no filesystem to read from,
  write to, or open Notepad against.
- VER - requires a subprocess call to git against the local repo checkout.
- The up/down arrow-key shortcuts (these already only apply to native
  Windows interactive mode).

BEHAVIOUR ON WEB
- The startup banner omits any mention of the above features entirely -
  it must never advertise a command the user cannot use.
- If a disabled command is entered anyway (typed literally, regardless of
  whether the banner mentioned it), it is recognised and rejected with a
  short message explaining it isn't available in this environment. It is
  never passed through to the schedule parser as literal text.
- Everything else (Mode 1, Mode 2, ASC/DESC, all shorthand rules) behaves
  identically on web and native.

ON A NEW CHAT (startup message)
- At the very top of your first reply in any new chat, before anything
  else, output a banner with: an Executive Summary, all three modes, a
  MISC FEATURES section, the Time Markup KEY, and the worked examples for
  both modes. On web, omit Mode 3 and MISC FEATURES per ENVIRONMENT
  DETECTION above.
- Then carry on and handle whatever I've actually asked in that first
  message.

==============================
EXECUTIVE SUMMARY / WHAT THIS TOOL DOES
==============================

Type shorthand date/time input to instantly produce clean, fixed-width
output ready to paste into WhatsApp or SMS — saving time, keeping things
consistent, and always looking professional to your clients.

The default lesson duration is two hours, so you only need to enter a
start time — the system will automatically calculate and append the end
time.

  Input:  3112 10
  Output: Thurs 31/12 1000–1200

Alternatively, specify the end time explicitly:

  Input:  3112 10-1130
  Output: Thurs 31/12 1000–1130

For more usage examples, see the example inputs and outputs below. Three
modes cover schedule formatting (Mode 1), test-date countdowns (Mode 2),
and file-based batch input (Mode 3).

==============================
MODE 1 – SCHEDULE FORMATTER
==============================

ASSUMPTIONS
1. Every entry begins with a date, always followed by at least one time
   slot. A slot may be a start-end range or a single start time
   (expanded to 2 hours per Assumption 9).
   Reason: the first item on a line is then unambiguously the date and
   everything after it is times, removing the collision between a 4-digit
   date (0406) and a 4-digit time (0406).
2. A date written without a slash is always 4 digits in DDMM order
   (day first, then month), never DMM.
   Reason: fixes a single day-then-month convention and requires
   zero-padding, so there's no order ambiguity.
3. No list ever spans more than 6 months.
   Reason: each date can be read as its next occurrence from today,
   making year assignment - and sorting across a December/January
   boundary - unambiguous.
4. My working day is 0800-2000.
   Reason: it serves as both the validity bound (every time must fall
   inside it) and the window for resolving shorthand 12-hour times. At
   12 hours wide it's narrow enough that only one of a shorthand time's
   two readings ever falls inside, so disambiguation is always clean -
   even for 1-hour ranges.
5. A full stop is only ever a within-range separator, equivalent to a
   hyphen (6.8 = 6-8).
   Reason: it is never a decimal or a sentence end, so it always reads
   as the divider between a range's start and end.
6. Commas are only ever used to separate one time range from the next.
   Reason: a single explicit slot delimiter, so nothing relies on spaces
   to tell where one range ends and the next begins.
7. When I mark a time slot with * or #, the marker is always flush
   against the time with no space. A marker at either end of a range,
   or both ends, means the same thing - apply that marker once and strip
   it before parsing the time. Mixing * and # on the same range is
   invalid.
   - * marks other available lesson times.
   - # marks previously booked lessons.
   - No marker means a new lesson booking.
   Reason: removes any doubt about which range the marker applies to and
   gives each range an unambiguous category.
8. A non-hour time may be written either with a colon (14:30) or as a
   4-digit HHMM value (1430); both mean thirty minutes past two. A
   colon, when present, is always a hours-minutes separator and never a
   range or slot delimiter. A value with no colon and fewer than 3
   digits is on the hour.
   Reason: 4-digit HHMM is unambiguous in the time position because
   Assumption 1 guarantees the first token is the date and everything
   after it is times - so a 4-digit token can never be confused with a
   date. Allowing both forms accepts the most natural shorthand.
9. The default slot duration is 2 hours.
   Reason: specifying only a start time is the common case; a fixed
   2-hour default removes the need to repeat the end when it follows
   mechanically. AM/PM resolution and working-day validation apply to
   the computed end time just as they do to an explicit end.

OUTPUT FORMAT (Mode 1)
- Output is grouped into up to three sections; a section is shown only
  if that marker type appears in the input:
    1. No-marker slots  -> "Here is the new lesson booking."          (1 slot)
                          "Here are the new lesson bookings."         (2+ slots)
    2. * slots          -> "Here is another lesson time that is available."      (1 slot)
                          "Here are some other lesson times that are available." (2+ slots)
    3. # slots          -> "For reference, the following lesson is already booked."  (1 slot)
                          "For reference, the following lessons are already booked." (2+ slots)
  The section header uses singular or plural grammar depending on how many
  slots appear in that section.
  Within each section, slots are sorted chronologically. Default sort
  order is ascending (ASC) unless I say DESC; ASC/DESC applies within
  each section independently. Each section's slot lines are wrapped in a
  triple-backtick code fence (one fence line before and one after the
  block, for monospace rendering in WhatsApp/Markdown). Sections sit
  directly adjacent: the closing fence of one is immediately followed by
  the next section's header, with no blank line between them.
- Date format: DDD DD/MM - e.g. Thurs 01/12 for 1st December.
  Day abbreviations: Mon, Tues, Wed, Thurs, Fri, Sat, Sun.
- Pad each day abbreviation with trailing spaces so they are all the
  same width (the width of the longest, "Thurs" = 5 characters), so the
  date and time columns align vertically in Courier/monospace.
- Times in 24-hour format, no colon - e.g. 1000 for 10am, 2200 for 10pm.
  An input colon time is converted to this form (14:30 becomes 1430).
- Ranges are written start-end, e.g. 0900-1100.
- No per-line suffix is appended; the section header identifies the
  meaning of each group.

READING MY INPUT (Mode 1)
- The first item on a line is the date; everything after it is times.
- Time ranges on a line are separated by commas; each comma-separated
  range is its own slot, output on its own line with the date repeated.
- A line may contain ** anywhere (typically at the end) to apply the *
  marker to all times on that line — shorthand for marking every
  comma-separated slot with * individually.
- A range's start and end may be divided by a hyphen or a full stop -
  both mean the same thing (9-11 and 9.11 are identical).
- A time with minutes may be written as H:MM (14:30) or as a 4-digit
  HHMM value (1430); both mean half past two. A time with no colon and
  fewer than 3 digits is on the hour. All times are output in 4-digit
  no-colon form (14:30 or 1430 -> 1430).
- Dates may be written with or without a slash (see Assumption 2).
- Validate: day 01-31, month 01-12.
- Read each date as its next occurrence on or after today (Assumption 3).
- A slot may be given as a single time with no end (e.g. "9", "14:30").
  It is expanded to a 2-hour range starting at that time (Assumption 9).
  AM/PM resolution and working-day validation apply to the computed end.

WEBSITE BOOKING EXPORT FORMAT (Mode 1)
- Lines copied directly from the online booking website are accepted
  as-is and may be freely mixed with standard shorthand lines in the
  same input block. The website produces tab-separated lines in this
  structure:
    DD/MM/YYYY  [*|#]HH:MM[*|#]  HH:MM  [name]  [postcode]  [status] ...
  Column 1: date in DD/MM/YYYY format. Unlike shorthand dates, the year
    is explicit and significant - it is used exactly as given and is
    never re-resolved to a "next occurrence" (Assumption 3 does not
    apply here, since there is no ambiguity to resolve). This is what
    keeps a mix of past, present, and future export rows - e.g. old
    "Delivered" lessons alongside upcoming "Instructor confirmed" ones -
    sorted in true chronological order instead of being pulled into the
    wrong year.
  Column 2: start time in HH:MM format, optionally prefixed or suffixed
    with a * or # marker (e.g. "08:00#" or "#09:00"). The marker is
    extracted and applied to the resulting slot exactly as in the
    standard shorthand format.
  Column 3: end time in HH:MM format, no marker expected.
  Columns 4+: customer name, postcode, confirmation status, and any
    other website fields — all silently ignored.
- The * and # markers carry the same meanings as in the standard format:
    # = previously booked lesson
    * = other available lesson times
- Detection: a line is treated as a website export line when it is
  tab-separated, its first field matches DD/MM/YYYY, and its second and
  third fields are valid HH:MM time tokens. Any line that does not match
  this pattern is parsed under the existing shorthand rules.

RESOLVING AM/PM
- For an ambiguous 12-hour range like 11-1 (or 11.1), resolve each end
  against my working day 0800-2000 (Assumption 4): pick the 24-hour
  value that falls within it and keep the end later than the start. So
  11-1 = 1100-1300, 2-4 = 1400-1600, 9-5 = 0900-1700, 6-8 = 1800-2000.
- This applies to the hour part of colon times too: 2:30-4 = 1430-1600.
  Minutes are preserved. Times already in unambiguous 24-hour form are
  left as-is.
- After resolving, check every time falls within 0800-2000. Anything
  outside it goes in Notes, not silently dropped or guessed.

MARKERS
- Markers are placed flush against the start or end of a range (or both
  ends - placing a marker at either end means the same thing). Strip the
  marker before parsing the time. Mixing * and # on the same range is
  not valid.
- * means "other available lesson times".
- # means "previously booked lesson".
- No marker means "new lesson booking".

LINE-LEVEL * SHORTHAND
- Adding ** anywhere on a line applies the * marker to every time slot
  on that line. This is equivalent to placing * on every comma-separated
  time individually, but requires less typing when all times on a line
  share the same * status.
- ** is stripped from the line before parsing, so it may appear at any
  position (start, end, or middle of the time portion).
- Typically used at the end of the line (e.g. "0306 9, 11, 1430 **"),
  but any position on the line is valid.
- If a line contains ** and individual per-slot markers are also present,
  ** takes precedence: all slots on the line are treated as *.

TIME MARKUP KEY
Always print this key in the startup banner:

TIME MARKUP KEY
[No markup] - new lesson booking
     *      - other available lesson times
     **     - line-level shorthand: applies * to every time on the line
     #      - previously booked lesson

INTERACTIVE SESSION
- After every response — whether a formatted schedule, a VER display,
  a TXT_INPUT result, or a TXT_EDIT session — the program immediately
  returns to the input prompt. No restart is needed.
  The startup banner is shown once only, at the start of the session.
- To exit, submit an empty input (press the EOF key with no text entered).
- On web, VER, TXT_INPUT and TXT_EDIT are not available; entering one is
  rejected with a short message instead of being run or parsed as
  schedule text (see ENVIRONMENT DETECTION).

INPUT OPTIONS (native only - see ENVIRONMENT DETECTION)
- In interactive mode, instead of typing or pasting input directly,
  you may reference a UTF-8 text file using the TXT_INPUT keyword:
    TXT_INPUT "C:\\path\\to\\your\\input.txt"
  Quotes around the path are optional but recommended when the path
  contains spaces. The file's contents are processed exactly as if
  you had typed them.
- If no path is given (i.e. just "TXT_INPUT" with nothing after it),
  the default path TXT_INPUT_DEFAULT_PATH is used. This constant is
  defined near the top of the file so it can be updated easily.
- To open the input file in Notepad for editing, use TXT_EDIT (path
  syntax and default-path rules are identical to TXT_INPUT):
    TXT_EDIT "C:\\path\\to\\your\\input.txt"
  The program opens Notepad and waits for it to close, then returns
  to the prompt. Press ↑ + Enter to run TXT_INPUT afterwards.
  When the default path is used and the target directory or file does
  not yet exist, both are created automatically before Notepad opens.
- VER, TXT_INPUT and TXT_EDIT are single-line commands that submit on
  pressing Enter alone — no Ctrl+Z required. After executing, the
  program immediately returns to the input prompt.
- Arrow-key shortcuts (Windows interactive mode only):
  At the input prompt, press ↑ to fill the line with TXT_INPUT or
  ↓ to fill it with TXT_EDIT. Press Enter to run, or keep typing to
  edit the command (e.g. to supply a different path). Shortcuts only
  act before any regular character has been typed. Pressing the same
  arrow key again clears the line back to empty.

AMBIGUITY / NOTES
- Always produce the standard formatted output first.
- If anything was ambiguous, invalid, or required a judgement call (an
  out-of-range date, a time outside 0800-2000, a missing comma between
  ranges, or anything otherwise unclear), do NOT interrupt the standard
  block. Instead, add a short "Notes:" section beneath it listing each
  issue, the entry it relates to, and what you did or what you need from
  me to resolve it.

EXAMPLE (Mode 1)
EXAMPLE INPUT:
0206 9#
0306 9, 1430
0406 6-8, 9-1030*
0506 9#

EXAMPLE OUTPUT:
Here are the new lesson bookings.
```
Wed   03/06 0900–1100
Wed   03/06 1430–1630
Thurs 04/06 1800–2000
```
Here is another lesson time that is available.
```
Thurs 04/06 0900–1030
```
For reference, the following lessons are already booked.
```
Tues  02/06 0900–1100
Fri   05/06 0900–1100
```

==============================
MODE 2 – PRACTICAL TEST DATE MODE
==============================

INPUT FORMAT
- A single line starting with "TD " (case-insensitive) followed by a date
  in DDMM or DD/MM format. Any lines after the first are ignored.

OUTPUT FORMAT (Mode 2)
- Displays the dates 12, 10, 8, 6 and 4 weeks before the test date,
  followed by a blank line, then the test date itself.
- The test date is resolved to its next occurrence on or after today
  (same rule as Assumption 3). Lead-up dates are plain arithmetic
  subtractions from the resolved test date and may fall in the past.
- Date format: DDD DD/MM (day abbreviation unpadded, no trailing spaces).
  Day abbreviations: Mon, Tues, Wed, Thurs, Fri, Sat, Sun.

EXAMPLE (Mode 2)
EXAMPLE INPUT:
TD 0408

EXAMPLE OUTPUT:
12 weeks before: Tues 12/05
10 weeks before: Tues 26/05
8 weeks before: Tues 09/06
6 weeks before: Tues 23/06
4 weeks before: Tues 07/07

Test Date: Tues 04/08

=========================================================================
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import date, timedelta

# --------------------------------------------------------------------------- #
# Constants (Assumptions 4 and 9)
# --------------------------------------------------------------------------- #
WORK_START = 8 * 60        # 0800 in minutes since midnight
WORK_END = 20 * 60         # 2000 in minutes since midnight
DEFAULT_DURATION = 2 * 60  # 120 minutes applied when no end time is given

# Default file path used when TXT_INPUT is entered without a path argument.
# Update this constant to change the default location.
TXT_INPUT_DEFAULT_PATH = r"C:\temp\adi_schedule_formatter\adi_schedule_formatter_INPUT.txt"

# True when running under Pyodide in a browser (e.g. GitHub Pages), where
# there is no real filesystem and no ability to spawn subprocesses (git,
# Notepad). Gates any feature that depends on either (see ENVIRONMENT
# DETECTION in the spec above).
IS_WEB = sys.platform == "emscripten"

# weekday() returns Mon=0 .. Sun=6
DAY_ABBR = ["Mon", "Tues", "Wed", "Thurs", "Fri", "Sat", "Sun"]
PAD = max(len(a) for a in DAY_ABBR)   # 5, the width of "Thurs"

# Section headers for each marker type (singular and plural).
SECTION_NEW   = "Here are the new lesson bookings."
SECTION_NEW_S = "Here is the new lesson booking."
SECTION_STAR   = "Here are some other lesson times that are available."
SECTION_STAR_S = "Here is another lesson time that is available."
SECTION_HASH   = "For reference, the following lessons are already booked."
SECTION_HASH_S = "For reference, the following lesson is already booked."

EXAMPLE_INPUT = "0206 9#\n0306 9, 1430\n0406 6-8, 9-1030*\n0506 9#"
EXAMPLE_OUTPUT = (
    "Here are the new lesson bookings.\n"
    "```\n"
    "Wed   03/06 0900–1100\n"
    "Wed   03/06 1430–1630\n"
    "Thurs 04/06 1800–2000\n"
    "```\n"
    "Here is another lesson time that is available.\n"
    "```\n"
    "Thurs 04/06 0900–1030\n"
    "```\n"
    "For reference, the following lessons are already booked.\n"
    "```\n"
    "Tues  02/06 0900–1100\n"
    "Fri   05/06 0900–1100\n"
    "```"
)

# Regression test: website-export rows spanning past ("Delivered") and
# future ("Instructor confirmed") dates must sort in true chronological
# order using the literal year given, not get bumped to a "next
# occurrence" year once today has passed them (see bug report: past
# rows were pulled into next year and sorted after the future ones).
WEBSITE_EXPORT_REGRESSION_INPUT = (
    "31/05/2026\t11:00\t13:00\tSherlock Holmes\t221B Baker Street, NW1 1AA\tDelivered\n"
    "07/06/2026\t11:00\t13:00\tSherlock Holmes\t221B Baker Street, NW1 1AA\tDelivered\n"
    "14/06/2026\t11:00\t13:00\tSherlock Holmes\t221B Baker Street, NW1 1AA\tDelivered\n"
    "21/06/2026\t11:00\t13:00\tSherlock Holmes\t221B Baker Street, NW1 1AA\tDelivered\n"
    "28/06/2026\t11:00\t13:00\tSherlock Holmes\t221B Baker Street, NW1 1AA\tDelivered\n"
    "05/07/2026\t11:00\t13:00\tSherlock Holmes\t221B Baker Street, NW1 1AA\tInstructor confirmed\n"
    "12/07/2026\t11:00\t13:00\tSherlock Holmes\t221B Baker Street, NW1 1AA\tInstructor confirmed\n"
    "19/07/2026\t11:00\t13:00\tSherlock Holmes\t221B Baker Street, NW1 1AA\tInstructor confirmed"
)
WEBSITE_EXPORT_REGRESSION_OUTPUT = (
    "Here are the new lesson bookings.\n"
    "```\n"
    "Sun   31/05 1100–1300\n"
    "Sun   07/06 1100–1300\n"
    "Sun   14/06 1100–1300\n"
    "Sun   21/06 1100–1300\n"
    "Sun   28/06 1100–1300\n"
    "Sun   05/07 1100–1300\n"
    "Sun   12/07 1100–1300\n"
    "Sun   19/07 1100–1300\n"
    "```"
)

TD_EXAMPLE_INPUT = "TD 0408"
TD_EXAMPLE_OUTPUT = (
    "12 weeks before: Tues 12/05\n"
    "10 weeks before: Tues 26/05\n"
    "8 weeks before: Tues 09/06\n"
    "6 weeks before: Tues 23/06\n"
    "4 weeks before: Tues 07/07\n"
    "\n"
    "Test Date: Tues 04/08"
)


# --------------------------------------------------------------------------- #
# Small helpers
# --------------------------------------------------------------------------- #
def to_hhmm(minutes: int) -> str:
    """Minutes-since-midnight -> 4-digit HHMM string (Output format)."""
    return f"{minutes // 60:02d}{minutes % 60:02d}"


def next_occurrence(day: int, month: int, today: date) -> date:
    """
    Assumption 3: read a date as its next occurrence on or after today.
    Tries this year then the next few (covers 29 Feb on a non-leap year).
    Raises ValueError if the day/month never form a real calendar date.
    """
    for year in (today.year, today.year + 1, today.year + 2, today.year + 3):
        try:
            candidate = date(year, month, day)
        except ValueError:
            continue
        if candidate >= today:
            return candidate
    raise ValueError(f"{day:02d}/{month:02d} is not a valid calendar date")


# --------------------------------------------------------------------------- #
# Test Date Mode
# --------------------------------------------------------------------------- #
def detect_td(text: str) -> tuple[int, int] | None:
    """
    If the first non-empty line of text starts with 'TD ' (case-insensitive)
    followed by a valid date, returns (day, month). Otherwise returns None.
    """
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if not stripped.upper().startswith("TD "):
            return None
        date_tok = stripped[3:].strip()
        try:
            day, month, _year = parse_date(date_tok)
            return day, month
        except ValueError:
            return None
    return None


def render_td(day: int, month: int, today: date | None = None) -> str:
    """
    Renders the test date countdown: 8, 6, 4 weeks before and the test date.
    Lead-up dates are simple arithmetic and may fall in the past.
    """
    today = today or date.today()
    test_date = next_occurrence(day, month, today)

    def fmt(d: date) -> str:
        return f"{DAY_ABBR[d.weekday()]} {d.day:02d}/{d.month:02d}"

    twelve = test_date - timedelta(weeks=12)
    ten    = test_date - timedelta(weeks=10)
    eight  = test_date - timedelta(weeks=8)
    six    = test_date - timedelta(weeks=6)
    four   = test_date - timedelta(weeks=4)

    return (
        f"12 weeks before: {fmt(twelve)}\n"
        f"10 weeks before: {fmt(ten)}\n"
        f"8 weeks before: {fmt(eight)}\n"
        f"6 weeks before: {fmt(six)}\n"
        f"4 weeks before: {fmt(four)}\n"
        f"\n"
        f"Test Date: {fmt(test_date)}"
    )


# --------------------------------------------------------------------------- #
# Parsing
# --------------------------------------------------------------------------- #
def parse_date(token: str) -> tuple[int, int, int | None]:
    """
    Reads a date token, returning (day, month, year).
    Accepts DD/MM (with slash), DDMM (Assumption 2: 4 digits, day first),
    or DD/MM/YYYY (website export format: an explicit, significant year).
    year is None for the year-less forms, signalling that the date should
    be resolved to its next occurrence on or after today (Assumption 3).
    """
    token = token.strip()
    if "/" in token:
        bits = token.split("/")
        if len(bits) == 2 and all(b.isdigit() for b in bits):
            day, month, year = int(bits[0]), int(bits[1]), None
        elif len(bits) == 3 and all(b.isdigit() for b in bits):
            day, month, year = int(bits[0]), int(bits[1]), int(bits[2])
        else:
            raise ValueError(f"unrecognised date '{token}'")
    elif token.isdigit() and len(token) == 4:
        day, month, year = int(token[:2]), int(token[2:]), None
    else:
        raise ValueError(f"unrecognised date '{token}' (use DDMM or DD/MM)")

    if not 1 <= month <= 12:
        raise ValueError(f"month {month:02d} is out of range in '{token}'")
    if not 1 <= day <= 31:
        raise ValueError(f"day {day:02d} is out of range in '{token}'")
    return day, month, year


def parse_endpoint(token: str) -> list[int]:
    """
    Turns one end of a range into a list of candidate values (minutes since
    midnight). A shorthand 12-hour value returns two candidates (AM and PM);
    an explicit value returns one. Raises ValueError on anything unparseable.

    Rules (Assumption 8: a colon means minutes; no colon means on the hour):
      - "H:MM"  colon time. H 1-11 is ambiguous; H 12 is noon/midnight;
                 H 0 or 13-23 is explicit 24-hour.
      - "9"/"11" 1-2 digits, value 1-11 -> ambiguous; 12 -> noon/midnight;
                 13-23 -> explicit 24-hour hour; 0 -> midnight.
      - "900"/"1800" 3-4 digits -> explicit 24-hour HHMM.
    """
    token = token.strip()

    if ":" in token:
        bits = token.split(":")
        if len(bits) != 2 or not all(b.isdigit() for b in bits):
            raise ValueError(f"unrecognised time '{token}'")
        h, m = int(bits[0]), int(bits[1])
        if not 0 <= m <= 59:
            raise ValueError(f"'{token}' has invalid minutes")
        if h == 12:
            return [720 + m, m]                        # noon or midnight
        if 1 <= h <= 11:
            return [h * 60 + m, (h + 12) * 60 + m]    # AM or PM
        if 0 <= h <= 23:
            return [h * 60 + m]                        # explicit 24-hour
        raise ValueError(f"'{token}' has an invalid hour")

    if not token.isdigit():
        raise ValueError(f"unrecognised time '{token}'")
    n = int(token)

    if len(token) <= 2:
        if n == 12:
            return [720, 0]                            # noon or midnight
        if 1 <= n <= 11:
            return [n * 60, (n + 12) * 60]             # AM or PM
        if 13 <= n <= 23:
            return [n * 60]                            # explicit 24-hour hour
        if n == 0:
            return [0]
        raise ValueError(f"'{token}' is not a valid hour")

    if len(token) in (3, 4):
        h, m = n // 100, n % 100
        if not (0 <= h <= 23 and 0 <= m <= 59):
            raise ValueError(f"'{token}' is not a valid 24-hour time")
        return [h * 60 + m]

    raise ValueError(f"unrecognised time '{token}'")


# --------------------------------------------------------------------------- #
# Range resolution (RESOLVING AM/PM)
# --------------------------------------------------------------------------- #
@dataclass
class Slot:
    start: int | None = None        # minutes since midnight
    end: int | None = None
    marker: str = ""                # "": new booking  "*": other available  "#": previously booked
    error: str | None = None        # fatal: nothing to output
    note: str | None = None         # non-fatal: output, but flag it


def resolve_range(chunk: str) -> Slot:
    """
    Resolves one comma-delimited range chunk into a Slot.

    Markers: * or # flush at either end (Assumption 7) indicate slot type
    and are stripped before parsing. Mixing * and # on the same range is
    invalid. Separators: start and end may be divided by '-' or '.'
    (Assumption 5).
    """
    stripped = chunk.strip()
    has_star = stripped.startswith("*") or stripped.endswith("*")
    has_hash = stripped.startswith("#") or stripped.endswith("#")

    if has_star and has_hash:
        return Slot(error=f"cannot mix * and # markers in '{chunk}'")

    marker = "*" if has_star else ("#" if has_hash else "")
    core = stripped.strip("*#").strip()

    parts = re.split(r"[-.]", core)

    if len(parts) == 1:
        # Single start time: apply default 2-hour duration (Assumption 9).
        try:
            starts = parse_endpoint(parts[0])
        except ValueError as exc:
            return Slot(marker=marker, error=str(exc))
        pairs = [(s, s + DEFAULT_DURATION) for s in starts]
    elif len(parts) == 2 and all(p.strip() for p in parts):
        try:
            starts = parse_endpoint(parts[0])
            ends = parse_endpoint(parts[1])
        except ValueError as exc:
            return Slot(marker=marker, error=str(exc))
        pairs = [(s, e) for s in starts for e in ends if e > s]
        if not pairs:
            return Slot(marker=marker, error="end time is not after start time")
    else:
        return Slot(marker=marker,
                    error=f"expected a start-end range or single start time, got '{chunk}'")

    # Prefer interpretations that sit entirely inside the working day.
    in_window = [
        (s, e) for (s, e) in pairs
        if WORK_START <= s <= WORK_END and WORK_START <= e <= WORK_END
    ]

    if len(in_window) == 1:
        s, e = in_window[0]
        return Slot(start=s, end=e, marker=marker)

    if len(in_window) > 1:
        # Should not happen with a 12-hour window, but flag rather than guess.
        s, e = in_window[0]
        options = ", ".join(f"{to_hhmm(a)}–{to_hhmm(b)}" for a, b in in_window)
        return Slot(start=s, end=e, marker=marker,
                    note=f"ambiguous; could be {options} - used {to_hhmm(s)}–{to_hhmm(e)}")

    # Nothing fits the working day: keep the earliest ascending reading, flag it.
    s, e = min(pairs, key=lambda p: p[0])
    return Slot(start=s, end=e, marker=marker,
                note="outside working day (0800-2000)")


# --------------------------------------------------------------------------- #
# Output formatting
# --------------------------------------------------------------------------- #
def format_line(when: date, slot: Slot) -> str:
    """Builds one padded output line (date + times, no suffix)."""
    abbr = DAY_ABBR[when.weekday()].ljust(PAD)
    times = f"{to_hhmm(slot.start)}–{to_hhmm(slot.end)}"
    return f"{abbr} {when.day:02d}/{when.month:02d} {times}"


# --------------------------------------------------------------------------- #
# Website export pre-processing
# --------------------------------------------------------------------------- #
def preprocess_website_line(line: str) -> str:
    """
    Detects a booking-website export line (tab-separated, DD/MM/YYYY date)
    and converts it to standard shorthand format for the existing parser.

    Input structure:  DD/MM/YYYY  [*|#]HH:MM[*|#]  HH:MM  [ignored...]
    Output:           DD/MM/YYYY START-END[marker]

    The year is preserved (not discarded) so the date resolves to the
    literal calendar date given, not to a "next occurrence" guess.

    Returns the original line unchanged if it does not match.
    """
    fields = [f.strip() for f in line.split("\t")]
    fields = [f for f in fields if f]
    if len(fields) < 3:
        return line

    date_field, start_field, end_field = fields[0], fields[1], fields[2]

    # Must have a DD/MM/YYYY date in the first column
    date_match = re.match(r"^\d{2}/\d{2}/\d{4}$", date_field)
    if not date_match:
        return line

    # Extract any marker from the start-time field
    marker = "#" if "#" in start_field else ("*" if "*" in start_field else "")
    start_clean = start_field.strip("#*")

    # Both start and end must look like time tokens (e.g. HH:MM)
    if not re.match(r"^\d+:\d+$", start_clean):
        return line
    if not re.match(r"^\d+:\d+$", end_field):
        return line

    return f"{date_field} {start_clean}-{end_field}{marker}"


# --------------------------------------------------------------------------- #
# Top-level processing
# --------------------------------------------------------------------------- #
def format_schedule(
    text: str,
    order: str = "asc",
    today: date | None = None,
) -> tuple[list[str], list[str], list[str], list[str]]:
    """
    Processes the whole input and returns (no_marker_lines, star_lines,
    hash_lines, notes). A bare line of 'ASC' or 'DESC' anywhere in the
    input sets the sort order (applied within each section independently).
    """
    today = today or date.today()
    no_marker_rows: list[tuple[date, int, str]] = []
    star_rows:      list[tuple[date, int, str]] = []
    hash_rows:      list[tuple[date, int, str]] = []
    notes: list[str] = []

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.upper() == "DESC":
            order = "desc"
            continue
        if line.upper() == "ASC":
            order = "asc"
            continue

        line = preprocess_website_line(line)

        # Line-level ** shorthand: applies * to every slot on this line.
        line_star = "**" in line
        if line_star:
            line = re.sub(r"\*\*", "", line)
            line = re.sub(r"  +", " ", line).strip()

        match = re.match(r"(\S+)\s+(.*)", line)
        if not match:
            notes.append(f"'{line}': a date needs at least one time range after it.")
            continue
        date_tok, rest = match.group(1), match.group(2)

        try:
            day, month, year = parse_date(date_tok)
            when = date(year, month, day) if year is not None else next_occurrence(day, month, today)
        except ValueError as exc:
            notes.append(f"'{line}': {exc}")
            continue

        chunks = [c.strip() for c in rest.split(",") if c.strip()]
        if not chunks:
            notes.append(f"{date_tok}: a date needs at least one time range.")
            continue

        for chunk in chunks:
            slot = resolve_range(chunk)
            if line_star:
                slot.marker = "*"
            if slot.error:
                notes.append(f"{date_tok} '{chunk}': {slot.error}")
                continue
            if slot.note:
                notes.append(f"{date_tok} '{chunk}': {slot.note}")
            row = (when, slot.start, format_line(when, slot))
            if slot.marker == "*":
                star_rows.append(row)
            elif slot.marker == "#":
                hash_rows.append(row)
            else:
                no_marker_rows.append(row)

    def sorted_lines(rows: list[tuple[date, int, str]]) -> list[str]:
        rows.sort(key=lambda r: (r[0], r[1]))
        if order == "desc":
            rows.reverse()
        return [r[2] for r in rows]

    return (
        sorted_lines(no_marker_rows),
        sorted_lines(star_rows),
        sorted_lines(hash_rows),
        notes,
    )


def render(text: str, order: str = "asc", today: date | None = None) -> str:
    """Formats input into grouped sections and appends Notes if anything was flagged."""
    no_marker, star_lines, hash_lines, notes = format_schedule(
        text, order=order, today=today
    )

    sections: list[str] = []
    if no_marker:
        h = SECTION_NEW_S if len(no_marker) == 1 else SECTION_NEW
        sections.append(f"{h}\n```\n" + "\n".join(no_marker) + "\n```")
    if star_lines:
        h = SECTION_STAR_S if len(star_lines) == 1 else SECTION_STAR
        sections.append(f"{h}\n```\n" + "\n".join(star_lines) + "\n```")
    if hash_lines:
        h = SECTION_HASH_S if len(hash_lines) == 1 else SECTION_HASH
        sections.append(f"{h}\n```\n" + "\n".join(hash_lines) + "\n```")

    out = "\n".join(sections)
    if notes:
        out += "\n\nNotes:\n" + "\n".join(f"- {n}" for n in notes)
    return out


def process_input(text: str, order: str = "asc", today: date | None = None) -> str:
    """
    Dispatches to TD mode or the schedule formatter depending on the first line.
    """
    td = detect_td(text)
    if td is not None:
        day, month = td
        return render_td(day, month, today=today)
    return render(text, order=order, today=today)


def startup_banner(web: bool = IS_WEB) -> str:
    """
    The startup message: both modes, file input option, key, and examples.
    On web (Pyodide), Mode 3 and MISC FEATURES are omitted entirely, since
    both depend on filesystem/subprocess access that isn't available there
    (see ENVIRONMENT DETECTION in the module spec).
    """
    rule = "=" * 66
    thin = "-" * 66

    mode3_and_misc = (
        f"  MODE 3 – FILE INPUT\n"
        f"  ===================\n"
        f"  Instead of typing input, reference a text file:\n"
        f"    TXT_INPUT \"C:\\path\\to\\your\\input.txt\"\n"
        f"  To open the file for editing first, use TXT_EDIT (same syntax).\n"
        f"  Omit the path to use the default file:\n"
        f"    {TXT_INPUT_DEFAULT_PATH}\n"
        f"  Arrow-key shortcuts at the input prompt:\n"
        f"    ↑ TXT_INPUT  ↓ TXT_EDIT\n"
        f"\n"
        f"  MISC FEATURES\n"
        f"  =============\n"
        f"  VER – Type VER at the prompt to display the current git version\n"
        f"        of this script.\n"
        f"\n"
    ) if not web else ""

    submitting_input_commands = (
        f"  Commands (VER, TXT_INPUT, TXT_EDIT): press Enter only — no\n"
        f"  Ctrl+Z needed. The program always returns to this prompt.\n"
    ) if not web else ""

    return (
        f"{rule}\n"
        f"  ADI SCHEDULE FORMATTER\n"
        f"{rule}\n"
        f"\n"
        f"  WHAT THIS TOOL DOES\n"
        f"  ===================\n"
        f"  Type shorthand date/time input to instantly produce clean,\n"
        f"  fixed-width output ready to paste into WhatsApp or SMS —\n"
        f"  saving time, keeping things consistent, and always looking\n"
        f"  professional to your clients.\n"
        f"\n"
        f"  The default lesson duration is two hours, so you only need\n"
        f"  to enter a start time — the system will automatically\n"
        f"  calculate and append the end time.\n"
        f"\n"
        f"    Input:  3112 10\n"
        f"    Output: Thurs 31/12 1000–1200\n"
        f"\n"
        f"  Alternatively, specify the end time explicitly:\n"
        f"\n"
        f"    Input:  3112 10-1130\n"
        f"    Output: Thurs 31/12 1000–1130\n"
        f"\n"
        f"  For more usage examples, see the example inputs and outputs\n"
        f"  below.\n"
        f"\n"
        f"  MODE 1 – SCHEDULE FORMATTER\n"
        f"  ===========================\n"
        f"  Enter lesson dates and times in shorthand format to produce a\n"
        f"  clean, fixed-width layout ready to paste into WhatsApp or SMS.\n"
        f"  Note: triple-backticks (```) preserve monospace formatting in\n"
        f"  WhatsApp.\n"
        f"\n"
        f"  MODE 2 – PRACTICAL TEST DATE MODE\n"
        f"  ==================================\n"
        f"  Start your input with \"TD DDMM\" (e.g. TD 0408) to calculate the\n"
        f"  list of dates 12, 10, 8, 6 and 4 weeks before a practical test\n"
        f"  date. Useful to setup a future-reminder for yourself to keep in\n"
        f"  touch with students at these times (in case you think there is a\n"
        f"  risk that they may not be test ready you may want to offer more\n"
        f"  lessons...)\n"
        f"\n"
        f"{mode3_and_misc}"
        f"{thin}\n"
        f"  TIME MARKUP KEY\n"
        f"  ---------------\n"
        f"  [No markup]  new lesson booking\n"
        f"       *       other available lesson times\n"
        f"       **      line-level: applies * to every time on the line\n"
        f"       #       previously booked lesson\n"
        f"\n"
        f"  SUBMITTING INPUT\n"
        f"  ----------------\n"
        f"  Multi-line schedule input: press Ctrl+Z then Enter (Windows)\n"
        f"  or Ctrl+D (Mac/Linux) to submit. Submit empty input to exit.\n"
        f"{submitting_input_commands}"
        f"\n"
        f"{rule}\n"
        f"  MODE 1 - SHORTHAND INPUT EXAMPLE\n"
        f"{rule}\n"
        f"INPUT:\n"
        f"{EXAMPLE_INPUT}\n"
        f"\n"
        f"OUTPUT:\n"
        f"{EXAMPLE_OUTPUT}\n"
        f"\n"
        f"{rule}\n"
        f"  MODE 2 - TEST DATE EXAMPLE\n"
        f"{rule}\n"
        f"INPUT:\n"
        f"{TD_EXAMPLE_INPUT}\n"
        f"\n"
        f"OUTPUT:\n"
        f"{TD_EXAMPLE_OUTPUT}"
    )


# --------------------------------------------------------------------------- #
# Self-test (verifies the program reproduces the spec example)
# --------------------------------------------------------------------------- #
def selftest() -> bool:
    fixed_today = date(2026, 5, 28)       # so 03/06 and 04/06 are this year
    produced = render(EXAMPLE_INPUT, today=fixed_today)
    ok = produced == EXAMPLE_OUTPUT
    print("SELF-TEST (Mode 1):", "PASS" if ok else "FAIL")
    if not ok:
        print("--- expected ---")
        print(EXAMPLE_OUTPUT)
        print("--- produced ---")
        print(produced)

    # Website-export regression: today falls between the past ("Delivered")
    # and future ("Instructor confirmed") rows, which is exactly the
    # condition that used to bump past rows into next year and break sort
    # order.
    web_today = date(2026, 7, 4)
    web_produced = render(WEBSITE_EXPORT_REGRESSION_INPUT, today=web_today)
    web_ok = web_produced == WEBSITE_EXPORT_REGRESSION_OUTPUT
    print("SELF-TEST (website export regression):", "PASS" if web_ok else "FAIL")
    if not web_ok:
        print("--- expected ---")
        print(WEBSITE_EXPORT_REGRESSION_OUTPUT)
        print("--- produced ---")
        print(web_produced)

    # TD self-test: test date 04/08/2026 from a fixed reference so dates are deterministic.
    td_today = date(2026, 6, 12)
    td_produced = render_td(4, 8, today=td_today)
    td_ok = td_produced == TD_EXAMPLE_OUTPUT
    print("SELF-TEST (Mode 2):", "PASS" if td_ok else "FAIL")
    if not td_ok:
        print("--- expected ---")
        print(TD_EXAMPLE_OUTPUT)
        print("--- produced ---")
        print(td_produced)

    return ok and web_ok and td_ok


# --------------------------------------------------------------------------- #
# Interactive input (used when no file and nothing is piped)
# --------------------------------------------------------------------------- #
def _is_single_line_cmd(line: str) -> bool:
    """True for commands that submit immediately on Enter (no Phase 2 / Ctrl+Z needed)."""
    upper = line.strip().upper()
    return (upper == "VER" or
            upper.startswith("TXT_INPUT") or
            upper.startswith("TXT_EDIT"))


def _win_read_with_shortcuts() -> str:
    """
    Windows-only interactive reader with ↑/↓ arrow-key shortcut support.

    Phase 1 – reads the first line char-by-char via msvcrt so arrow keys can
    be intercepted before any text is committed:
      ↑  fills the line with TXT_INPUT (pressing ↑ again clears it)
      ↓  fills the line with TXT_EDIT  (pressing ↓ again clears it)
    Pressing Enter on a shortcut returns it immediately (no Phase 2).
    Pressing Enter on normal typed text ends Phase 1 and starts Phase 2.
    Ctrl+Z alone signals EOF (empty return → exit).

    Phase 2 – reads additional lines via sys.stdin.readline() until EOF
    (Ctrl+Z then Enter on Windows).
    """
    import msvcrt

    PROMPT = "> "
    _ARROW: dict[str, str] = {"H": "TXT_INPUT", "P": "TXT_EDIT"}

    shortcut = ""
    buf: list[str] = []

    sys.stdout.write(PROMPT)
    sys.stdout.flush()

    def _redraw(new_text: str, prev_len: int) -> None:
        sys.stdout.write(
            "\r" + PROMPT + " " * prev_len + "\r" + PROMPT + new_text
        )
        sys.stdout.flush()

    first_line: str | None = None

    while first_line is None:
        ch = msvcrt.getwch()

        # ── special / arrow key ───────────────────────────────────────────────
        if ch in ("\xe0", "\x00"):
            ch2 = msvcrt.getwch()
            if not buf and ch2 in _ARROW:
                new = _ARROW[ch2] if _ARROW[ch2] != shortcut else ""
                prev_len = len(shortcut)
                shortcut = new
                _redraw(shortcut, prev_len)
            continue

        # ── Enter ─────────────────────────────────────────────────────────────
        if ch == "\r":
            sys.stdout.write("\n")
            sys.stdout.flush()
            if shortcut:
                return shortcut          # single-line shortcut; skip Phase 2
            first_line = "".join(buf)    # "" → exit; non-empty → Phase 2
            if first_line and _is_single_line_cmd(first_line):
                return first_line        # command: skip Phase 2
            break

        # ── Ctrl+Z (Windows EOF) ──────────────────────────────────────────────
        if ch == "\x1a":
            sys.stdout.write("\n")
            sys.stdout.flush()
            return "".join(buf)          # "" if nothing typed → exit signal

        # ── Ctrl+C ────────────────────────────────────────────────────────────
        if ch == "\x03":
            raise KeyboardInterrupt

        # ── Backspace ─────────────────────────────────────────────────────────
        if ch == "\x08":
            if buf:
                buf.pop()
                sys.stdout.write("\b \b")
                sys.stdout.flush()
            elif shortcut:
                prev_len = len(shortcut)
                shortcut = ""
                _redraw("", prev_len)
            continue

        # ── Regular character ─────────────────────────────────────────────────
        if shortcut:
            prev_len = len(shortcut)
            buf = list(shortcut)
            shortcut = ""
            buf.append(ch)
            _redraw("".join(buf), prev_len)
        else:
            buf.append(ch)
            sys.stdout.write(ch)
            sys.stdout.flush()

    # ── Phase 2: collect additional lines until EOF ───────────────────────────
    if not first_line:
        return ""

    lines = [first_line]
    while True:
        line = sys.stdin.readline()
        if not line:                     # Ctrl+Z+Enter → EOF
            break
        lines.append(line.rstrip("\r\n"))

    text = "\n".join(lines)
    line_count = text.count("\n") + 1 if text else 0
    print(f"\nGot {len(text)} characters across {line_count} lines.")
    return text


def read_interactive_input() -> str:
    """
    Prompt the user to paste/type their dates and read until EOF.
    On Windows, ↑ pre-fills TXT_INPUT and ↓ pre-fills TXT_EDIT at the prompt.
    """
    eof_keys = "Ctrl+Z then Enter" if os.name == "nt" else "Ctrl+D"
    print()
    print(f"Input ({eof_keys} to submit):")
    if os.name == "nt":
        return _win_read_with_shortcuts()
    text = sys.stdin.read()
    line_count = text.count("\n") + 1 if text else 0
    print(f"\nGot {len(text)} characters across {line_count} lines.")
    return text


# --------------------------------------------------------------------------- #
# File-input helpers (TXT_INPUT / TXT_EDIT)
# --------------------------------------------------------------------------- #
def handle_txt_input(directive: str) -> str | None:
    """
    Parses a TXT_INPUT directive and returns the file contents, or None on error.
    Syntax: TXT_INPUT "path"  or  TXT_INPUT path
    """
    rest = directive[9:].strip()   # strip "TXT_INPUT" prefix
    if (rest.startswith('"') and rest.endswith('"')) or \
       (rest.startswith("'") and rest.endswith("'")):
        rest = rest[1:-1]
    if not rest:
        rest = TXT_INPUT_DEFAULT_PATH
        print(f"[No path given — using default: {rest}]")
    try:
        with open(rest, encoding="utf-8") as fh:
            content = fh.read()
        print(f"[Read {len(content)} character(s) from: {rest}]")
        return content
    except FileNotFoundError:
        print(f"Error: file not found: {rest}")
        return None
    except OSError as exc:
        print(f"Error reading file: {exc}")
        return None


def handle_txt_edit(directive: str) -> None:
    """
    Opens the given file in Notepad for editing and waits until it closes.
    Syntax mirrors TXT_INPUT: optional quoted or unquoted path; omit path to
    use TXT_INPUT_DEFAULT_PATH. Returns None; caller should re-prompt.
    """
    rest = directive[8:].strip()   # strip "TXT_EDIT" prefix
    if (rest.startswith('"') and rest.endswith('"')) or \
       (rest.startswith("'") and rest.endswith("'")):
        rest = rest[1:-1]
    if not rest:
        rest = TXT_INPUT_DEFAULT_PATH
        print(f"[No path given — using default: {rest}]")
        dirpath = os.path.dirname(rest)
        os.makedirs(dirpath, exist_ok=True)
        if not os.path.isfile(rest):
            with open(rest, "w", encoding="utf-8"):
                pass
            print(f"[Created: {rest}]")
    print(f"[Opening for editing: {rest}]")
    try:
        subprocess.run(["notepad", rest], check=False)
        print("[Editor closed. Press ↑ + Enter to run TXT_INPUT.]")
    except OSError as exc:
        print(f"Error opening Notepad: {exc}")


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Format a list of dates and times per the agreed spec.")
    parser.add_argument("file", nargs="?",
                        help="input file; if omitted, reads stdin")
    parser.add_argument("--desc", action="store_true",
                        help="sort descending (default ascending)")
    parser.add_argument("--no-banner", action="store_true",
                        help="suppress the startup greeting/example")
    parser.add_argument("--selftest", action="store_true",
                        help="check the program against the spec example")
    args = parser.parse_args(argv)

    if args.selftest:
        return 0 if selftest() else 1

    if not args.no_banner:
        print(startup_banner())

    order = "desc" if args.desc else "asc"

    if args.file:
        with open(args.file, "r", encoding="utf-8") as fh:
            text = fh.read()
        if not args.no_banner:
            print("\n---\n")
        print(process_input(text, order=order))
    elif not sys.stdin.isatty():
        text = sys.stdin.read()
        if not args.no_banner:
            print("\n---\n")
        print(process_input(text, order=order))
    else:
        if not args.no_banner:
            print("\n---\n")
        while True:
            text = read_interactive_input()
            if not text.strip():
                print("Exiting.")
                break
            if IS_WEB and _is_single_line_cmd(text):
                print("That command isn't available in this web version "
                      "(no local file or git access here).")
                continue
            if text.strip().upper() == "VER":
                try:
                    _repo = os.path.dirname(os.path.abspath(__file__))
                    _count = subprocess.run(
                        ["git", "rev-list", "--count", "HEAD"],
                        capture_output=True, text=True, check=False, cwd=_repo,
                    ).stdout.strip()
                    _hash = subprocess.run(
                        ["git", "rev-parse", "--short", "HEAD"],
                        capture_output=True, text=True, check=False, cwd=_repo,
                    ).stdout.strip()
                    _dirty = subprocess.run(
                        ["git", "status", "--porcelain"],
                        capture_output=True, text=True, check=False, cwd=_repo,
                    ).stdout.strip()
                    ver = f"r{_count} ({_hash})" + ("-dirty" if _dirty else "")
                except FileNotFoundError:
                    ver = "git not found"
                print(f"Version: {ver}")
                continue
            if text.strip().upper().startswith("TXT_EDIT"):
                handle_txt_edit(text.strip())
                continue
            if text.strip().upper().startswith("TXT_INPUT"):
                text = handle_txt_input(text.strip())
                if text is None:
                    continue
                if not text.strip():
                    print("File is empty, skipping.")
                    continue
            print(process_input(text, order=order))
            print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

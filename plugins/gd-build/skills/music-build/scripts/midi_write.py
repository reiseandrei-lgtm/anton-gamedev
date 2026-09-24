#!/usr/bin/env python3
"""Cue в JSON → Standard MIDI File type 1 (Python stdlib): общий .mid и по файлу на стем.

Использование:
  python3 midi_write.py design/audio/music/<cue>.json <out-dir> [--stems]
Формат cue (подробно — references/music-method.md §2):
  {"cue": "run_main", "bpm": 90, "meter": "4/4", "bars": 8, "key": "D major",
   "tracks": [{"name": "pad", "program": 89, "channel": 0, "volume": 100, "repeat_bars": 2,
               "notes": [[0, 4, 62, 70], [0, 4, 66, 64]]}]}
  notes: [начало в долях (четвертях) от начала паттерна, длительность в долях, MIDI-нота, velocity].
  repeat_bars — паттерн повторяется каждые N тактов до конца cue. channel 9 — ударные (GM).
PPQ 480; End of Track ровно в конце последнего такта — длина cue = bars тактов без хвоста.
"""
import argparse
import json
import os
import struct
import sys

PPQ = 480


def vlq(n):
    out = [n & 0x7F]
    n >>= 7
    while n:
        out.insert(0, (n & 0x7F) | 0x80)
        n >>= 7
    return bytes(out)


def chunk(events):
    """events: [(tick, bytes)] → MTrk с дельта-временем; сортировка: note off раньше note on в том же тике."""
    events = sorted(events, key=lambda e: (e[0], 0 if (e[1][0] & 0xF0) == 0x80 else 1))
    data, last = b"", 0
    for tick, msg in events:
        data += vlq(tick - last) + msg
        last = tick
    return b"MTrk" + struct.pack(">I", len(data)) + data


def beats_per_bar(meter):
    num, den = (int(x) for x in str(meter).split("/"))
    return num * 4 / den


def tempo_track(cue, end):
    num, den = (int(x) for x in str(cue.get("meter", "4/4")).split("/"))
    us = int(round(60_000_000 / float(cue["bpm"])))
    ev = [(0, b"\xff\x51\x03" + us.to_bytes(3, "big")),
          (0, bytes([0xFF, 0x58, 0x04, num, den.bit_length() - 1, 24, 8])),
          (end, b"\xff\x2f\x00")]
    name = cue.get("cue", "cue").encode("utf-8")[:120]
    ev.insert(0, (0, b"\xff\x03" + vlq(len(name)) + name))
    return chunk(ev)


def note_track(tr, bar_beats, bars, end):
    ch = int(tr.get("channel", 0)) & 0x0F
    name = tr.get("name", "track").encode("utf-8")[:120]
    ev = [(0, b"\xff\x03" + vlq(len(name)) + name),
          (0, bytes([0xB0 | ch, 7, int(tr.get("volume", 100)) & 0x7F]))]
    if ch != 9:
        ev.append((0, bytes([0xC0 | ch, int(tr.get("program", 0)) & 0x7F])))
    rep = int(tr.get("repeat_bars", 0)) or bars
    for offset_bar in range(0, bars, rep):
        base = offset_bar * bar_beats
        for start, dur, pitch, vel in tr["notes"]:
            on = int(round((base + start) * PPQ))
            off = min(int(round((base + start + dur) * PPQ)), end)
            if on >= end:
                continue
            ev.append((on, bytes([0x90 | ch, int(pitch) & 0x7F, int(vel) & 0x7F])))
            ev.append((off, bytes([0x80 | ch, int(pitch) & 0x7F, 0])))
    ev.append((end, b"\xff\x2f\x00"))
    return chunk(ev)


def write_smf(path, tracks_bytes):
    with open(path, "wb") as f:
        f.write(b"MThd" + struct.pack(">IHHH", 6, 1, len(tracks_bytes), PPQ) + b"".join(tracks_bytes))


def main():
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser()
    ap.add_argument("cue")
    ap.add_argument("out")
    ap.add_argument("--stems", action="store_true")
    a = ap.parse_args()
    with open(a.cue, encoding="utf-8") as f:
        cue = json.load(f)
    bar_beats = beats_per_bar(cue.get("meter", "4/4"))
    bars = int(cue["bars"])
    end = int(round(bars * bar_beats * PPQ))
    name = cue.get("cue") or os.path.splitext(os.path.basename(a.cue))[0]
    os.makedirs(a.out, exist_ok=True)
    tempo = tempo_track(cue, end)
    full = os.path.join(a.out, f"{name}.mid")
    write_smf(full, [tempo] + [note_track(t, bar_beats, bars, end) for t in cue["tracks"]])
    print(f"{os.path.abspath(full)}: {len(cue['tracks'])} дорожек · {bars} тактов {cue.get('meter', '4/4')} · {cue['bpm']} BPM")
    if a.stems:
        for t in cue["tracks"]:
            p = os.path.join(a.out, f"{name}_{t.get('name', 'track')}.mid")
            write_smf(p, [tempo, note_track(t, bar_beats, bars, end)])
            print(f"{os.path.abspath(p)}: стем {t.get('name')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

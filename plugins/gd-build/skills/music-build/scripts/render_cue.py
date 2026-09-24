#!/usr/bin/env python3
"""Рендер стемов cue через FluidSynth с точной длиной петли (Python stdlib + внешний fluidsynth).

Использование:
  python3 render_cue.py design/audio/music/<cue>.json <mid-dir> <out-dir> [--sr 48000] [--gain 0.6]
                        [--soundfont <file.sf2>] [--fluidsynth <exe>] [--no-fold] [--lufs -16 --ceiling -1]
Берёт <mid-dir>/<cue>_<track>.mid (из midi_write.py --stems), рендерит каждый в WAV 16 бит стерео, затем:
  длина = round(sr × 60 / bpm × долей в такте × bars) сэмплов (кратно такту);
  хвост после конца петли (ревёрб, отзвук) складывается в начало (--no-fold — просто обрезается; для стингеров).
Выход: <out-dir>/<cue>_<track>.wav. SoundFont: --soundfont, SOUNDFONT или поиск preflight.py.
FluidSynth (LGPL-2.1) вызывается как внешняя программа.
"""
import argparse
import json
import math
import os
import struct
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "slice-build" / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "sfx-design" / "scripts"))
import loudness  # noqa: E402
import preflight  # noqa: E402
from midi_write import beats_per_bar  # noqa: E402


def main():
    preflight.utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("cue")
    ap.add_argument("mid_dir")
    ap.add_argument("out")
    ap.add_argument("--sr", type=int, default=48000)
    ap.add_argument("--gain", type=float, default=0.6)
    ap.add_argument("--soundfont", default=None)
    ap.add_argument("--fluidsynth", default=None)
    ap.add_argument("--no-fold", action="store_true")
    ap.add_argument("--lufs", type=float, default=None, help="цель громкости суммы стемов (одно усиление на все)")
    ap.add_argument("--ceiling", type=float, default=-1.0, help="потолок sample peak суммы, dBFS")
    a = ap.parse_args()

    fs = a.fluidsynth or os.environ.get("FLUIDSYNTH") or preflight.find_tool("fluidsynth")
    sf = a.soundfont or preflight.find_soundfont()
    if not fs or not sf:
        print(f"Нет {'fluidsynth' if not fs else 'SoundFont'} — режим plan (см. preflight.py --for music)")
        return 2
    with open(a.cue, encoding="utf-8") as f:
        cue = json.load(f)
    name = cue.get("cue") or Path(a.cue).stem
    loop = int(round(a.sr * 60 / float(cue["bpm"]) * beats_per_bar(cue.get("meter", "4/4")) * int(cue["bars"])))
    os.makedirs(a.out, exist_ok=True)
    print(f"cue {name}: {cue['bpm']} BPM · {cue.get('meter', '4/4')} · {cue['bars']} тактов → {loop} сэмплов "
          f"({loop / a.sr:.3f} s) · SoundFont {Path(sf).name}")
    rendered = []
    for t in cue["tracks"]:
        mid = Path(a.mid_dir) / f"{name}_{t.get('name', 'track')}.mid"
        if not mid.is_file():
            print(f"нет {mid} — сначала midi_write.py --stems")
            return 2
        with tempfile.TemporaryDirectory() as tmp:
            raw = Path(tmp) / "raw.wav"
            subprocess.run([str(fs), "-ni", "-q", "-g", str(a.gain), "-r", str(a.sr), "-O", "s16", "-F", str(raw),
                            str(sf), str(mid)], check=True, capture_output=True)
            with wave.open(str(raw), "rb") as w:
                ch, n = w.getnchannels(), w.getnframes()
                frames = list(struct.unpack(f"<{n * ch}h", w.readframes(n)))
        need = loop * ch
        body = frames[:need] + [0] * max(0, need - len(frames))
        tail = frames[need:]
        if not a.no_fold:
            for i, v in enumerate(tail[:need]):
                body[i] += v
        rendered.append((t.get("name", "track"), ch, body, len(tail) // ch))

    gain = 1.0
    if a.lufs is not None and rendered:
        ch = rendered[0][1]
        mix = [[0.0] * loop for _ in range(ch)]
        for _, c, body, _ in rendered:
            if c == ch:
                for k in range(ch):
                    src, dst = body[k::ch], mix[k]
                    for i, v in enumerate(src):
                        dst[i] += v / 32768
        lufs, _ = loudness.integrated(mix, a.sr)
        peak = max((abs(v) for c in mix for v in c), default=0.0)
        if lufs > -100:
            gain = 10 ** ((a.lufs - lufs) / 20)
            if peak * gain > 10 ** (a.ceiling / 20):
                gain = 10 ** (a.ceiling / 20) / peak
        print(f"сумма стемов {lufs:.1f} LUFS → усиление {20 * math.log10(gain):+.1f} dB (цель {a.lufs:g}, потолок {a.ceiling:g} dBFS)")
    for stem, ch, body, tail in rendered:
        body = [max(-32768, min(32767, int(round(v * gain)))) for v in body]
        out = Path(a.out) / f"{name}_{stem}.wav"
        with wave.open(str(out), "wb") as w:
            w.setnchannels(ch)
            w.setsampwidth(2)
            w.setframerate(a.sr)
            w.writeframes(struct.pack(f"<{len(body)}h", *body))
        m = loudness.measure(out)
        print(f"{out.resolve()}: {m['frames']} сэмплов · хвост {tail} {'сложен в начало' if not a.no_fold else 'обрезан'}"
              f" · {m['lufs']:.1f} LUFS · peak {m['peak_db']:.1f} dBFS")
    return 0


if __name__ == "__main__":
    sys.exit(main())

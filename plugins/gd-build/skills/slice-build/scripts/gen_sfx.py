#!/usr/bin/env python3
"""Плейсхолдерные SFX синтезом — только Python stdlib, без ключей и сервисов.

Адаптировано из unity-kit scripts/gen-sfx.py (MIT © 2026 Benjamin Curlier), см. ATTRIBUTION.md.
Изменения: выбор звуков по имени, новые рецепты (land, confirm, fail, whoosh), имя файла с префиксом.

Использование:
  python3 gen_sfx.py <out-dir> [имя ...] [--prefix ph_] [--list]
  python3 gen_sfx.py Assets/_Project/Audio/Placeholder jump land coin
Без имён — все рецепты. WAV 44.1 кГц, 16 бит, моно, пик 0.85.
Плейсхолдер отличим от финала: файлы получают префикс (по умолчанию `ph_`).
"""
import argparse
import math
import os
import random
import struct
import sys
import wave

SR = 44100


def square(phase):
    return 1.0 if (phase % 1.0) < 0.5 else -1.0


def sweep(f0, f1, dur, decay, wave_fn=square):
    out, phase = [], 0.0
    for i in range(int(SR * dur)):
        t = i / SR
        phase += f0 * (f1 / f0) ** (t / dur) / SR
        out.append(wave_fn(phase) * math.exp(-t * decay))
    return out


def noise(dur, decay, seed, darken=60):
    rng = random.Random(seed)
    raw = [rng.uniform(-1, 1) for _ in range(int(SR * dur))]
    out, window = [], []
    for i, s in enumerate(raw):
        t = i / SR
        k = 1 + int(2 + t * darken)
        window.append(s)
        if len(window) > k:
            window = window[-k:]
        out.append(sum(window) / len(window) * math.exp(-t * decay))
    return out


def jump():
    return sweep(220, 880, 0.3, 6)


def land():
    thump = sweep(160, 60, 0.12, 30, lambda p: math.sin(2 * math.pi * p))
    return [a + 0.4 * b for a, b in zip(thump, noise(0.12, 40, 3, 20))]


def coin():
    out, phase = [], 0.0
    for i in range(int(SR * 0.35)):
        t = i / SR
        phase += (987.77 if t < 0.08 else 1318.51) / SR
        out.append(square(phase) * (1.0 if t < 0.08 else math.exp(-(t - 0.08) * 14)))
    return out


def hurt():
    out, phase, dur = [], 0.0, 0.22
    for i in range(int(SR * dur)):
        t = i / SR
        phase += 400 * (90 / 400) ** (t / dur) / SR
        out.append(square(phase) * (1.0 - (t / dur) ** 2))
    return out


def fail():
    out = []
    for f in (392.0, 329.63, 261.63):  # G4 → E4 → C4, нисходящее «не вышло»
        out += sweep(f, f * 0.97, 0.18, 5)
    return out


def confirm():
    return sweep(660, 660, 0.06, 20) + sweep(990, 990, 0.12, 18)


def ui_click():
    rng = random.Random(7)
    out, phase = [], 0.0
    for i in range(int(SR * 0.06)):
        t = i / SR
        phase += 2200 / SR
        out.append((math.sin(2 * math.pi * phase) * 0.7 + rng.uniform(-1, 1) * 0.3) * math.exp(-t * 90))
    return out


def whoosh():
    base = noise(0.4, 0, 11, 30)
    return [s * math.sin(math.pi * i / len(base)) for i, s in enumerate(base)]


def laser():
    return sweep(1800, 300, 0.25, 10)


def explosion():
    return noise(0.9, 5, 42)


RECIPES = {f.__name__: f for f in (jump, land, coin, hurt, fail, confirm, ui_click, whoosh, laser, explosion)}


def write_wav(path, samples):
    peak = max(1e-9, max(abs(s) for s in samples))
    norm = 0.85 / peak
    with wave.open(path, "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(b"".join(struct.pack("<h", int(max(-1.0, min(1.0, s * norm)) * 32767)) for s in samples))


def main():
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?")
    ap.add_argument("names", nargs="*")
    ap.add_argument("--prefix", default="ph_")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    if a.list or not a.out:
        print("Рецепты: " + ", ".join(RECIPES))
        return 0 if a.list else 2
    unknown = [n for n in a.names if n not in RECIPES]
    if unknown:
        print(f"Неизвестные рецепты: {', '.join(unknown)}. Есть: {', '.join(RECIPES)}")
        return 2
    os.makedirs(a.out, exist_ok=True)
    for name in a.names or RECIPES:
        path = os.path.join(a.out, f"{a.prefix}{name}.wav")
        write_wav(path, RECIPES[name]())
        with wave.open(path) as w:
            print(f"{os.path.abspath(path)}: {w.getnframes() / SR:.2f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())

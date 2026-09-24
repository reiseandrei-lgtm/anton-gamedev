#!/usr/bin/env python3
"""Синтез SFX по рецепту из слоёв с вариациями и seed — Python stdlib, детерминированно.

Использование:
  python3 synth_sfx.py <recipes.json> <out-dir> [имя ...] [--variations N] [--seed S] [--sr 48000]
                       [--lufs -20] [--ceiling -1] [--prefix ""] [--list]
Рецепт (формат и пример — references/sfx-method.md §2, references/recipes-example.json):
  {"land": {"dur": 0.35, "layers": [
      {"wave": "sine", "f0": 160, "f1": 55, "attack": 0.002, "decay": 18, "gain": 1.0},   # тело
      {"wave": "noise", "start": 0, "dur": 0.08, "decay": 45, "lowpass": 2500, "gain": 0.5}  # транзиент
   ], "vary": {"cents": 80, "gain_db": 1.5, "start_ms": 6}}}
wave: sine | square | saw | triangle | noise. f1 — экспоненциальный свип f0 → f1 за длительность слоя.
Огибающая: линейная атака `attack` (с), затем exp(−decay·t); `release` (с) — линейный спад в конце слоя.
Фильтры одного полюса: `lowpass`, `highpass` (Гц). Вариация i использует Random(seed·1000 + i).
Выход: <prefix><имя>_<NN>.wav (N > 1) или <prefix><имя>.wav; 16 бит, моно. Громкость: нормализация к --lufs
(BS.1770, loudness.py), затем потолок sample peak --ceiling dBFS (true peak проверяй ffmpeg).
"""
import argparse
import json
import math
import os
import random
import struct
import sys
import wave

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import loudness  # noqa: E402

WAVES = {
    "sine": lambda p: math.sin(2 * math.pi * p),
    "square": lambda p: 1.0 if (p % 1.0) < 0.5 else -1.0,
    "saw": lambda p: 2.0 * (p % 1.0) - 1.0,
    "triangle": lambda p: 4.0 * abs((p % 1.0) - 0.5) - 1.0,
}


def layer(spec, sr, rng, vary):
    dur = float(spec.get("dur", 0.3))
    n = int(sr * dur)
    ratio = 2 ** (rng.uniform(-1, 1) * vary.get("cents", 0) / 1200)
    f0 = float(spec.get("f0", 440)) * ratio
    f1 = float(spec.get("f1", spec.get("f0", 440))) * ratio
    attack, decay, release = float(spec.get("attack", 0.001)), float(spec.get("decay", 0)), float(spec.get("release", 0))
    out, phase = [0.0] * n, 0.0
    fn = WAVES.get(spec.get("wave", "sine"))
    for i in range(n):
        t = i / sr
        if fn:
            phase += (f0 * (f1 / f0) ** (t / dur) if f0 > 0 and f1 > 0 else f0) / sr
            s = fn(phase)
        else:
            s = rng.uniform(-1, 1)
        env = min(1.0, t / attack) if attack > 0 else 1.0
        env *= math.exp(-decay * t)
        if release > 0 and t > dur - release:
            env *= max(0.0, (dur - t) / release)
        out[i] = s * env
    for key, hp in (("lowpass", False), ("highpass", True)):
        fc = spec.get(key)
        if fc:
            a = math.exp(-2 * math.pi * float(fc) / sr)
            y, prev = 0.0, 0.0
            for i, v in enumerate(out):
                y = (1 - a) * v + a * y
                out[i] = v - y if hp else y
    return [v * float(spec.get("gain", 1.0)) for v in out]


def render(recipe, sr, rng):
    vary = recipe.get("vary", {})
    total = int(sr * float(recipe.get("dur", 0.5)))
    mix = [0.0] * total
    for spec in recipe["layers"]:
        start = int(sr * (float(spec.get("start", 0)) + rng.uniform(0, vary.get("start_ms", 0)) / 1000))
        for i, v in enumerate(layer(spec, sr, rng, vary)):
            if start + i < total:
                mix[start + i] += v
    g = 10 ** (rng.uniform(-1, 1) * vary.get("gain_db", 0) / 20)
    fade = min(total, int(sr * 0.005))            # без щелчка в конце
    for i in range(fade):
        mix[total - 1 - i] *= i / fade
    return [v * g for v in mix]


def write(path, samples, sr, lufs_target, ceiling_db):
    lufs, _ = loudness.integrated([samples], sr)
    gain = 10 ** ((lufs_target - lufs) / 20) if lufs_target is not None and lufs > -100 else 1.0
    peak = max((abs(v) for v in samples), default=0.0) * gain
    limit = 10 ** (ceiling_db / 20)
    if peak > limit:
        gain *= limit / peak
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(b"".join(struct.pack("<h", int(max(-1.0, min(1.0, v * gain)) * 32767)) for v in samples))


def main():
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser()
    ap.add_argument("recipes")
    ap.add_argument("out", nargs="?")
    ap.add_argument("names", nargs="*")
    ap.add_argument("--variations", type=int, default=1)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--sr", type=int, default=48000)
    ap.add_argument("--lufs", type=float, default=None)
    ap.add_argument("--ceiling", type=float, default=-1.0)
    ap.add_argument("--prefix", default="")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    with open(a.recipes, encoding="utf-8") as f:
        recipes = {k: v for k, v in json.load(f).items() if not k.startswith("_")}
    if a.list or not a.out:
        print("Рецепты: " + ", ".join(recipes))
        return 0 if a.list else 2
    unknown = [n for n in a.names if n not in recipes]
    if unknown:
        print(f"Неизвестные рецепты: {', '.join(unknown)}. Есть: {', '.join(recipes)}")
        return 2
    os.makedirs(a.out, exist_ok=True)
    for name in a.names or recipes:
        for i in range(a.variations):
            rng = random.Random(a.seed * 1000 + i)
            suffix = f"_{i + 1:02d}" if a.variations > 1 else ""
            path = os.path.join(a.out, f"{a.prefix}{name}{suffix}.wav")
            write(path, render(recipes[name], a.sr, rng), a.sr, a.lufs, a.ceiling)
            m = loudness.measure(path)
            print(f"{os.path.abspath(path)}: {m['duration']:.2f} s · {m['lufs']:.1f} LUFS"
                  f"{' (short)' if m['short'] else ''} · peak {m['peak_db']:.1f} dBFS")
    return 0


if __name__ == "__main__":
    sys.exit(main())

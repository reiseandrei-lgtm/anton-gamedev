#!/usr/bin/env python3
"""Громкость WAV по ITU-R BS.1770-4 / EBU R128 на Python stdlib: K-взвешивание, стробирование, sample peak.

Использование как скрипт:
  python3 loudness.py <file.wav> [...]        # печатает LUFS, sample peak (dBFS), длительность, формат
Как модуль: read_wav(path) → (sr, bits, channels, [[float, …] по каналам]); measure(path) → dict.

Integrated: блоки 400 мс с перекрытием 75 %, абсолютный порог −70 LUFS, относительный −10 LU. Файл короче 400 мс
(короткий SFX) — один блок на весь файл без стробирования (`short: True`). Коэффициенты K-фильтра выводятся для
любой частоты дискретизации (формулы libebur128 / pyloudnorm, MIT); на 48 кГц совпадают с таблицей BS.1770.
True peak здесь не считается (нужна передискретизация) — для него `ffmpeg -af ebur128=peak=true`.
PCM 16/24/32 бит; WAV с float-сэмплами не читается (модуль wave) — переведи через sox/ffmpeg.
"""
import math
import struct
import sys
import wave


def read_wav(path):
    with wave.open(str(path), "rb") as w:
        ch, bits, sr, n = w.getnchannels(), w.getsampwidth() * 8, w.getframerate(), w.getnframes()
        raw = w.readframes(n)
    width = bits // 8
    count = len(raw) // width
    if width == 2:
        vals = struct.unpack(f"<{count}h", raw)
        scale = 32768.0
    elif width == 4:
        vals = struct.unpack(f"<{count}i", raw)
        scale = 2147483648.0
    elif width == 3:
        vals = [int.from_bytes(raw[i:i + 3], "little", signed=True) for i in range(0, len(raw), 3)]
        scale = 8388608.0
    elif width == 1:
        vals = [b - 128 for b in raw]
        scale = 128.0
    else:
        raise ValueError(f"{bits} бит не поддерживается")
    chans = [[v / scale for v in vals[c::ch]] for c in range(ch)]
    return sr, bits, ch, chans


def _biquad(x, b, a):
    b0, b1, b2 = b
    a1, a2 = a
    y, x1, x2, y1, y2 = [0.0] * len(x), 0.0, 0.0, 0.0, 0.0
    for i, v in enumerate(x):
        out = b0 * v + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
        x2, x1, y2, y1 = x1, v, y1, out
        y[i] = out
    return y


def k_coeffs(sr):
    f0, gain, q = 1681.974450955533, 3.999843853973347, 0.7071752369554196
    k = math.tan(math.pi * f0 / sr)
    vh = 10 ** (gain / 20)
    vb = vh ** 0.4996667741545416
    a0 = 1 + k / q + k * k
    shelf = ((vh + vb * k / q + k * k) / a0, 2 * (k * k - vh) / a0, (vh - vb * k / q + k * k) / a0), \
            (2 * (k * k - 1) / a0, (1 - k / q + k * k) / a0)
    f0, q = 38.13547087602444, 0.5003270373238773
    k = math.tan(math.pi * f0 / sr)
    a0 = 1 + k / q + k * k
    hp = (1.0, -2.0, 1.0), (2 * (k * k - 1) / a0, (1 - k / q + k * k) / a0)
    return shelf, hp


def integrated(chans, sr):
    """(LUFS, short) — gated integrated loudness; −inf для тишины."""
    shelf, hp = k_coeffs(sr)
    weights = [1.0, 1.0, 1.0, 0.0, 1.41, 1.41][:len(chans)] if len(chans) > 2 else [1.0] * len(chans)
    filt = [_biquad(_biquad(c, *shelf), *hp) for c in chans]
    n = len(filt[0]) if filt else 0
    block, step = int(0.4 * sr), int(0.1 * sr)
    if n < block:
        z = sum(w * sum(v * v for v in f) / max(n, 1) for w, f in zip(weights, filt))
        return (-0.691 + 10 * math.log10(z) if z > 0 else float("-inf")), True
    sq = [[v * v for v in f] for f in filt]
    pref = []
    for s in sq:
        acc, p = 0.0, [0.0]
        for v in s:
            acc += v
            p.append(acc)
        pref.append(p)
    zs = []
    for start in range(0, n - block + 1, step):
        z = sum(w * (p[start + block] - p[start]) / block for w, p in zip(weights, pref))
        zs.append(z)

    def lufs(z):
        return -0.691 + 10 * math.log10(z) if z > 0 else float("-inf")

    gated = [z for z in zs if lufs(z) > -70]
    if not gated:
        return float("-inf"), False
    rel = lufs(sum(gated) / len(gated)) - 10
    gated = [z for z in gated if lufs(z) > rel]
    return lufs(sum(gated) / len(gated)), False


def measure(path):
    sr, bits, ch, chans = read_wav(path)
    peak = max((abs(v) for c in chans for v in c), default=0.0)
    lufs, short = integrated(chans, sr)
    return {"sr": sr, "bits": bits, "channels": ch, "frames": len(chans[0]) if chans else 0,
            "duration": (len(chans[0]) / sr) if chans else 0.0, "lufs": lufs, "short": short,
            "peak_db": 20 * math.log10(peak) if peak > 0 else float("-inf")}


def main():
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    for p in sys.argv[1:]:
        m = measure(p)
        print(f"{p}: {m['lufs']:.1f} LUFS{' (short)' if m['short'] else ''} · sample peak {m['peak_db']:.1f} dBFS · "
              f"{m['duration']:.3f} s · {m['sr']} Hz {m['bits']} bit {m['channels']} ch")
    return 0


if __name__ == "__main__":
    sys.exit(main())

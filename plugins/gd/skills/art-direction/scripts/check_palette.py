#!/usr/bin/env python3
"""Проверка палитры art-bible: контраст WCAG, grayscale, дальтонизм (Python stdlib).

Использование:
  python3 check_palette.py design/art/art-bible.md

Читает таблицу `| Role | HEX | Use |` в разделе `## Palette`.
Пары и пороги — references/art-method.md §2. Выход с кодом 1, если есть FAIL.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "gd-router" / "scripts"))
import gdd_ids  # noqa: E402

REQUIRED = ["bg", "gameplay", "interactive", "danger", "ui-text"]
# (a, b, порог WCAG, тип проверки)
PAIRS = [
    ("gameplay", "bg", 3.0, "contrast"),
    ("interactive", "bg", 3.0, "contrast"),
    ("danger", "bg", 3.0, "contrast"),
    ("ui-text", "bg", 4.5, "contrast"),
    ("accent", "bg", 3.0, "contrast"),
    ("danger", "gameplay", 1.5, "distinct"),
    ("interactive", "gameplay", 1.5, "distinct"),
    ("accent", "interactive", 1.5, "distinct"),
    ("accent", "gameplay", 1.5, "distinct"),
]
MIN_L_DELTA = 20.0
MIN_DE = 20.0      # различимость пары в норме
CVD_MIN_DE = 12.0  # различимость при симуляции дальтонизма
# Machado, Oliveira, Fernandes 2009, severity 1.0, в линейном RGB
CVD = {
    "протанопия": ((0.152286, 1.052583, -0.204868), (0.114503, 0.786281, 0.099216), (-0.003882, -0.048116, 1.051998)),
    "дейтеранопия": ((0.367322, 0.860646, -0.227968), (0.280085, 0.672501, 0.047413), (-0.011820, 0.042940, 0.968881)),
    "тританопия": ((1.255528, -0.076749, -0.178779), (-0.078411, 0.930809, 0.147602), (0.004733, 0.691367, 0.303900)),
}


def hex_rgb(h):
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if not re.fullmatch(r"[0-9a-fA-F]{6}", h):
        raise ValueError(h)
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def to_lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def lum(lin):
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(l1, l2):
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def lab(lin):
    x = (0.4124 * lin[0] + 0.3576 * lin[1] + 0.1805 * lin[2]) / 0.95047
    y = 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]
    z = (0.0193 * lin[0] + 0.1192 * lin[1] + 0.9505 * lin[2]) / 1.08883

    def f(t):
        return t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116
    fx, fy, fz = f(x), f(y), f(z)
    return (116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz))


def de76(a, b):
    return sum((p - q) ** 2 for p, q in zip(a, b)) ** 0.5


def simulate(lin, m):
    return tuple(min(1.0, max(0.0, sum(m[r][k] * lin[k] for k in range(3)))) for r in range(3))


def base_role(role):
    return re.sub(r"-\d+$", "", role.strip().lower())


def main():
    gdd_ids.utf8_stdout()
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    text = gdd_ids.read(sys.argv[1])
    lines = gdd_ids.find_section(gdd_ids.sections(text), "palette")
    if lines is None:
        print("FAIL: нет раздела `## Palette`")
        return 1
    colors, fails, warns = {}, [], []
    for row in gdd_ids.table_rows(lines):
        role, hx = row.get("role", ""), row.get("hex", "")
        if not role or not hx or "<" in role:
            continue
        try:
            lin = tuple(to_lin(c) for c in hex_rgb(hx))
        except ValueError:
            fails.append(f"{role}: неверный HEX «{hx}»")
            continue
        colors.setdefault(base_role(role), []).append((role, hx, lin))
    for r in REQUIRED:
        if r not in colors:
            fails.append(f"нет обязательной роли `{r}`")
    print(f"Палитра: {sum(len(v) for v in colors.values())} цветов, роли: {', '.join(sorted(colors))}")
    for a, b, thr, kind in PAIRS:
        for ra, ha, la in colors.get(a, []):
            for rb, hb, lb in colors.get(b, []):
                c = contrast(lum(la), lum(lb))
                laba, labb = lab(la), lab(lb)
                tag = f"{ra} {ha} / {rb} {hb}"
                if kind == "contrast":
                    dl = abs(laba[0] - labb[0])
                    status = "OK" if c >= thr else "FAIL"
                    print(f"  {status:4} {tag}: контраст {c:.2f} (нужно ≥ {thr}), ΔL* {dl:.0f}")
                    if c < thr:
                        fails.append(f"{tag}: контраст {c:.2f} < {thr}")
                    if dl < MIN_L_DELTA:
                        warns.append(f"{tag}: ΔL* {dl:.0f} < {MIN_L_DELTA:.0f} — сливается в grayscale")
                    continue
                de = de76(laba, labb)
                if c < thr and de < MIN_DE:
                    fails.append(f"{tag}: неразличимы в норме (контраст {c:.2f}, ΔE {de:.0f})")
                    print(f"  FAIL {tag}: неразличимы (контраст {c:.2f}, ΔE {de:.0f})")
                    continue
                bad = []
                for name, m in CVD.items():
                    sa, sb = simulate(la, m), simulate(lb, m)
                    sc, sde = contrast(lum(sa), lum(sb)), de76(lab(sa), lab(sb))
                    if sc < thr and sde < CVD_MIN_DE:
                        bad.append(f"{name} (контраст {sc:.2f}, ΔE {sde:.0f})")
                if bad:
                    fails.append(f"{tag}: различается только оттенком — {'; '.join(bad)}")
                    print(f"  FAIL {tag}: сливаются при {'; '.join(bad)}")
                else:
                    print(f"  OK   {tag}: различимы в норме и при 3 видах дальтонизма (контраст {c:.2f}, ΔE {de:.0f})")
    for w in warns:
        print(f"WARN {w}")
    for f in fails:
        print(f"FAIL {f}")
    print(f"Итог: {'FAIL' if fails else ('WARN' if warns else 'PASS')} · FAIL {len(fails)} · WARN {len(warns)}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())

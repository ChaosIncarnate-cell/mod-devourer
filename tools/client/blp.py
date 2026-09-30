"""BLP2 textures for the client patch: palettized with 8-bit alpha and a full mip chain (the format every
3.3.5a client reads). Needs Pillow (pip install pillow).

    python blp.py icon.png out.blp          convert an image (the class icon made from the CoA emblem)
    python blp.py --placeholder out.png     draw the placeholder icon the patch uses when no icon is given
"""
from __future__ import annotations

import struct
import sys


def _pil():
    try:
        from PIL import Image, ImageDraw, ImageFilter
    except ImportError:
        raise SystemExit("Pillow is needed for the class icon: python -m pip install pillow")
    return Image, ImageDraw, ImageFilter


def to_blp(img, size: int | None = None) -> bytes:
    """An image as BLP2 (compression 1 = palette, alpha depth 8), sides rounded to powers of two."""
    Image, _, _ = _pil()
    img = img.convert("RGBA")
    w, h = img.size
    if size:
        w = h = size
    pw, ph = 1 << max(0, (w - 1).bit_length()), 1 << max(0, (h - 1).bit_length())
    img = img.resize((pw, ph), Image.LANCZOS) if (pw, ph) != img.size else img

    mips = [img]
    while mips[-1].size != (1, 1):
        mw, mh = mips[-1].size
        mips.append(img.resize((max(1, mw // 2), max(1, mh // 2)), Image.LANCZOS))
    mips = mips[:16]

    # one palette for every level, from the full-size image
    palette_img = img.convert("RGB").quantize(colors=256, method=Image.Quantize.MEDIANCUT)
    rgb = palette_img.getpalette()[:768]
    rgb += [0] * (768 - len(rgb))
    palette = b"".join(struct.pack("<4B", rgb[i * 3 + 2], rgb[i * 3 + 1], rgb[i * 3], 255) for i in range(256))

    blobs = []
    for mip in mips:
        idx = mip.convert("RGB").quantize(palette=palette_img, dither=Image.Dither.NONE)
        blobs.append(idx.tobytes() + mip.getchannel("A").tobytes())

    offsets, sizes, pos = [], [], 148 + 1024
    for b in blobs:
        offsets.append(pos)
        sizes.append(len(b))
        pos += len(b)
    offsets += [0] * (16 - len(offsets))
    sizes += [0] * (16 - len(sizes))
    header = (b"BLP2" + struct.pack("<I4B2I", 1, 1, 8, 8, 1, pw, ph)
              + struct.pack("<16I", *offsets) + struct.pack("<16I", *sizes))
    return header + palette + b"".join(blobs)


def placeholder_icon(size: int = 64):
    """Our own stand-in until the CoA emblem is converted: a bronze maw with glowing eyes on a dark ground."""
    Image, ImageDraw, ImageFilter = _pil()
    s = size * 4                                            # drawn large, scaled down for smooth edges
    img = Image.new("RGBA", (s, s), (0, 0, 0, 255))
    d = ImageDraw.Draw(img)
    for r in range(s // 2, 0, -2):                          # dark red-brown radial ground
        t = r / (s / 2)
        d.ellipse([s / 2 - r * 1.5, s / 2 - r * 1.5, s / 2 + r * 1.5, s / 2 + r * 1.5],
                  fill=(int(70 - 45 * t), int(28 - 18 * t), int(20 - 14 * t), 255))
    bronze, dark = (184, 120, 46, 255), (40, 14, 10, 255)
    cx, cy, rad = s / 2, s * 0.56, s * 0.30
    d.ellipse([cx - rad, cy - rad * 0.8, cx + rad, cy + rad * 0.8], fill=bronze)
    d.ellipse([cx - rad * 0.78, cy - rad * 0.58, cx + rad * 0.78, cy + rad * 0.58], fill=dark)
    teeth = 9
    for i in range(teeth):                                  # fangs along the upper and lower lip
        x0 = cx - rad * 0.7 + i * (rad * 1.4 / teeth)
        x1 = x0 + rad * 1.4 / teeth
        d.polygon([(x0, cy - rad * 0.5), (x1, cy - rad * 0.5), ((x0 + x1) / 2, cy - rad * 0.12)], fill=bronze)
        d.polygon([(x0, cy + rad * 0.5), (x1, cy + rad * 0.5), ((x0 + x1) / 2, cy + rad * 0.14)], fill=bronze)
    glow = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    g = ImageDraw.Draw(glow)
    for ex in (cx - s * 0.16, cx + s * 0.16):
        g.ellipse([ex - s * 0.07, s * 0.17, ex + s * 0.07, s * 0.27], fill=(255, 170, 40, 255))
    img = Image.alpha_composite(img, glow.filter(ImageFilter.GaussianBlur(s * 0.02)))
    img = Image.alpha_composite(img, glow)
    return img.resize((size, size), Image.LANCZOS)


def read_blp_size(data: bytes) -> tuple[int, int]:
    if data[:4] != b"BLP2":
        raise ValueError("not a BLP2 texture")
    return struct.unpack_from("<2I", data, 12)


if __name__ == "__main__":
    Image, _, _ = _pil()
    if len(sys.argv) == 3 and sys.argv[1] == "--placeholder":
        placeholder_icon(128).save(sys.argv[2])
    elif len(sys.argv) == 3:
        with open(sys.argv[2], "wb") as f:
            f.write(to_blp(Image.open(sys.argv[1])))
    else:
        raise SystemExit(__doc__)

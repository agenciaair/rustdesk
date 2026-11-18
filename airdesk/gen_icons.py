"""Gera os icones do AIRDESK com a identidade da AIR (a mesma do admin.agenciaair.tech):
- airdesk/air-icon.png: simbolo "AR" sobre #111 (favicon do admin) -> icones do app
- airdesk/air-logo.png: logotipo "AiR" em PNG transparente -> logo dentro do app
Uso (na raiz do repo): python airdesk/gen_icons.py
"""
import os
from PIL import Image, ImageChops

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "airdesk", "air-icon.png")
WORDMARK = os.path.join(ROOT, "airdesk", "air-logo.png")
BG = (17, 17, 17, 255)  # #111, fundo do icone do admin


def p(*a):
    return os.path.join(ROOT, *a)


src = Image.open(SRC).convert("RGB")
# Logo recortado sobre fundo transparente: alpha = brilho maximo do pixel.
r, g, b = src.split()
alpha = ImageChops.lighter(ImageChops.lighter(r, g), b)
alpha = alpha.point(lambda v: 0 if v < 24 else min(255, int((v - 24) * 255 / 200)))
logo = src.convert("RGBA")
logo.putalpha(alpha)
logo = logo.crop(logo.getbbox())  # so o desenho "AIR"


def fit(img, size, pad):
    """Centraliza img num quadrado transparente size x size com margem pad (0-1)."""
    inner = int(size * (1 - 2 * pad))
    im = img.copy()
    im.thumbnail((inner, inner), Image.LANCZOS)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    canvas.paste(im, ((size - im.width) // 2, (size - im.height) // 2), im)
    return canvas


def square(size, pad=0.14, radius=0.0):
    canvas = Image.new("RGBA", (size, size), BG)
    fg = fit(logo, size, pad)
    canvas.alpha_composite(fg)
    if radius:
        mask = Image.new("L", (size, size), 0)
        from PIL import ImageDraw
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, size - 1, size - 1], int(size * radius), fill=255)
        canvas.putalpha(mask)
    return canvas


def round_icon(size):
    from PIL import ImageDraw
    canvas = square(size, pad=0.2)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, size - 1, size - 1], fill=255)
    canvas.putalpha(mask)
    return canvas


def white(img):
    w = Image.new("RGBA", img.size, (255, 255, 255, 0))
    w.putalpha(img.getchannel("A"))
    return w


def save(img, *path):
    full = p(*path)
    img.save(full)
    print("ok", os.path.relpath(full, ROOT), img.size)


# --- res/ (desktop) ---
big = square(1024, radius=0.18)
save(big, "res", "icon.png")
save(big, "res", "mac-icon.png")
for s, name in [(32, "32x32.png"), (64, "64x64.png"), (128, "128x128.png"), (256, "128x128@2x.png")]:
    save(big.resize((s, s), Image.LANCZOS), "res", name)
ico_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
for target in [("res", "icon.ico"), ("flutter", "windows", "runner", "resources", "app_icon.ico")]:
    big.save(p(*target), sizes=ico_sizes)
    print("ok", "/".join(target))
square(256, pad=0.08).save(p("res", "tray-icon.ico"), sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64)])
print("ok res/tray-icon.ico")
for name in ["mac-tray-dark-x2.png", "mac-tray-light-x2.png"]:
    old = Image.open(p("res", name))
    t = fit(white(logo), max(old.size), 0.05).resize(old.size, Image.LANCZOS)
    if "light" in name:
        t = Image.merge("RGBA", (*Image.new("RGB", t.size, (0, 0, 0)).split(), t.getchannel("A")))
    save(t, "res", name)

# --- flutter/assets (icone e logo dentro do app) ---
save(square(512, radius=0.18), "flutter", "assets", "icon.png")
wordmark = Image.open(WORDMARK).convert("RGBA")
wordmark = wordmark.crop(wordmark.getbbox())
wordmark.thumbnail((600, 120), Image.LANCZOS)
save(wordmark, "flutter", "assets", "logo_dark.png")  # tema escuro: letras brancas
dark_letters = wordmark.copy()
px = dark_letters.load()
for y in range(dark_letters.height):
    for x in range(dark_letters.width):
        rr, gg, bb, aa = px[x, y]
        if aa and abs(rr - gg) < 40 and abs(gg - bb) < 40:  # parte branca/cinza -> preta
            px[x, y] = (17, 17, 17, aa)
save(dark_letters, "flutter", "assets", "logo_light.png")  # tema claro: letras pretas
save(dark_letters, "flutter", "assets", "logo.png")

# --- Android ---
dens = {"mdpi": 1, "hdpi": 1.5, "xhdpi": 2, "xxhdpi": 3, "xxxhdpi": 4}
for d, k in dens.items():
    base = ("flutter", "android", "app", "src", "main", "res", "mipmap-" + d)
    save(square(int(48 * k), pad=0.16, radius=0.18), *base, "ic_launcher.png")
    save(round_icon(int(48 * k)), *base, "ic_launcher_round.png")
    # adaptive icon: area segura = 66% central
    save(fit(logo, int(108 * k), 0.27), *base, "ic_launcher_foreground.png")
    save(fit(white(logo), int(24 * k), 0.04), *base, "ic_stat_logo.png")

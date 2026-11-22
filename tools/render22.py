#!/usr/bin/env python3
"""Render the 22 November 2026 broadsheet (news-image-20261122).

Reads news.json + three CC file photos, draws a one-page newspaper at
2x (1360x2048) with Pillow, then downscales with LANCZOS to 680x1024
and writes entry.png. No network, no clock: the same input bytes give
the same output bytes every run.
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SCALE = 2
W, H = 680 * SCALE, 1024 * SCALE
MARGIN = 26 * SCALE
PAPER = (247, 243, 234)
INK = (22, 22, 22)
GREY = (92, 88, 80)
RED = (163, 22, 33)
RULE = (30, 30, 30)
FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    """Load a DejaVu face at 2x size; fall back to plain sans."""
    path = os.path.join(FONT_DIR, name)
    if not os.path.exists(path):
        path = os.path.join(FONT_DIR, "DejaVuSans.ttf")
    return ImageFont.truetype(path, size * SCALE)


SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
SERIF = lambda s: font("DejaVuSerif.ttf", s)
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)
SANS = lambda s: font("DejaVuSans.ttf", s)


def wrap(draw, text, fnt, width):
    """Greedy word wrap; returns a list of lines that fit width."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(draw, x, y, text, fnt, fill, width, lead):
    """Draw a wrapped paragraph; returns the y below it."""
    for line in wrap(draw, text, fnt, width):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += lead
    return y


def rule(draw, x0, y, x1, width=1):
    draw.line([(x0, y), (x1, y)], fill=RULE, width=width * SCALE)


def cover(path, w, h):
    """Centre-crop an image to fill w x h exactly."""
    img = Image.open(path).convert("RGB")
    return ImageOps.fit(img, (w, h), Image.LANCZOS)


def main():
    with open(os.path.join(ROOT, "news.json"), encoding="utf-8") as fh:
        news = json.load(fh)

    page = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(page)
    cw = W - 2 * MARGIN  # content width
    y = 16 * SCALE

    # ---- Masthead -------------------------------------------------
    mast = SERIF_B(44)
    tw = d.textlength(news["masthead"], font=mast)
    d.text(((W - tw) / 2, y), news["masthead"], font=mast, fill=INK)
    y += 52 * SCALE
    date_f = SANS_B(13)
    tw = d.textlength(news["dateline"], font=date_f)
    d.text(((W - tw) / 2, y), news["dateline"], font=date_f, fill=INK)
    y += 20 * SCALE
    ed_f = SANS(10)
    tw = d.textlength(news["edition"], font=ed_f)
    d.text(((W - tw) / 2, y), news["edition"], font=ed_f, fill=GREY)
    y += 18 * SCALE
    rule(d, MARGIN, y, W - MARGIN, 3)
    y += 4 * SCALE
    rule(d, MARGIN, y, W - MARGIN, 1)
    y += 12 * SCALE

    # ---- Lead story: Hong Kong ------------------------------------
    lead = news["lead"]
    kick = SANS_B(11)
    d.text((MARGIN, y), lead["kicker"], font=kick, fill=RED)
    y += 18 * SCALE
    head = SERIF_B(38)
    d.text((MARGIN, y), lead["headline"], font=head, fill=INK)
    y += 46 * SCALE
    deck_f = SANS(13)
    y = para(d, MARGIN, y, lead["deck"], deck_f, INK, cw, 17 * SCALE)
    y += 8 * SCALE
    photo_h = 185 * SCALE
    page.paste(cover(os.path.join(ROOT, lead["photo"]), cw, photo_h),
               (MARGIN, y))
    y += photo_h + 5 * SCALE
    cap_f = SANS(9)
    y = para(d, MARGIN, y, lead["photo_credit"], cap_f, GREY, cw,
             12 * SCALE)
    y += 8 * SCALE
    # Lead body in two columns.
    body_f = SERIF(11)
    col_w = (cw - 14 * SCALE) // 2
    paras = lead["body"]
    # Split paragraphs across the two columns by lines.
    all_lines = []
    for p in paras:
        all_lines.extend(wrap(d, p, body_f, col_w))
        all_lines.append("")  # paragraph gap
    half = (len(all_lines) + 1) // 2
    left, right = all_lines[:half], all_lines[half:]
    top_y = y
    yy = top_y
    for line in left:
        if line:
            d.text((MARGIN, yy), line, font=body_f, fill=INK)
        yy += 15 * SCALE
    yy = top_y
    for line in right:
        if line:
            d.text((MARGIN + col_w + 14 * SCALE, yy), line,
                   font=body_f, fill=INK)
        yy += 15 * SCALE
    y = max(yy, top_y) + 4 * SCALE
    rule(d, MARGIN, y, W - MARGIN, 1)
    y += 10 * SCALE

    # ---- Two stories side by side ---------------------------------
    def column(x, w, story):
        yy = y
        kick_f = SANS_B(10)
        d.text((x, yy), story["kicker"], font=kick_f, fill=RED)
        yy += 16 * SCALE
        h_f = SERIF_B(18)
        for line in wrap(d, story["headline"], h_f, w):
            d.text((x, yy), line, font=h_f, fill=INK)
            yy += 22 * SCALE
        yy += 3 * SCALE
        ph = 88 * SCALE
        page.paste(cover(os.path.join(ROOT, story["photo"]), w, ph),
                   (x, yy))
        yy += ph + 4 * SCALE
        yy = para(d, x, yy, story["photo_credit"], SANS(8), GREY, w,
                  11 * SCALE)
        yy += 5 * SCALE
        yy = para(d, x, yy, story["body"], SERIF(11), INK, w,
                  15 * SCALE)
        return yy

    col_w2 = (cw - 14 * SCALE) // 2
    end_l = column(MARGIN, col_w2, news["second"])
    end_r = column(MARGIN + col_w2 + 14 * SCALE, col_w2, news["third"])
    # Vertical divider between the two columns.
    d.line([(W // 2, y), (W // 2, max(end_l, end_r))], fill=RULE,
           width=1 * SCALE)
    y = max(end_l, end_r) + 8 * SCALE
    rule(d, MARGIN, y, W - MARGIN, 1)
    y += 8 * SCALE

    # ---- The day in brief -----------------------------------------
    brief_f = SANS_B(10)
    d.text((MARGIN, y), "THE DAY IN BRIEF", font=brief_f, fill=INK)
    y += 16 * SCALE
    bw = (cw - 2 * 12 * SCALE) // 3
    ends = []
    for i, b in enumerate(news["briefs"]):
        bx = MARGIN + i * (bw + 12 * SCALE)
        yy = y
        d.text((bx, yy), b["tag"], font=SANS_B(10), fill=RED)
        yy += 14 * SCALE
        yy = para(d, bx, yy, b["text"], SANS(10), INK, bw, 13 * SCALE)
        ends.append(yy)
    y = max(ends) + 8 * SCALE
    rule(d, MARGIN, y, W - MARGIN, 1)
    y += 6 * SCALE

    # ---- Footer ----------------------------------------------------
    y = para(d, MARGIN, y, news["footer"], SANS(8), GREY, cw,
             11 * SCALE)

    out = page.resize((680, 1024), Image.LANCZOS)
    dest = os.path.join(ROOT, "entry.png")
    out.save(dest, "PNG", optimize=True)
    size = os.path.getsize(dest)
    print(f"wrote {dest} {out.size} {size} bytes")
    if size > 1024 * 1024:
        print("OVER 1 MiB!", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

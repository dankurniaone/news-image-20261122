#!/usr/bin/env python3
"""Render THE WORLD TODAY — a one-page broadsheet summing up the world news
of Sunday 22 November 2026 — as a 680x1024 PNG.

Drawn at 2x (1360x2048) with Pillow and downscaled with LANCZOS so the
small type stays crisp. Layout: masthead, Hong Kong election lead with a
real skyline photograph, Israel and COP31 side by side with real photos,
a three-brief strip, and a sources footer. All photographs are freely
licensed file photos, credited in the footer; none is from 22 November
itself. Every story on the page is an event of 22 November 2026.
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

SCALE = 2
W, H = 680 * SCALE, 1024 * SCALE
MARGIN = 28 * SCALE
CW = W - 2 * MARGIN  # content width

PAPER = (246, 242, 231)
INK = (17, 17, 17)
RED = (164, 30, 34)
GREY = (90, 86, 78)

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size * SCALE)


def wrap(text, fnt, width, draw):
    """Greedy word wrap to a pixel width; returns a list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_lines(draw, x, y, lines, fnt, fill=INK, leading=None):
    """Draw lines top to bottom; returns the y below the last line."""
    lh = leading if leading is not None else int(fnt.size * 1.35)
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += lh
    return y


def crop_cover(img, tw, th):
    """Centre-crop an image to the target aspect, then resize to it."""
    iw, ih = img.size
    ta = tw / th
    ia = iw / ih
    if ia > ta:  # too wide: trim sides
        nw = int(ih * ta)
        x0 = (iw - nw) // 2
        img = img.crop((x0, 0, x0 + nw, ih))
    else:  # too tall: trim top/bottom
        nh = int(iw / ta)
        y0 = (ih - nh) // 2
        img = img.crop((0, y0, iw, y0 + nh))
    return img.resize((tw, th), Image.LANCZOS)


def tracked(draw, x, y, text, fnt, fill, tracking=0):
    """Draw text with extra space between characters; returns end x."""
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textlength(ch, font=fnt) + tracking
    return x


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    x = MARGIN
    y = 18 * SCALE

    # ---- Masthead ----
    f_mast = font(SERIF_B, 48)
    t = "THE WORLD TODAY"
    d.text(((W - d.textlength(t, font=f_mast)) / 2, y), t, font=f_mast, fill=INK)
    y += int(48 * SCALE * 1.25)

    f_date = font(SANS_B, 15)
    t = "SUNDAY, 22 NOVEMBER 2026"
    d.text(((W - d.textlength(t, font=f_date)) / 2, y), t, font=f_date, fill=INK)
    y += int(15 * SCALE * 1.6)

    f_sub = font(SANS, 11)
    t = "ONE DAY  ·  ONE PAGE  ·  No. 326"
    d.text(((W - d.textlength(t, font=f_sub)) / 2, y), t, font=f_sub, fill=GREY)
    y += int(11 * SCALE * 1.6) + 6 * SCALE

    d.rectangle([x, y, x + CW, y + 3 * SCALE], fill=INK)
    y += 5 * SCALE
    d.rectangle([x, y, x + CW, y + 1 * SCALE], fill=INK)
    y += 8 * SCALE

    # ---- Lead: Hong Kong ----
    f_kick = font(SANS_B, 13)
    tracked(d, x, y, "HONG KONG · ELECTION", f_kick, RED, tracking=2)
    y += int(13 * SCALE * 1.7)

    f_head = font(SERIF_B, 54)
    d.text((x, y), "HONG KONG VOTES", font=f_head, fill=INK)
    y += int(54 * SCALE * 1.15)

    f_deck = font(SERIF, 16)
    deck = ("About 5,700 voters pick the 1,500-member committee that will choose "
            "Hong Kong's next leader, as 856 candidates contest 723 seats "
            "across 31 subsectors.")
    y = draw_lines(d, x, y + 2 * SCALE, wrap(deck, f_deck, CW, d), f_deck,
                   leading=int(16 * SCALE * 1.45))
    y += 4 * SCALE

    hk = Image.open(os.path.join(ROOT, "assets", "hk-skyline.jpg")).convert("RGB")
    ph = 135 * SCALE
    img.paste(crop_cover(hk, CW, ph), (x, y))
    y += ph + 4 * SCALE
    f_cap = font(SERIF_I, 11)
    d.text((x, y), "Hong Kong's skyline. Polling runs 9am–6pm across five stations. (File photo)",
           font=f_cap, fill=GREY)
    y += int(11 * SCALE * 1.7) + 2 * SCALE

    # Lead body, two columns
    f_body = font(SERIF, 13)
    col_w = (CW - 20 * SCALE) // 2
    lh = int(13 * SCALE * 1.5)
    left = ("Polls opened at 9am today in Hong Kong's Election Committee "
            "Subsector Ordinary Elections, with 856 candidates contesting "
            "723 seats. The 5,700 voters choose the 1,500-strong Election "
            "Committee, which nominates and elects the chief executive and "
            "picks 40 lawmakers.")
    right = ("Voting runs until 6pm at five ordinary polling stations, and "
             "the committee's five-year term begins on 1 February 2027. "
             "The results will shape the race for the city's top job next year.")
    y1 = draw_lines(d, x, y, wrap(left, f_body, col_w, d), f_body, leading=lh)
    y2 = draw_lines(d, x + col_w + 20 * SCALE, y,
                    wrap(right, f_body, col_w, d), f_body, leading=lh)
    y = max(y1, y2) + 6 * SCALE

    d.rectangle([x, y, x + CW, y + 1 * SCALE], fill=INK)
    y += 8 * SCALE

    # ---- Middle: Israel | COP31 ----
    mid_y = y
    col_w = (CW - 20 * SCALE) // 2
    f_mid_head = font(SERIF_B, 24)

    def story(cx, kicker, headline, photo, caption, body):
        yy = mid_y
        tracked(d, cx, yy, kicker, f_kick, RED, tracking=2)
        yy += int(13 * SCALE * 1.7)
        yy = draw_lines(d, cx, yy, wrap(headline, f_mid_head, col_w, d),
                        f_mid_head, leading=int(24 * SCALE * 1.12))
        yy += 3 * SCALE
        im = Image.open(os.path.join(ROOT, "assets", photo)).convert("RGB")
        ph2 = 72 * SCALE
        img.paste(crop_cover(im, col_w, ph2), (cx, yy))
        yy += ph2 + 4 * SCALE
        d.text((cx, yy), caption, font=f_cap, fill=GREY)
        yy += int(11 * SCALE * 1.7) + 2 * SCALE
        yy = draw_lines(d, cx, yy, wrap(body, f_body, col_w, d), f_body, leading=lh)
        return yy

    y_isr = story(
        x, "ISRAEL · GOVERNMENT",
        "EISENKOT BEGINS BID TO FORM GOVERNMENT",
        "knesset.jpg", "The Knesset in Jerusalem. (File photo)",
        ("Gadi Eisenkot, the former army chief, begins intensive coalition "
         "talks with Likud today after President Isaac Herzog asked him — "
         "not Benjamin Netanyahu — to try to form Israel's next government. "
         "Herzog informed Netanyahu on Saturday evening; the mandate "
         "handover takes place today."))
    y_cop = story(
        x + col_w + 20 * SCALE, "CLIMATE · COP31",
        "CLIMATE TALKS DEADLOCKED AS COP31 RUNS INTO OVERTIME",
        "turbines.jpg", "Wind turbines. The fossil-fuel fight has stalled the talks. (File photo)",
        ("Climate talks in Antalya run past their deadline with no deal, "
         "deadlocked over fossil fuels after a draft text stripped out every "
         "mention of them. Delegates worked through the night as a third "
         "draft was promised for this morning; nearly 200 countries are at "
         "the table."))
    y = max(y_isr, y_cop)
    # vertical divider between the two middle stories
    div_x = x + col_w + 10 * SCALE
    d.rectangle([div_x, mid_y, div_x + 1 * SCALE, y - 4 * SCALE], fill=INK)
    y += 6 * SCALE

    d.rectangle([x, y, x + CW, y + 1 * SCALE], fill=INK)
    y += 8 * SCALE

    # ---- The day in brief ----
    f_brief_h = font(SANS_B, 13)
    tracked(d, x, y, "THE DAY IN BRIEF", f_brief_h, INK, tracking=2)
    y += int(13 * SCALE * 1.8)
    bw = (CW - 2 * 16 * SCALE) // 3
    f_bh = font(SANS_B, 12)
    f_bb = font(SERIF, 13)
    briefs = [
        ("MYANMAR", "A magnitude 4.1 earthquake struck Myanmar in the early "
                    "hours of today."),
        ("VENICE", "The 61st Venice Art Biennale closes today after six "
                   "months, ending the world's biggest art exhibition."),
        ("TURIN", "The Nitto ATP Finals reach their final day in Turin "
                  "today, closing the season's last showpiece."),
    ]
    yb = y
    for i, (h, b) in enumerate(briefs):
        bx = x + i * (bw + 16 * SCALE)
        d.text((bx, y), h, font=f_bh, fill=RED)
        yy = draw_lines(d, bx, y + int(12 * SCALE * 1.7),
                        wrap(b, f_bb, bw, d), f_bb, leading=int(13 * SCALE * 1.45))
        yb = max(yb, yy)
    y = yb + 8 * SCALE

    d.rectangle([x, y, x + CW, y + 1 * SCALE], fill=INK)
    y += 6 * SCALE

    # ---- Footer ----
    f_foot = font(SANS, 8)
    foot1 = ("All events on this page happened on Sunday 22 November 2026. Sources: Hong Kong "
             "Registration and Electoral Office; China Daily Asia; Times of Israel; BBC; "
             "National Centre for Seismology.")
    foot2 = ("Photos are freely licensed file photos, not from today: Hong Kong "
             "skyline — Portland Seminary, CC BY-SA; Knesset — leighklotz, CC BY; wind "
             "turbines — sludgegulper, CC BY-SA.")
    y = draw_lines(d, x, y, wrap(foot1, f_foot, CW, d), f_foot, fill=GREY,
                   leading=int(8 * SCALE * 1.55))
    y = draw_lines(d, x, y + 2 * SCALE, wrap(foot2, f_foot, CW, d), f_foot,
                   fill=GREY, leading=int(8 * SCALE * 1.55))

    out = img.resize((680, 1024), Image.LANCZOS)
    out.save(os.path.join(ROOT, "entry.png"), "PNG")
    print("wrote entry.png", out.size,
          os.path.getsize(os.path.join(ROOT, "entry.png")), "bytes")


if __name__ == "__main__":
    main()

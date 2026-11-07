#!/usr/bin/env python3
"""Render a looping hand-drawn explainer GIF from a small JSON document."""
import argparse
import json
import math
import os
import random
import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

SCENES = {"grid", "parallel", "flow"}
DEFAULTS = {
    "grid": ["输入", "处理", "结果"],
    "parallel": ["任务 1", "任务 2", "任务 3"],
    "flow": ["CPU", "数据", "GPU", "结果"],
}


def validate(data):
    if not isinstance(data, dict):
        raise ValueError("JSON 根节点必须是对象 / JSON root must be an object")
    allowed = {"scene", "title", "subtitle", "labels", "width", "height", "frames", "duration", "font"}
    extra = set(data) - allowed
    if extra:
        raise ValueError("未知字段 / unknown fields: " + ", ".join(sorted(extra)))
    scene = data.get("scene")
    if scene not in SCENES:
        raise ValueError("scene must be one of: grid, parallel, flow")
    for key in ("title", "subtitle", "font"):
        if key in data and not isinstance(data[key], str):
            raise ValueError(f"{key} must be a string")
    for key, low, high, default in (("width", 320, 1920, 800), ("height", 240, 1080, 450),
                                    ("frames", 2, 120, 16), ("duration", 20, 2000, 100)):
        value = data.get(key, default)
        if isinstance(value, bool) or not isinstance(value, int) or not low <= value <= high:
            raise ValueError(f"{key} must be an integer between {low} and {high}")
    labels = data.get("labels", DEFAULTS[scene])
    limits = {"grid": (1, 9), "parallel": (2, 6), "flow": (2, 5)}
    low, high = limits[scene]
    if not isinstance(labels, list) or not low <= len(labels) <= high or any(not isinstance(x, str) or not x.strip() for x in labels):
        raise ValueError(f"labels must contain {low}–{high} nonempty strings for {scene}")
    return labels


def choose_font(explicit):
    candidates = [explicit] if explicit else [os.path.expanduser("~/.local/share/fonts/codex-handwriting/LongCang-Regular.ttf")]
    try:
        # Fontconfig is optional; prefer a font containing Chinese glyphs.
        result = subprocess.run(["fc-list", ":lang=zh", "-f", "%{file}\n"], capture_output=True, text=True, timeout=3, check=False)
        if result.stdout:
            candidates.extend(result.stdout.splitlines())
    except (OSError, subprocess.SubprocessError):
        pass
    candidates += ["/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc", "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", "/usr/share/fonts/sarasa-gothic/Sarasa-Regular.ttc", "/System/Library/Fonts/PingFang.ttc", "C:/Windows/Fonts/msyh.ttc", "DejaVuSans.ttf"]
    for candidate in candidates:
        if not candidate:
            continue
        try:
            ImageFont.truetype(candidate, 18)
            if explicit and candidate != explicit:
                print(f"Warning: cannot load font {explicit!r}; using {candidate!r}", file=sys.stderr)
            if candidate == "DejaVuSans.ttf":
                print("Warning: no CJK font found; Chinese characters may be missing", file=sys.stderr)
            return candidate
        except (OSError, ValueError):
            continue
    print("Warning: no TrueType font found; using Pillow default; Chinese may be missing", file=sys.stderr)
    return None


def font(path, size):
    return ImageFont.truetype(path, max(8, int(size))) if path else ImageFont.load_default(size=max(8, int(size)))


def render(data, labels, fontpath):
    w, h = data.get("width", 800), data.get("height", 450)
    count = data.get("frames", 16)
    scene = data["scene"]
    # Work at requested resolution; a stable paper texture avoids distracting flicker.
    scale = min(w / 800, h / 450)
    rng = random.Random(78123)
    paper = Image.new("RGB", (w, h), "#f7f2e5")
    pd = ImageDraw.Draw(paper)
    for _ in range(int(w * h / 140)):
        x, y = rng.randrange(w), rng.randrange(h)
        pd.point((x, y), fill=rng.choice(("#e8e0ce", "#eee7d8", "#f1eadc")))
    for y in range(max(1, round(75*scale)), h, max(1, round(35*scale))):
        pd.line((20*scale, y, w-20*scale, y), fill="#eae2d1", width=1)
    ink, accent, pale = "#394653", "#d77355", "#b7c9bf"
    titlefont, textfont, smallfont = font(fontpath, 42*scale), font(fontpath, 30*scale), font(fontpath, 23*scale)

    def xy(x, y): return (x*w/800, y*h/450)
    def line(draw, points, color=ink, width=2, seed=0):
        r = random.Random(seed)
        pts = []
        for start, end in zip(points, points[1:]):
            for j in range(8):
                t = j / 8
                pts.append((start[0]*(1-t)+end[0]*t+r.uniform(-1,1)*scale,
                            start[1]*(1-t)+end[1]*t+r.uniform(-1,1)*scale))
        pts.append(points[-1])
        draw.line(pts, fill=color, width=max(1,round(width*scale)), joint="curve")
    def box(draw, rect, seed, color=ink):
        x1,y1,x2,y2=rect
        points=[(x1,y1),(x2,y1),(x2,y2),(x1,y2),(x1,y1)]
        line(draw, points, color, 2.5, seed)
        line(draw, [(x1+2*scale,y1+2*scale),(x2-2*scale,y1+2*scale)], color, 1, seed+99)
    def text(draw, value, center, ft, maxwidth, color=ink):
        # Split at character boundaries so Chinese and unbroken English both fit.
        lines=[]
        for para in value.split("\n"):
            current=""
            for ch in para:
                if current and draw.textlength(current+ch, font=ft)>maxwidth:
                    lines.append(current); current=ch
                else: current+=ch
            lines.append(current)
        maxlines=3
        if len(lines)>maxlines:
            lines=lines[:maxlines]; lines[-1]=lines[-1][:-1]+"…"
        textvalue="\n".join(lines)
        try:
            draw.multiline_text(center, textvalue, font=ft, fill=color, anchor="mm", align="center", spacing=max(1,int(4*scale)))
        except UnicodeEncodeError:
            draw.multiline_text(center, textvalue.encode("ascii", "replace").decode(), font=ft, fill=color, anchor="mm", align="center")
    def arrow(draw, start, end, seed):
        line(draw,[start,end],ink,2,seed)
        a=math.atan2(end[1]-start[1],end[0]-start[0]); size=9*scale
        for angle in (a+2.55,a-2.55):
            line(draw,[end,(end[0]+size*math.cos(angle),end[1]+size*math.sin(angle))],ink,2,seed+1)
    frames=[]
    for frame in range(count):
        im=paper.copy(); d=ImageDraw.Draw(im)
        text(d,data.get("title", ""),xy(400,46),titlefont,w*.88)
        text(d,data.get("subtitle", ""),xy(400,87),smallfont,w*.88)
        phase=frame/count
        if scene == "grid":
            cols=3; rows=math.ceil(len(labels)/cols)
            cellw,cellh=180,110
            for i,label in enumerate(labels):
                col,row=i%cols,i//cols
                left=400-cols*cellw/2+col*cellw+8; top=133+(2-rows)*55+row*cellh
                a=xy(left,top); b=xy(left+164,top+93)
                if i == int(phase*len(labels)):
                    d.rounded_rectangle((*a,*b),radius=max(2,int(8*scale)),fill=pale)
                box(d,(*a,*b),i+1)
                text(d,label,xy(left+82,top+46),textfont,145*w/800)
        elif scene == "parallel":
            n=len(labels); gap=15; cellw=min(205,(680-gap*(n-1))/n); total=n*cellw+(n-1)*gap
            for i,label in enumerate(labels):
                left=400-total/2+i*(cellw+gap); top=174
                a=xy(left,top); b=xy(left+cellw,top+125)
                d.rounded_rectangle((*a,*b),radius=max(2,int(8*scale)),fill=pale if (phase+i/n)%1 < .45 else "#f3e6d4")
                box(d,(*a,*b),i+10)
                text(d,label,xy(left+cellw/2,top+46),textfont,(cellw-18)*w/800)
                progress=(phase+i/n)%1
                line(d,[xy(left+15,top+100),xy(left+15+(cellw-30)*progress,top+100)],accent,4,i+20)
        else:
            n=len(labels); gap=25; cellw=min(165,(700-gap*(n-1))/n); total=n*cellw+(n-1)*gap
            for i,label in enumerate(labels):
                left=400-total/2+i*(cellw+gap); top=180
                a=xy(left,top); b=xy(left+cellw,top+85)
                d.rounded_rectangle((*a,*b),radius=max(2,int(8*scale)),fill=pale if i==int(phase*n) else "#f3e6d4")
                box(d,(*a,*b),i+30)
                text(d,label,xy(left+cellw/2,top+42),textfont,(cellw-12)*w/800)
                if i<n-1: arrow(d,xy(left+cellw+3,top+42),xy(left+cellw+gap-3,top+42),i+40)
        frames.append(im)
    return frames


def main():
    parser=argparse.ArgumentParser(description="Render a looping hand-drawn explainer GIF from JSON. Use scene or scenes; each scene has scene (grid, parallel, flow), title, subtitle and labels. Shared options: width, height, frames, duration and font.")
    parser.add_argument("input", help="UTF-8 JSON input path")
    parser.add_argument("output", help="GIF output path")
    parser.add_argument("--font", help="font file path; overrides JSON font")
    args=parser.parse_args()
    try:
        with open(args.input, encoding="utf-8") as f: data=json.load(f)
        if not isinstance(data, dict):
            raise ValueError("JSON root must be an object")
        if "scenes" in data:
            shared_keys = {"width", "height", "frames", "duration", "font"}
            extra = set(data) - shared_keys - {"scenes"}
            if extra:
                raise ValueError("unknown shared fields: " + ", ".join(sorted(extra)))
            if not isinstance(data["scenes"], list) or not 1 <= len(data["scenes"]) <= 12:
                raise ValueError("scenes must contain 1–12 scene objects")
            shared = {k: v for k, v in data.items() if k in shared_keys}
            scenes = []
            for item in data["scenes"]:
                if not isinstance(item, dict) or set(item) - {"scene", "title", "subtitle", "labels"}:
                    raise ValueError("each scene must contain only scene, title, subtitle and labels")
                scenes.append({**shared, **item})
        else:
            scenes = [data]
        scene_labels = [validate(scene) for scene in scenes]
        total_pixels = sum(s.get("width", 800) * s.get("height", 450) * s.get("frames", 16) for s in scenes)
        if total_pixels > 65_000_000:
            raise ValueError("animation exceeds 65 million frame-pixels; reduce dimensions, frames or scenes")
        path=choose_font(args.font or data.get("font"))
        frames=[]
        for scene, labels in zip(scenes, scene_labels):
            frames.extend(render(scene, labels, path))
        # Exclusive creation protects existing files from accidental overwrite.
        with open(args.output,"xb") as out:
            frames[0].save(out, format="GIF", save_all=True, append_images=frames[1:], duration=data.get("duration",100), loop=0, optimize=True, disposal=2)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())

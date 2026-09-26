"""Render a looping demo of the fourteen authored god constellations.

Run with /usr/bin/python3 scripts/generate-constellation-demo.py from the
frontend directory. Requires the system Pillow and rsvg-convert packages.
"""

import io
import json
import math
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "public/assets/god-ghosts/constellation-demo.gif"
SIZE = 480
ART_SIZE = 410
ART_LEFT = (SIZE - ART_SIZE) // 2
ART_TOP = 12
FRAMES_PER_GOD = 60
FRAME_MS = 100

NAMES = {
    "tuvi": "TỬ VI  ·  ZEUS",
    "thienphu": "THIÊN PHỦ  ·  HERA",
    "thatsat": "THẤT SÁT  ·  ARES",
    "phaquan": "PHÁ QUÂN  ·  PROMETHEUS",
    "thamlang": "THAM LANG  ·  APHRODITE",
    "thaiduong": "THÁI DƯƠNG  ·  APOLLO",
    "thaiam": "THÁI ÂM  ·  ARTEMIS",
    "vukhuc": "VŨ KHÚC  ·  HERMES",
    "liemtrinh": "LIÊM TRINH  ·  NEMESIS",
    "thienco": "THIÊN CƠ  ·  ATHENA",
    "thienluong": "THIÊN LƯƠNG  ·  DEMETER",
    "thientuong": "THIÊN TƯỚNG  ·  HADES",
    "thiendong": "THIÊN ĐỒNG  ·  DIONYSUS",
    "cumon": "CỰ MÔN  ·  IRIS",
}

# Read the same TypeScript records as the UI, so future landmark edits are
# picked up when this demo is regenerated.
NODE_EXPORT = r"""
const fs = require('fs');
const ts = require('typescript');
const vm = require('vm');
function read(name, exportName) {
  const source = fs.readFileSync(`src/content/${name}.ts`, 'utf8');
  const js = ts.transpileModule(source, {
    compilerOptions: { module: ts.ModuleKind.CommonJS }
  }).outputText;
  const module = { exports: {} };
  vm.runInNewContext(js, { module, exports: module.exports });
  return module.exports[exportName];
}
const shapes = read('god-landmark-constellations', 'GOD_LANDMARK_CONSTELLATIONS');
const schedule = read('../features/an-sao/constellation-wave', 'constellationWaveSchedule');
const starPulseCycleMs = read('../features/an-sao/constellation-wave', 'STAR_PULSE_CYCLE_MS');
const starPulsePhases = read('../features/an-sao/constellation-wave', 'constellationStarPulsePhases');
process.stdout.write(JSON.stringify({
  ghosts: read('god-ghosts', 'GOD_GHOSTS'),
  shapes,
  wave: read('../features/an-sao/constellation-wave', 'CONSTELLATION_WAVE'),
  starPulseCycleMs,
  schedules: Object.fromEntries(Object.entries(shapes).map(([key, shape]) => [key, schedule(shape)])),
  pulsePhases: Object.fromEntries(Object.entries(shapes).map(([key, shape]) => [key, starPulsePhases(key, shape.points.length)]))
}));
"""


def load_content():
    raw = subprocess.check_output(["node", "-e", NODE_EXPORT], cwd=ROOT)
    content = json.loads(raw)
    assert list(content["ghosts"]) == list(NAMES)
    assert set(content["shapes"]) == set(NAMES)
    return content


def portrait(path):
    png = subprocess.check_output(
        ["rsvg-convert", "--height", str(ART_SIZE), str(ROOT / "public" / path.lstrip("/"))]
    )
    image = Image.open(io.BytesIO(png)).convert("RGBA")
    image.thumbnail((ART_SIZE, ART_SIZE), Image.Resampling.LANCZOS)
    image.putalpha(image.getchannel("A").point(lambda a: round(a * 0.52)))
    return image


def background():
    image = Image.new("RGBA", (SIZE, SIZE), "#070b20")
    aura = Image.new("RGBA", image.size)
    ImageDraw.Draw(aura).ellipse((68, 12, 412, 385), fill=(49, 62, 121, 80))
    image.alpha_composite(aura.filter(ImageFilter.GaussianBlur(70)))
    return image


def position(point):
    return (ART_LEFT + point[0] * ART_SIZE / 100, ART_TOP + point[1] * ART_SIZE / 100)


def render_frame(base, shape, schedule, wave, pulse_cycle_ms, pulse_phases, name, number, total,
                 frame, font, small_font):
    time = frame * FRAME_MS
    wave_time = time % wave["cycleMs"]
    image = base.copy()
    lines = Image.new("RGBA", image.size)
    line_draw = ImageDraw.Draw(lines)
    points = shape["points"]
    for index, (start, end) in enumerate(schedule["lineDirections"]):
        elapsed = wave_time - schedule["lineDelays"][index]
        if elapsed < 0 or elapsed > wave["linkTravelMs"]:
            continue
        draw_ms = wave["linkTravelMs"] * 0.45
        hold_ms = wave["linkTravelMs"] * 0.1
        if elapsed < draw_ms:
            progress = elapsed / draw_ms
            progress = progress * progress * (3 - 2 * progress)
            start_progress, end_progress = 0, progress
        elif elapsed < draw_ms + hold_ms:
            start_progress, end_progress = 0, 1
        else:
            progress = min(1, (elapsed - draw_ms - hold_ms) / draw_ms)
            start_progress = progress * progress * (3 - 2 * progress)
            end_progress = 1
        x1, y1 = position(points[start])
        x2, y2 = position(points[end])
        line_draw.line((x1 + (x2 - x1) * start_progress,
                        y1 + (y2 - y1) * start_progress,
                        x1 + (x2 - x1) * end_progress,
                        y1 + (y2 - y1) * end_progress),
                       fill=(229, 219, 188, 166), width=2)
    image.alpha_composite(lines)

    halos = Image.new("RGBA", image.size)
    halo_draw = ImageDraw.Draw(halos)
    cores = Image.new("RGBA", image.size)
    core_draw = ImageDraw.Draw(cores)
    for index, point in enumerate(points):
        pulse = (1 - math.cos(2 * math.pi * ((time + pulse_phases[index]) / pulse_cycle_ms))) / 2
        x, y = position(point)
        power = point[2] if len(point) > 2 else 1
        radius = 7.4 * power
        halo_draw.ellipse((x - radius, y - radius, x + radius, y + radius),
                          fill=(232, 199, 118, round(255 * (0.04 + 0.88 * pulse))))
        core_radius = 2.8 * power
        core_draw.ellipse((x - core_radius - 0.8, y - core_radius - 0.8,
                           x + core_radius + 0.8, y + core_radius + 0.8),
                          fill=(218, 176, 93, round(255 * (0.16 + 0.84 * pulse))))
        core_draw.ellipse((x - core_radius, y - core_radius,
                           x + core_radius, y + core_radius),
                          fill=(255, 253, 237, round(255 * (0.16 + 0.84 * pulse))))
    image.alpha_composite(halos.filter(ImageFilter.GaussianBlur(5)))
    image.alpha_composite(cores)

    draw = ImageDraw.Draw(image)
    bounds = draw.textbbox((0, 0), name, font=font)
    draw.text(((SIZE - (bounds[2] - bounds[0])) / 2, 430), name,
              fill=(245, 235, 211), font=font)
    count = f"{number:02d} / {total:02d}"
    bounds = draw.textbbox((0, 0), count, font=small_font)
    draw.text(((SIZE - (bounds[2] - bounds[0])) / 2, 456), count,
              fill=(172, 163, 147), font=small_font)

    # A short dip at each cut makes the loop read as separate reveals.
    fade = min(1, (frame + 1) / 2, (FRAMES_PER_GOD - frame) / 2)
    if fade < 1:
        image = Image.blend(background(), image, fade)
    return image.convert("RGB").quantize(colors=128, method=Image.Quantize.FASTOCTREE)


def main():
    content = load_content()
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    font = ImageFont.truetype(font_path, 17)
    small_font = ImageFont.truetype(font_path, 11)
    backdrop = background()
    frames = []
    for number, key in enumerate(NAMES, 1):
        base = backdrop.copy()
        art = portrait(content["ghosts"][key])
        base.alpha_composite(art, (ART_LEFT + (ART_SIZE - art.width) // 2,
                                   ART_TOP + (ART_SIZE - art.height) // 2))
        shape = content["shapes"][key]
        schedule = content["schedules"][key]
        pulse_phases = content["pulsePhases"][key]
        for frame in range(FRAMES_PER_GOD):
            frames.append(render_frame(base, shape, schedule, content["wave"],
                                       content["starPulseCycleMs"], pulse_phases, NAMES[key],
                                       number, len(NAMES), frame, font, small_font))
        print(f"Rendered {number:02d}/{len(NAMES)}: {key}")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(OUTPUT, save_all=True, append_images=frames[1:],
                   duration=FRAME_MS, loop=0, optimize=True, disposal=2)
    print(f"Saved {OUTPUT}")


if __name__ == "__main__":
    main()

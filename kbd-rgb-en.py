import os
import sys
import json
import time
import math
import random
import signal
import subprocess
import threading
import tempfile
import colorsys
from pathlib import Path

LED_PATH = "/sys/class/leds/rgb:kbd_backlight/multi_intensity"
CONFIG_DIR = Path.home() / ".config" / "kbd-rgb"
CONFIG_FILE = CONFIG_DIR / "config.json"
PROFILES_FILE = CONFIG_DIR / "profiles.json"
SERVICE_DIR = Path.home() / ".config" / "systemd" / "user"

current_effect_thread = None
stop_event = threading.Event()

BOLD    = "\033[1m"
DIM     = "\033[2m"
RED     = "\033[91m"
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
BLUE    = "\033[94m"
MAGENTA = "\033[95m"
CYAN    = "\033[96m"
WHITE   = "\033[97m"
RESET   = "\033[0m"
CLEAR   = "\033[2J\033[H"


def colored(text, *codes):
    return "".join(codes) + str(text) + RESET


def write_color(r, g, b):
    r = max(0, min(255, int(r)))
    g = max(0, min(255, int(g)))
    b = max(0, min(255, int(b)))
    try:
        with open(LED_PATH, "w") as fh:
            fh.write(f"{r} {g} {b}\n")
    except PermissionError:
        subprocess.run(
            ["sudo", "tee", LED_PATH],
            input=f"{r} {g} {b}\n",
            text=True,
            capture_output=True,
        )
    except Exception:
        subprocess.run(
            f'echo "{r} {g} {b}" | sudo tee {LED_PATH}',
            shell=True,
            capture_output=True,
        )


def set_brightness(percent):
    percent = max(0, min(100, int(percent)))
    subprocess.run(
        ["brightnessctl", "-d", "rgb:kbd_backlight", "set", f"{percent}%"],
        capture_output=True,
    )


def hsv_to_rgb(h, s, v):
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return int(r * 255), int(g * 255), int(b * 255)


def lerp(a, b, t):
    return a + (b - a) * t


def check_dependencies():
    missing = []
    for dep in ["brightnessctl", "cava"]:
        result = subprocess.run(["which", dep], capture_output=True)
        if result.returncode != 0:
            missing.append(dep)
    return missing


def effect_static(color=(0, 0, 255), **kw):
    write_color(*color)
    stop_event.wait()


def effect_breathing(color=(0, 0, 255), speed=0.05, **kw):
    phase = 0.0
    while not stop_event.is_set():
        t = (math.sin(phase) + 1.0) / 2.0
        write_color(int(color[0] * t), int(color[1] * t), int(color[2] * t))
        phase += speed * 0.5
        stop_event.wait(0.02)


def effect_wave(speed=0.05, **kw):
    hue = 0.0
    while not stop_event.is_set():
        hue = (hue + speed * 0.1) % 1.0
        write_color(*hsv_to_rgb(hue, 1.0, 1.0))
        stop_event.wait(0.02)


def effect_reactive(color=(255, 255, 255), speed=0.05, **kw):
    while not stop_event.is_set():
        for i in range(20):
            if stop_event.is_set():
                return
            t = 1.0 - (i / 20.0)
            write_color(int(color[0] * t), int(color[1] * t), int(color[2] * t))
            stop_event.wait(speed * 0.8)
        stop_event.wait(speed * 4)


def effect_cycle(speed=0.05, **kw):
    hue = 0.0
    while not stop_event.is_set():
        hue = (hue + speed * 0.05) % 1.0
        write_color(*hsv_to_rgb(hue, 1.0, 1.0))
        stop_event.wait(0.02)


def effect_ripple(color=(0, 150, 255), speed=0.05, **kw):
    phase = 0.0
    while not stop_event.is_set():
        t = abs(math.sin(phase))
        write_color(int(color[0] * t), int(color[1] * t), int(color[2] * t))
        phase += speed * 0.3
        stop_event.wait(0.02)


def effect_rain(speed=0.05, **kw):
    rain_palette = [
        (0, 80, 200),
        (0, 120, 255),
        (50, 180, 255),
        (100, 220, 255),
        (0, 50, 150),
    ]
    idx = 0
    while not stop_event.is_set():
        c = rain_palette[idx % len(rain_palette)]
        for step in range(15):
            if stop_event.is_set():
                return
            t = step / 15.0
            write_color(int(c[0] * t), int(c[1] * t), int(c[2] * t))
            stop_event.wait(speed * 0.5)
        for step in range(15, -1, -1):
            if stop_event.is_set():
                return
            t = step / 15.0
            write_color(int(c[0] * t), int(c[1] * t), int(c[2] * t))
            stop_event.wait(speed * 0.5)
        idx += 1
        stop_event.wait(random.uniform(speed, speed * 3))


def effect_snake(speed=0.05, **kw):
    palette = [
        (255, 0, 0),
        (255, 120, 0),
        (255, 255, 0),
        (0, 255, 0),
        (0, 180, 255),
        (80, 0, 255),
        (200, 0, 255),
    ]
    idx = 0
    while not stop_event.is_set():
        c = palette[idx % len(palette)]
        write_color(*c)
        idx += 1
        stop_event.wait(speed * 3)


def effect_starlight(speed=0.05, **kw):
    while not stop_event.is_set():
        hue = random.random()
        r, g, b = hsv_to_rgb(hue, 0.3, 1.0)
        for step in range(10):
            if stop_event.is_set():
                return
            t = step / 10.0
            write_color(int(r * t), int(g * t), int(b * t))
            stop_event.wait(speed * 0.5)
        stop_event.wait(random.uniform(speed * 2, speed * 6))
        for step in range(10, -1, -1):
            if stop_event.is_set():
                return
            t = step / 10.0
            write_color(int(r * t), int(g * t), int(b * t))
            stop_event.wait(speed * 0.3)


def effect_radar(speed=0.05, **kw):
    angle = 0.0
    while not stop_event.is_set():
        angle = (angle + speed * 0.4) % (2 * math.pi)
        val = (math.sin(angle * 3) + 1.0) / 2.0
        r, g, b = hsv_to_rgb(0.33, 1.0, val)
        write_color(r, g, b)
        stop_event.wait(0.02)


def effect_vortex(speed=0.05, **kw):
    angle = 0.0
    while not stop_event.is_set():
        angle = (angle + speed * 0.5) % (2 * math.pi)
        hue = angle / (2 * math.pi)
        sat = 0.7 + 0.3 * math.sin(angle * 2)
        r, g, b = hsv_to_rgb(hue, sat, 1.0)
        write_color(r, g, b)
        stop_event.wait(0.02)


def effect_heartbeat(color=(255, 0, 0), **kw):
    pattern = [0.0, 0.9, 0.3, 0.0, 1.0, 0.4, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    delays  = [0.08, 0.08, 0.1, 0.08, 0.08, 0.12, 0.1, 0.1, 0.1, 0.1, 0.3, 0.4]
    while not stop_event.is_set():
        for t, d in zip(pattern, delays):
            if stop_event.is_set():
                return
            write_color(int(color[0] * t), int(color[1] * t), int(color[2] * t))
            stop_event.wait(d)


def effect_fireworks(speed=0.05, **kw):
    while not stop_event.is_set():
        hue = random.random()
        r, g, b = hsv_to_rgb(hue, 1.0, 1.0)
        for step in range(15):
            if stop_event.is_set():
                return
            t = step / 15.0
            write_color(int(r * t), int(g * t), int(b * t))
            stop_event.wait(speed * 0.4)
        for step in range(15, -1, -1):
            if stop_event.is_set():
                return
            t = step / 15.0
            write_color(int(r * t), int(g * t), int(b * t))
            stop_event.wait(speed * 0.6)
        write_color(0, 0, 0)
        stop_event.wait(random.uniform(speed * 2, speed * 5))


def effect_sine_wave(color=(0, 100, 255), speed=0.05, **kw):
    phase = 0.0
    while not stop_event.is_set():
        t = (math.sin(phase) + 1.0) / 2.0
        write_color(int(color[0] * t), int(color[1] * t), int(color[2] * t))
        phase += speed * 0.4
        stop_event.wait(0.02)


def effect_neon(speed=0.05, **kw):
    neon = [
        (255, 0, 255),
        (0, 255, 255),
        (255, 255, 0),
        (255, 0, 128),
        (128, 0, 255),
        (0, 255, 128),
    ]
    idx = 0
    while not stop_event.is_set():
        c = neon[idx % len(neon)]
        for step in range(25):
            if stop_event.is_set():
                return
            t = step / 25.0
            write_color(int(c[0] * t), int(c[1] * t), int(c[2] * t))
            stop_event.wait(speed * 0.5)
        stop_event.wait(speed * 2)
        for step in range(25, -1, -1):
            if stop_event.is_set():
                return
            t = step / 25.0
            write_color(int(c[0] * t), int(c[1] * t), int(c[2] * t))
            stop_event.wait(speed * 0.5)
        idx += 1


def effect_screen_sync(speed=0.05, **kw):
    try:
        from PIL import Image
    except ImportError:
        write_color(255, 60, 0)
        stop_event.wait()
        return

    capture_path = "/tmp/kbd_rgb_scr.png"

    while not stop_event.is_set():
        captured = False
        for cmd in [
            ["scrot", "-o", capture_path],
            ["grim", capture_path],
            ["import", "-window", "root", capture_path],
            ["ffmpeg", "-y", "-f", "x11grab", "-video_size", "1x1", "-i", ":0.0", "-vframes", "1", capture_path],
        ]:
            try:
                res = subprocess.run(cmd, capture_output=True, timeout=2)
                if res.returncode == 0:
                    captured = True
                    break
            except Exception:
                continue

        if captured:
            try:
                from PIL import ImageStat
                img = Image.open(capture_path).convert("RGB")
                img = img.resize((64, 64), Image.LANCZOS)
                stat = ImageStat.Stat(img)
                avg_r, avg_g, avg_b = (int(v) for v in stat.mean[:3])
                write_color(avg_r, avg_g, avg_b)
            except Exception:
                pass

        stop_event.wait(speed * 2)


def _run_cava_sync(cava_cfg, color1, color2):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".conf", delete=False) as fh:
        fh.write(cava_cfg)
        tmp_cfg = fh.name

    try:
        proc = subprocess.Popen(
            ["cava", "-p", tmp_cfg],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            bufsize=1,
        )
        while not stop_event.is_set():
            line = proc.stdout.readline()
            if not line:
                break
            clean = line.strip().replace("\r", "")
            parts = clean.split(";")
            parts = [p for p in parts if p.strip().isdigit()]
            if len(parts) >= 2:
                try:
                    v1 = int(parts[0])
                    v2 = int(parts[1])
                    level = min(100, max(0, (v1 + v2) // 2))
                    t = level / 100.0
                    r = int(lerp(color1[0], color2[0], t))
                    g = int(lerp(color1[1], color2[1], t))
                    b = int(lerp(color1[2], color2[2], t))
                    write_color(r, g, b)
                except ValueError:
                    pass
    finally:
        try:
            proc.terminate()
            proc.wait(timeout=2)
        except Exception:
            pass
        try:
            os.unlink(tmp_cfg)
        except Exception:
            pass


def effect_music_sync(color=(0, 0, 255), **kw):
    cfg = (
        "[general]\nbars=2\n"
        "[output]\nmethod=raw\ndata_format=ascii\nascii_max_range=100\n"
    )
    _run_cava_sync(cfg, (0, 0, 60), color)


def effect_mic_sync(color=(0, 255, 100), **kw):
    cfg = (
        "[input]\nmethod=pulse\nsource=default\n"
        "[general]\nbars=2\n"
        "[output]\nmethod=raw\ndata_format=ascii\nascii_max_range=100\n"
    )
    _run_cava_sync(cfg, (0, 30, 10), color)


def _read_cpu_temp():
    for hwmon in Path("/sys/class/hwmon").iterdir():
        name_file = hwmon / "name"
        if name_file.exists():
            chip_name = name_file.read_text().strip()
            if chip_name in ("coretemp", "k10temp", "zenpower"):
                for i in range(1, 15):
                    tf = hwmon / f"temp{i}_input"
                    if tf.exists():
                        return float(tf.read_text().strip()) / 1000.0
    for hwmon in Path("/sys/class/hwmon").iterdir():
        for i in range(1, 10):
            tf = hwmon / f"temp{i}_input"
            if tf.exists():
                try:
                    val = float(tf.read_text().strip()) / 1000.0
                    if 0 < val < 120:
                        return val
                except Exception:
                    continue
    return None


def effect_cpu_temp(**kw):
    cold_temp = 35.0
    hot_temp  = 95.0
    while not stop_event.is_set():
        temp = _read_cpu_temp()
        if temp is not None:
            t = max(0.0, min(1.0, (temp - cold_temp) / (hot_temp - cold_temp)))
            r = int(lerp(0,   255, t))
            g = int(lerp(120,   0, t))
            b = int(lerp(255,   0, t))
            write_color(r, g, b)
        stop_event.wait(2.0)


EFFECTS = {
    "static":      effect_static,
    "breathing":   effect_breathing,
    "wave":        effect_wave,
    "reactive":    effect_reactive,
    "cycle":       effect_cycle,
    "ripple":      effect_ripple,
    "rain":        effect_rain,
    "snake":       effect_snake,
    "starlight":   effect_starlight,
    "radar":       effect_radar,
    "vortex":      effect_vortex,
    "heartbeat":   effect_heartbeat,
    "fireworks":   effect_fireworks,
    "sine_wave":   effect_sine_wave,
    "neon":        effect_neon,
    "screen_sync": effect_screen_sync,
    "music_sync":  effect_music_sync,
    "mic_sync":    effect_mic_sync,
    "cpu_temp":    effect_cpu_temp,
}

EFFECT_DISPLAY = [
    ("Static",                   "static"),
    ("Breathing",               "breathing"),
    ("Wave",                    "wave"),
    ("Reactive",                "reactive"),
    ("Cycle",                   "cycle"),
    ("Ripple",                  "ripple"),
    ("Rain",                    "rain"),
    ("Snake",                   "snake"),
    ("Starlight",               "starlight"),
    ("Radar",                    "radar"),
    ("Vortex",                  "vortex"),
    ("Heartbeat",               "heartbeat"),
    ("Fireworks",               "fireworks"),
    ("Sine Wave",               "sine_wave"),
    ("Neon",                     "neon"),
    ("Screen Sync",             "screen_sync"),
    ("Music Sync",              "music_sync"),
    ("Mic Sync",                "mic_sync"),
    ("CPU Temperature Tracker", "cpu_temp"),
]

COLOR_PRESETS = {
    "Red":    [255, 0,   0  ],
    "Green":  [0,   255, 0  ],
    "Blue":   [0,   0,   255],
    "White":  [255, 255, 255],
    "Yellow": [255, 220, 0  ],
    "Purple": [140, 0,   255],
    "Cyan":   [0,   220, 255],
    "Orange": [255, 110, 0  ],
    "Pink":   [255, 0,   140],
    "Coral":  [255, 60,  60 ],
}


def stop_current_effect():
    global current_effect_thread
    stop_event.set()
    if current_effect_thread and current_effect_thread.is_alive():
        current_effect_thread.join(timeout=3)
    stop_event.clear()
    current_effect_thread = None


def start_effect(name, **kwargs):
    global current_effect_thread
    stop_current_effect()
    fn = EFFECTS.get(name)
    if fn is None:
        return False
    current_effect_thread = threading.Thread(target=fn, kwargs=kwargs, daemon=True)
    current_effect_thread.start()
    return True


def load_config():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as fh:
            return json.load(fh)
    return {"effect": "static", "color": [0, 0, 255], "brightness": 100, "speed": 0.05}


def save_config(cfg):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as fh:
        json.dump(cfg, fh, indent=2)


def load_profiles():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if PROFILES_FILE.exists():
        with open(PROFILES_FILE) as fh:
            return json.load(fh)
    return {}


def save_profiles(profiles):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(PROFILES_FILE, "w") as fh:
        json.dump(profiles, fh, indent=2)


def create_systemd_service(effect_name, color, brightness, speed):
    SERVICE_DIR.mkdir(parents=True, exist_ok=True)
    script_path = Path(__file__).resolve()
    svc = (
        "[Unit]\n"
        "Description=Keyboard RGB Effect Service (Monster/Clevo)\n"
        "After=graphical-session.target\n\n"
        "[Service]\n"
        "Type=simple\n"
        f"ExecStart=/usr/bin/python3 {script_path} --daemon"
        f" --effect {effect_name}"
        f" --color {color[0]} {color[1]} {color[2]}"
        f" --brightness {brightness}"
        f" --speed {speed}\n"
        "Restart=on-failure\n"
        "RestartSec=5\n\n"
        "[Install]\n"
        "WantedBy=graphical-session.target\n"
    )
    service_file = SERVICE_DIR / "kbd-rgb.service"
    with open(service_file, "w") as fh:
        fh.write(svc)
    subprocess.run(["systemctl", "--user", "daemon-reload"], capture_output=True)
    return str(service_file)


def print_header():
    print(CLEAR, end="")
    print(colored("╔══════════════════════════════════════════════════════════════╗", CYAN))
    print(colored("║      Monster / Clevo  ·  Keyboard RGB Manager               ║", CYAN, BOLD))
    print(colored("║                      Arch Linux                             ║", CYAN))
    print(colored("╚══════════════════════════════════════════════════════════════╝", CYAN))
    print()


def get_input(prompt, validator=None, default=None):
    while True:
        try:
            raw = input(colored(f"  ► {prompt}: ", CYAN)).strip()
        except (KeyboardInterrupt, EOFError):
            return default
        if not raw and default is not None:
            return default
        if validator is None:
            return raw
        result = validator(raw)
        if result is not None:
            return result


def int_range_validator(lo, hi):
    def v(s):
        try:
            n = int(s)
            if lo <= n <= hi:
                return n
        except ValueError:
            pass
        print(colored(f"  ! Please enter a number between {lo} and {hi}.", RED))
        return None
    return v


def color_input():
    print()
    print(colored("  Color Selection", BOLD, YELLOW))
    print(colored("  " + "─" * 56, DIM))
    names = list(COLOR_PRESETS.keys())
    for i, name in enumerate(names, 1):
        c = COLOR_PRESETS[name]
        swatch = f"\033[48;2;{c[0]};{c[1]};{c[2]}m   \033[0m"
        print(f"  {colored(str(i).rjust(2), GREEN)}. {swatch} {name}")
    print(f"  {colored(str(len(names)+1).rjust(2), GREEN)}. Enter custom RGB value")
    print()
    choice = get_input(f"Choice (1–{len(names)+1})", int_range_validator(1, len(names)+1), 3)
    if choice <= len(names):
        return list(COLOR_PRESETS[names[choice-1]])
    r = get_input("R (0–255)", int_range_validator(0, 255), 0)
    g = get_input("G (0–255)", int_range_validator(0, 255), 0)
    b = get_input("B (0–255)", int_range_validator(0, 255), 255)
    return [r, g, b]


def speed_input(default=5):
    SPEED_MAP = {1: 0.15, 2: 0.10, 3: 0.08, 4: 0.06, 5: 0.05,
                 6: 0.035, 7: 0.025, 8: 0.015, 9: 0.008, 10: 0.004}
    val = get_input("Speed (1=slow … 10=fast)", int_range_validator(1, 10), default)
    return SPEED_MAP[val]


def effects_menu(cfg):
    print_header()
    print(colored("  Effect Selection", BOLD, YELLOW))
    print(colored("  " + "─" * 56, DIM))
    print()
    active = cfg.get("effect", "static")
    for i, (label, key) in enumerate(EFFECT_DISPLAY, 1):
        marker = colored("▶ ", GREEN) if active == key else "  "
        print(f" {marker}{colored(str(i).rjust(2), GREEN)}. {label}")
    print()
    choice = get_input(f"Choice (1–{len(EFFECT_DISPLAY)})", int_range_validator(1, len(EFFECT_DISPLAY)), 1)
    label, key = EFFECT_DISPLAY[choice - 1]
    cfg["effect"] = key

    needs_color = key in {
        "static", "breathing", "reactive", "ripple",
        "heartbeat", "sine_wave", "music_sync", "mic_sync",
    }
    needs_speed = key not in {"static", "cpu_temp", "music_sync", "mic_sync"}

    if needs_color:
        cfg["color"] = color_input()
    if needs_speed:
        print()
        cfg["speed"] = speed_input()

    save_config(cfg)
    kwargs = {"color": tuple(cfg.get("color", [0, 0, 255])), "speed": cfg.get("speed", 0.05)}
    start_effect(key, **kwargs)
    print(colored(f"\n  ✓  {label} effect started.", GREEN))
    input(colored("\n  [Enter] Back to main menu...", DIM))


def brightness_menu(cfg):
    print_header()
    print(colored("  Brightness Settings", BOLD, YELLOW))
    print(colored("  " + "─" * 56, DIM))
    print()
    cur = cfg.get("brightness", 100)
    bar_filled = int(cur / 5)
    bar = "█" * bar_filled + "░" * (20 - bar_filled)
    print(f"  Current: {colored(str(cur) + '%', CYAN)}  [{colored(bar, BLUE)}]")
    print()
    val = get_input("New brightness (0–100)", int_range_validator(0, 100), cur)
    cfg["brightness"] = val
    set_brightness(val)
    save_config(cfg)
    print(colored(f"\n  ✓  Brightness set to {val}%.", GREEN))
    input(colored("\n  [Enter] Back to main menu...", DIM))


def profiles_menu(cfg):
    profiles = load_profiles()
    while True:
        print_header()
        print(colored("  Profile Management", BOLD, YELLOW))
        print(colored("  " + "─" * 56, DIM))
        print()
        items = [
            "Save current settings as profile",
            "Load profile",
            "Delete profile",
            "List all profiles",
            "← Back to main menu",
        ]
        for i, item in enumerate(items, 1):
            print(f"  {colored(str(i), GREEN)}. {item}")
        print()
        choice = get_input("Choice (1–5)", int_range_validator(1, 5), 5)

        if choice == 1:
            name = get_input("Profile name")
            if name:
                profiles[name] = {k: v for k, v in cfg.items()}
                save_profiles(profiles)
                print(colored(f"\n  ✓  Profile '{name}' saved.", GREEN))
            input(colored("  [Enter] continue...", DIM))

        elif choice == 2:
            if not profiles:
                print(colored("\n  ! No saved profiles found.", YELLOW))
                input(colored("  [Enter] continue...", DIM))
                continue
            print()
            pnames = list(profiles.keys())
            for i, pn in enumerate(pnames, 1):
                print(f"  {colored(str(i), GREEN)}. {pn}")
            print()
            pidx = get_input(f"Profile (1–{len(pnames)})", int_range_validator(1, len(pnames)), 1)
            loaded = profiles[pnames[pidx - 1]]
            cfg.update(loaded)
            save_config(cfg)
            kwargs = {"color": tuple(cfg.get("color", [0, 0, 255])), "speed": cfg.get("speed", 0.05)}
            start_effect(cfg.get("effect", "static"), **kwargs)
            set_brightness(cfg.get("brightness", 100))
            print(colored(f"\n  ✓  Profile '{pnames[pidx-1]}' loaded.", GREEN))
            input(colored("  [Enter] continue...", DIM))

        elif choice == 3:
            if not profiles:
                print(colored("\n  ! No saved profiles found.", YELLOW))
                input(colored("  [Enter] continue...", DIM))
                continue
            print()
            pnames = list(profiles.keys())
            for i, pn in enumerate(pnames, 1):
                print(f"  {colored(str(i), GREEN)}. {pn}")
            print()
            pidx = get_input(f"Profile to delete (1–{len(pnames)})", int_range_validator(1, len(pnames)), 1)
            del profiles[pnames[pidx - 1]]
            save_profiles(profiles)
            print(colored(f"\n  ✓  '{pnames[pidx-1]}' deleted.", GREEN))
            input(colored("  [Enter] continue...", DIM))

        elif choice == 4:
            print()
            if not profiles:
                print(colored("  No saved profiles.", YELLOW))
            else:
                for pname, pdata in profiles.items():
                    c = pdata.get("color", [0, 0, 255])
                    swatch = f"\033[48;2;{c[0]};{c[1]};{c[2]}m   \033[0m"
                    eff = pdata.get("effect", "?")
                    br  = pdata.get("brightness", 100)
                    print(f"  {swatch}  {colored(pname, BOLD)}  —  {eff}  @  {br}%")
            print()
            input(colored("  [Enter] continue...", DIM))

        elif choice == 5:
            break


def systemd_menu(cfg):
    print_header()
    print(colored("  Systemd Service Management", BOLD, YELLOW))
    print(colored("  " + "─" * 56, DIM))
    print()
    items = [
        "Create service file (from current settings)",
        "Enable and start service",
        "Stop and disable service",
        "View service status",
        "← Back to main menu",
    ]
    for i, item in enumerate(items, 1):
        print(f"  {colored(str(i), GREEN)}. {item}")
    print()
    choice = get_input("Choice (1–5)", int_range_validator(1, 5), 5)

    if choice == 1:
        sf = create_systemd_service(
            cfg.get("effect", "static"),
            cfg.get("color", [0, 0, 255]),
            cfg.get("brightness", 100),
            cfg.get("speed", 0.05),
        )
        print(colored(f"\n  ✓  Service file created:\n     {sf}", GREEN))

    elif choice == 2:
        r = subprocess.run(
            ["systemctl", "--user", "enable", "--now", "kbd-rgb.service"],
            capture_output=True, text=True,
        )
        if r.returncode == 0:
            print(colored("\n  ✓  Service enabled and started.", GREEN))
        else:
            print(colored(f"\n  ✗  Error: {r.stderr.strip()}", RED))

    elif choice == 3:
        r = subprocess.run(
            ["systemctl", "--user", "disable", "--now", "kbd-rgb.service"],
            capture_output=True, text=True,
        )
        if r.returncode == 0:
            print(colored("\n  ✓  Service stopped and disabled.", GREEN))
        else:
            print(colored(f"\n  ✗  Error: {r.stderr.strip()}", RED))

    elif choice == 4:
        r = subprocess.run(
            ["systemctl", "--user", "status", "kbd-rgb.service"],
            capture_output=True, text=True,
        )
        print()
        print(r.stdout or r.stderr)

    input(colored("\n  [Enter] Back to main menu...", DIM))


def info_menu():
    print_header()
    print(colored("  System Info & Help", BOLD, YELLOW))
    print(colored("  " + "─" * 56, DIM))
    print()

    missing = check_dependencies()
    if missing:
        print(colored(f"  ✗  Missing dependencies: {', '.join(missing)}", RED))
        print(colored(f"  →  sudo pacman -S {' '.join(missing)}", YELLOW))
    else:
        print(colored("  ✓  brightnessctl and cava are installed.", GREEN))

    print()
    led_ok = Path(LED_PATH).exists()
    status_str = colored("✓ Accessible", GREEN) if led_ok else colored("✗ Not found", RED)
    print(f"  LED Path : {colored(LED_PATH, DIM)}")
    print(f"  Status   : {status_str}")

    temp = _read_cpu_temp()
    if temp is not None:
        print(f"  CPU Temp : {colored(f'{temp:.1f} °C', CYAN)}")

    print()
    print(colored("  ─── udev Rule (passwordless access) ─────────────────────", DIM))
    rule = (
        'SUBSYSTEM=="leds", KERNEL=="rgb:kbd_backlight", '
        'RUN+="/bin/chmod a+w /sys/class/leds/rgb:kbd_backlight/multi_intensity"'
    )
    print(f"\n  {colored(rule, YELLOW)}\n")
    print(colored(
        "  sudo tee /etc/udev/rules.d/99-kbd-rgb.rules <<< '" + rule + "'",
        DIM,
    ))
    print(colored(
        "  sudo udevadm control --reload-rules && sudo udevadm trigger",
        DIM,
    ))
    print()
    print(colored(
        "  ─── Screen Sync requires Pillow ──────────────────────────",
        DIM,
    ))
    print(colored("  sudo pacman -S python-pillow scrot", DIM))
    print()
    input(colored("  [Enter] Back to main menu...", DIM))


def daemon_mode(args):
    effect    = "static"
    color     = [0, 0, 255]
    brightness = 100
    speed     = 0.05
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--effect" and i + 1 < len(args):
            effect = args[i + 1]; i += 2
        elif a == "--color" and i + 3 < len(args):
            color = [int(args[i+1]), int(args[i+2]), int(args[i+3])]; i += 4
        elif a == "--brightness" and i + 1 < len(args):
            brightness = int(args[i + 1]); i += 2
        elif a == "--speed" and i + 1 < len(args):
            speed = float(args[i + 1]); i += 2
        else:
            i += 1

    set_brightness(brightness)
    start_effect(effect, color=tuple(color), speed=speed)

    def _shutdown(signum, frame):
        stop_current_effect()
        sys.exit(0)

    signal.signal(signal.SIGTERM, _shutdown)
    signal.signal(signal.SIGINT,  _shutdown)

    while True:
        time.sleep(1)


def main():
    if "--daemon" in sys.argv:
        daemon_mode(sys.argv[sys.argv.index("--daemon") + 1:])
        return

    cfg = load_config()
    start_effect(cfg.get("effect", "static"),
                 color=tuple(cfg.get("color", [0, 0, 255])),
                 speed=cfg.get("speed", 0.05))
    set_brightness(cfg.get("brightness", 100))

    signal.signal(signal.SIGINT, lambda s, f: (stop_current_effect(), sys.exit(0)))

    while True:
        print_header()
        eff = cfg.get("effect", "static")
        br  = cfg.get("brightness", 100)
        c   = cfg.get("color", [0, 0, 255])
        swatch = f"\033[48;2;{c[0]};{c[1]};{c[2]}m   \033[0m"
        bar_f  = int(br / 5)
        bar    = "█" * bar_f + "░" * (20 - bar_f)

        print(f"  Effect     : {colored(eff, CYAN, BOLD)}  {swatch}")
        print(f"  Brightness : {colored(str(br) + '%', CYAN)}  [{colored(bar, BLUE)}]")
        print(colored("  " + "─" * 56, DIM))
        print()

        menu_items = [
            "Select & Start Effect",
            "Adjust Brightness",
            "Profile Management",
            "Systemd Service",
            "System Info & Help",
            "Exit",
        ]
        print(colored("  Main Menu", BOLD, YELLOW))
        print(colored("  " + "─" * 56, DIM))
        for i, item in enumerate(menu_items, 1):
            print(f"  {colored(str(i), GREEN)}. {item}")
        print()

        choice = get_input("Choice (1–6)", int_range_validator(1, 6), 6)

        if choice == 1:
            effects_menu(cfg)
        elif choice == 2:
            brightness_menu(cfg)
        elif choice == 3:
            profiles_menu(cfg)
        elif choice == 4:
            systemd_menu(cfg)
        elif choice == 5:
            info_menu()
        elif choice == 6:
            stop_current_effect()
            print(colored("\n  Goodbye! Keyboard left on last color. ✓\n", GREEN))
            sys.exit(0)


if __name__ == "__main__":
    main()

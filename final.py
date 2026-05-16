import os
import json
import time
import math
import serial
import pi3d

CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "main": 0,
    "cycle": 10,
    "configs": [
        {
            "modelA": "eyeOpen.obj",
            "modelB": "eyeClosed.obj",
            "texture": "eyeTexture.png",
            "sx": 1.0,
            "sy": 1.0,
            "sz": 1.0,
            "x": 0.0,
            "y": 0.0,
            "z": 4.0,
            "motion": 0.0,
            "SENSOR_MIN": 15.0,
            "SENSOR_MAX": 100.0,
            "SMOOTHING": 0.08
        }
    ]
}


def load_config():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        return DEFAULT_CONFIG

    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


def save_config(config_data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config_data, f, indent=4)


config_data = load_config()
main_id = config_data.get("main", 0)
configs = config_data["configs"]
cfg = configs[main_id]

SENSOR_MIN = float(cfg.get("SENSOR_MIN", 15.0))
SENSOR_MAX = float(cfg.get("SENSOR_MAX", 100.0))
SMOOTHING = float(cfg.get("SMOOTHING", 0.08))

BLEND_TIME = 1.0
HOLD_TIME = 5.0

sensor_value = SENSOR_MAX
smoothed_sensor = SENSOR_MAX

morphAmount = 0.0
anim_state = "idle"
anim_start_time = 0.0


DISPLAY = pi3d.Display.create(
    frames_per_second=60,
    background=(0.0, 0.0, 0.0, 1.0)
)

DISPLAY.hide_cursor()

CAMERA = pi3d.Camera()
KEYBOARD = pi3d.Keyboard()

shader = pi3d.Shader("uv_flat")

tex = pi3d.Texture(cfg["texture"])

modelA = pi3d.Model(
    file_string=cfg["modelA"],
    name="modelA",
    x=cfg["x"],
    y=cfg["y"],
    z=cfg["z"],
    sx=cfg["sx"],
    sy=cfg["sy"],
    sz=cfg["sz"]
)

modelB = pi3d.Model(
    file_string=cfg["modelB"],
    name="modelB",
    x=cfg["x"],
    y=cfg["y"],
    z=cfg["z"],
    sx=cfg["sx"],
    sy=cfg["sy"],
    sz=cfg["sz"]
)

modelA.set_draw_details(shader, [tex])
modelB.set_draw_details(shader, [tex])

try:
    ser = serial.Serial("/dev/ttyUSB0", 9600, timeout=0.01)
except Exception as e:
    print("Serial not available:", e)
    ser = None


def read_sensor():
    global sensor_value

    if ser is None:
        return sensor_value

    try:
        line = ser.readline().decode("utf-8").strip()
        if line:
            sensor_value = float(line)
    except Exception:
        pass

    return sensor_value


def update_animation(sensor):
    global morphAmount
    global anim_state
    global anim_start_time

    now = time.time()

    if anim_state == "idle":
        morphAmount = 0.0

        if sensor < SENSOR_MIN:
            anim_state = "blend_to_closed"
            anim_start_time = now

    elif anim_state == "blend_to_closed":
        t = min((now - anim_start_time) / BLEND_TIME, 1.0)
        morphAmount = t

        if t >= 1.0:
            morphAmount = 1.0
            anim_state = "hold_closed"
            anim_start_time = now

    elif anim_state == "hold_closed":
        morphAmount = 1.0

        if now - anim_start_time >= HOLD_TIME:
            anim_state = "blend_to_open"
            anim_start_time = now

    elif anim_state == "blend_to_open":
        t = min((now - anim_start_time) / BLEND_TIME, 1.0)
        morphAmount = 1.0 - t

        if t >= 1.0:
            morphAmount = 0.0
            anim_state = "idle"


def apply_transform():
    modelA.position(cfg["x"], cfg["y"], cfg["z"])
    modelB.position(cfg["x"], cfg["y"], cfg["z"])

    modelA.scale(cfg["sx"], cfg["sy"], cfg["sz"])
    modelB.scale(cfg["sx"], cfg["sy"], cfg["sz"])


while DISPLAY.loop_running():
    raw_sensor = read_sensor()

    smoothed_sensor += (raw_sensor - smoothed_sensor) * SMOOTHING

    update_animation(smoothed_sensor)

    apply_transform()

    motion = float(cfg.get("motion", 0.0))
    if motion != 0.0:
        rot = time.time() * motion
        modelA.rotateToY(rot)
        modelB.rotateToY(rot)

    # Draw both models.
    # modelA fades out as modelB fades in.
    modelA.set_alpha(1.0 - morphAmount)
    modelB.set_alpha(morphAmount)

    modelA.draw()
    modelB.draw()

    key = KEYBOARD.read()

    if key == 27:  # ESC
        break

    elif key == 10 or key == 13:  # ENTER
        configs[main_id] = cfg
        config_data["main"] = main_id
        save_config(config_data)
        print("Config saved")

    elif key == ord("w"):
        cfg["y"] += 0.05
    elif key == ord("s"):
        cfg["y"] -= 0.05
    elif key == ord("a"):
        cfg["x"] -= 0.05
    elif key == ord("d"):
        cfg["x"] += 0.05
    elif key == ord("q"):
        cfg["z"] += 0.05
    elif key == ord("e"):
        cfg["z"] -= 0.05

    elif key == ord("+") or key == ord("="):
        cfg["sx"] += 0.05
        cfg["sy"] += 0.05
        cfg["sz"] += 0.05

    elif key == ord("-"):
        cfg["sx"] -= 0.05
        cfg["sy"] -= 0.05
        cfg["sz"] -= 0.05

    elif key == ord("n"):
        main_id = (main_id + 1) % len(configs)
        cfg = configs[main_id]
        SENSOR_MIN = float(cfg.get("SENSOR_MIN", 15.0))
        SENSOR_MAX = float(cfg.get("SENSOR_MAX", 100.0))
        SMOOTHING = float(cfg.get("SMOOTHING", 0.08))
        print("Loaded config:", main_id)

KEYBOARD.close()
DISPLAY.destroy()
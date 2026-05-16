import time
import math
import json
import serial
import pi3d
import os

CONFIG_FILE = "config.json"
SERIAL_PORT = "/dev/ttyUSB0"
BAUDRATE = 115200


# --------------------------------------------------
# LOAD / SAVE CONFIG
# --------------------------------------------------

def load_config_file():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


config_data = load_config_file()
main_id = config_data["main"]
config = config_data["configs"][main_id]

cycle_seconds = config_data.get("cycle", 0)
last_cycle_time = time.time()


def apply_config(new_main_id):
    global cycle_seconds
    global main_id, config
    global OBJ_A, OBJ_B, TEXTURE
    global pos_x, pos_y, pos_z
    global scale_x, scale_y, scale_z
    global motion
    global SENSOR_MIN, SENSOR_MAX, SMOOTHING
    global texture, modelA, modelB
    global inputSensorValue, morphAmount

    main_id = new_main_id
    config_data["main"] = main_id
    config = config_data["configs"][main_id]
    cycle_seconds = config_data.get("cycle", 0)

    OBJ_A = config["modelA"]
    OBJ_B = config["modelB"]
    TEXTURE = config["texture"]

    pos_x = config["x"]
    pos_y = config["y"]
    pos_z = config["z"]

    scale_x = config["sx"]
    scale_y = config["sy"]
    scale_z = config["sz"]

    motion = config["motion"]

    SENSOR_MIN = config["sensorMin"]
    SENSOR_MAX = config["sensorMax"]
    SMOOTHING = config["smoothing"]

    texture = pi3d.Texture(TEXTURE, mipmap=False)

    modelA = pi3d.Model(
        file_string=OBJ_A,
        x=pos_x,
        y=pos_y,
        z=pos_z,
        sx=scale_x,
        sy=scale_y,
        sz=scale_z
    )

    modelB = pi3d.Model(file_string=OBJ_B)

    modelA.set_shader(shader)
    modelA.set_draw_details(shader, [texture])
    modelA.set_material((1.0, 1.0, 1.0))

    print("")
    print("Using config:", main_id)
    print("modelA:", OBJ_A)
    print("modelB:", OBJ_B)
    print("texture:", TEXTURE)
    print("buffers A:", len(modelA.buf))
    print("buffers B:", len(modelB.buf))

    if len(modelA.buf) != len(modelB.buf):
        raise ValueError("OBJ files must have same number of mesh buffers")

    for i, (bufA, bufB) in enumerate(zip(modelA.buf, modelB.buf)):
        print("buffer", i)
        print("verts A:", len(bufA.array_buffer))
        print("verts B:", len(bufB.array_buffer))

        if len(bufA.array_buffer) != len(bufB.array_buffer):
            raise ValueError("OBJ files must have identical topology")

        positionB = bufB.array_buffer[:, 0:3].copy()
        bufA.array_buffer[:, 3:6] = positionB
        bufA._loaded_opengl = False

    inputSensorValue = 0.0
    morphAmount = 0.0


def save_current_config():
    current_config = config_data["configs"][main_id]

    current_config["x"] = pos_x
    current_config["y"] = pos_y
    current_config["z"] = pos_z

    current_config["sx"] = scale_x
    current_config["sy"] = scale_y
    current_config["sz"] = scale_z

    current_config["motion"] = motion

    current_config["sensorMin"] = SENSOR_MIN
    current_config["sensorMax"] = SENSOR_MAX
    current_config["smoothing"] = SMOOTHING

    config_data["main"] = main_id

    with open(CONFIG_FILE, "w") as f:
        json.dump(config_data, f, indent=4)

    print("Saved selected config:", main_id)


def load_next_config(auto=False):
	if not auto:
		save_current_config()

    total = len(config_data["configs"])
    next_id = (main_id + 1) % total

    config_data["main"] = next_id

    with open(CONFIG_FILE, "w") as f:
        json.dump(config_data, f, indent=4)

    apply_config(next_id)

    print("Switched to config:", next_id)


# --------------------------------------------------
# DISPLAY
# --------------------------------------------------

DISPLAY = pi3d.Display.create(
    frames_per_second=60,
    background=(0.0, 0.0, 0.0, 1.0)
)

os.system("unclutter -idle 0 &")
DISPLAY.mouse = False

CAMERA = pi3d.Camera()


# --------------------------------------------------
# SHADERS
# --------------------------------------------------

VERT_SHADER = """
#ifdef GL_ES
precision mediump float;
#endif

attribute vec3 vertex;
attribute vec3 normal;
attribute vec2 texcoord;

uniform mat4 modelviewmatrix[2];
uniform vec3 unif[20];

varying vec2 uv;

void main(void) {
    float morphAmount = unif[16].x;

    vec3 positionA = vertex;
    vec3 positionB = normal;

    vec3 pos = mix(positionA, positionB, morphAmount);

    gl_Position = modelviewmatrix[1] * modelviewmatrix[0] * vec4(pos, 1.0);
    uv = texcoord;
}
"""

FRAG_SHADER = """
#ifdef GL_ES
precision mediump float;
#endif

uniform sampler2D tex0;
varying vec2 uv;

void main(void) {
    gl_FragColor = texture2D(tex0, uv);
}
"""

shader = pi3d.Shader(
    vshader_source=VERT_SHADER,
    fshader_source=FRAG_SHADER
)


# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def remap_sensor(v):
    v = clamp(v, SENSOR_MIN, SENSOR_MAX)
    return (v - SENSOR_MIN) / (SENSOR_MAX - SENSOR_MIN)


# --------------------------------------------------
# INITIAL MODEL LOAD
# --------------------------------------------------

texture = None
modelA = None
modelB = None

inputSensorValue = 0.0
morphAmount = 0.0

apply_config(main_id)


# --------------------------------------------------
# INPUT
# --------------------------------------------------

keys = pi3d.Keyboard()

ser = serial.Serial(
    SERIAL_PORT,
    baudrate=BAUDRATE,
    timeout=0
)

serial_buffer = ""


# --------------------------------------------------
# STATE
# --------------------------------------------------

start_time = time.time()
global_scale = 1.0


# --------------------------------------------------
# MAIN LOOP
# --------------------------------------------------

try:
    while DISPLAY.loop_running():
        t = time.time() - start_time

        # ------------------------------------------
        # SERIAL INPUT
        # ------------------------------------------

        data = ser.read(128).decode("utf-8", errors="ignore")

        if data:
            serial_buffer += data

            while "\n" in serial_buffer:
                line, serial_buffer = serial_buffer.split("\n", 1)
                line = line.strip()

                if line:
                    try:
                        raw_value = float(line)

                        if 0.0 <= raw_value <= 200.0:
                            inputSensorValue = remap_sensor(raw_value)

                    except ValueError:
                        pass

        # ------------------------------------------
        # SMOOTH SENSOR MORPH
        # ------------------------------------------

        morphAmount += (inputSensorValue - morphAmount) * SMOOTHING

        # ------------------------------------------
        # MOTION
        # ------------------------------------------

        yaw = math.sin(t * 0.45) * 10.0 * motion
        pitch = math.sin(t * 0.31 + 1.2) * 5.0 * motion
        roll = math.sin(t * 0.19 + 0.7) * 1.5 * motion

        modelA.position(pos_x, pos_y, pos_z)

        modelA.rotateToX(pitch)
        modelA.rotateToY(yaw)
        modelA.rotateToZ(roll)

        modelA.scale(
            scale_x * global_scale,
            scale_y * global_scale,
            scale_z * global_scale
        )

        modelA.set_custom_data(
            48,
            [morphAmount, 0.0, 0.0]
        )

        modelA.draw()
        
        # ------------------------------------------
        # AUTO CONFIG CYCLING
        # ------------------------------------------

        if cycle_seconds > 0:
            now = time.time()

            if now - last_cycle_time >= cycle_seconds:
                load_next_config(auto=True)
                last_cycle_time = now

        # ------------------------------------------
        # KEYBOARD
        # ------------------------------------------

        key = keys.read()

        if key == 27:
            break

        # ENTER saves selected config
        elif key == 10 or key == 13:
            save_current_config()

        # SPACE saves current config and loads next main config
		elif key == 32:
		    load_next_config()
		    last_cycle_time = time.time()

        # motion
        elif key == ord("a"):
            motion += 0.1
        elif key == ord("z"):
            motion = max(0.0, motion - 0.1)

        # global temporary scale, not saved
        elif key == ord("s"):
            global_scale += 0.05
        elif key == ord("x"):
            global_scale = max(0.05, global_scale - 0.05)

        # position
        elif key == ord("j"):
            pos_x -= 0.1
        elif key == ord("l"):
            pos_x += 0.1
        elif key == ord("i"):
            pos_y += 0.1
        elif key == ord("k"):
            pos_y -= 0.1
        elif key == ord("u"):
            pos_z += 0.1
        elif key == ord("o"):
            pos_z -= 0.1

        # actual saved model scale
        elif key == ord("1"):
            scale_x -= 0.05
        elif key == ord("2"):
            scale_x += 0.05
        elif key == ord("3"):
            scale_y -= 0.05
        elif key == ord("4"):
            scale_y += 0.05
        elif key == ord("5"):
            scale_z -= 0.05
        elif key == ord("6"):
            scale_z += 0.05

        # sensor calibration
        elif key == ord("q"):
            SENSOR_MIN -= 1.0
        elif key == ord("w"):
            SENSOR_MIN += 1.0
        elif key == ord("e"):
            SENSOR_MAX -= 1.0
        elif key == ord("r"):
            SENSOR_MAX += 1.0
        elif key == ord("t"):
            SMOOTHING = max(0.001, SMOOTHING - 0.01)
        elif key == ord("y"):
            SMOOTHING = min(1.0, SMOOTHING + 0.01)

finally:
    ser.close()
    keys.close()
    DISPLAY.destroy()

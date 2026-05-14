import serial
import pi3d

# ----------------------------
# SERIAL
# ----------------------------

ser = serial.Serial(
    '/dev/ttyUSB0',
    baudrate=115200,
    timeout=0
)

# ----------------------------
# DISPLAY
# ----------------------------

DISPLAY = pi3d.Display.create(
    frames_per_second=60,
    background=(0, 0, 0, 1)
)

CAMERA = pi3d.Camera(is_3d=False)

# ----------------------------
# KEYBOARD
# ----------------------------

keyboard = pi3d.Keyboard()

# ----------------------------
# FONT
# ----------------------------

font = pi3d.Font(
    "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    color=(255, 255, 255, 255)
)

shader = pi3d.Shader("uv_flat")

serial_text = pi3d.String(
    font=font,
    string="Waiting for serial...",
    x=-DISPLAY.width / 2 + 30,
    y=DISPLAY.height / 2 - 50,
    z=1.0,
    size=32
)

serial_text.set_shader(shader)

# ----------------------------
# MAIN LOOP
# ----------------------------

while DISPLAY.loop_running():

    # ------------------------
    # ESCAPE KEY
    # ------------------------

    key = keyboard.read()

    if key == 27:   # ESC key
        break

    # ------------------------
    # SERIAL READ
    # ------------------------

    if ser.in_waiting:
        try:
            line = ser.readline().decode(
                "utf-8",
                errors="ignore"
            ).strip()

            if line:
                print("SERIAL:", line)

                serial_text = pi3d.String(
                    font=font,
                    string=line,
                    x=-DISPLAY.width / 2 + 30,
                    y=DISPLAY.height / 2 - 50,
                    z=1.0,
                    size=32
                )

                serial_text.set_shader(shader)

        except Exception as e:
            print("Serial error:", e)

    # ------------------------
    # DRAW
    # ------------------------

    serial_text.draw()

# ----------------------------
# CLEANUP
# ----------------------------

keyboard.close()
ser.close()
DISPLAY.destroy()

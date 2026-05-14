import serial
import pi3d

ser = serial.Serial("/dev/ttyUSB0", baudrate=115200, timeout=0)

DISPLAY = pi3d.Display.create(
    frames_per_second=60,
    background=(0, 0, 0, 1)
)

CAMERA = pi3d.Camera(is_3d=False)
KEYBOARD = pi3d.Keyboard()

shader = pi3d.Shader("uv_flat")
font = pi3d.Font("/usr/share/fonts/truetype/freefont/FreeSans.ttf")

def make_text(msg):
    t = pi3d.String(
        camera=CAMERA,
        font=font,
        string=msg,
        x=0,
        y=0,
        z=0.1,
        size=64
    )
    t.set_shader(shader)
    return t

serial_text = make_text("Waiting for serial...")

while DISPLAY.loop_running():

    key = KEYBOARD.read()
    if key == 27:
        break

    if ser.in_waiting:
        try:
            line = ser.readline().decode("utf-8", errors="ignore").strip()

            if line:
                print("SERIAL:", line)
                serial_text = make_text(line)

        except Exception as e:
            print("Serial error:", e)

    serial_text.draw()

KEYBOARD.close()
ser.close()
DISPLAY.destroy()

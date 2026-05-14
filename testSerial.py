import serial
import pi3d

ser = serial.Serial('/dev/ttyUSB0', baudrate=115200, timeout=0)

DISPLAY = pi3d.Display.create(
    frames_per_second=60,
    background=(0, 0, 0, 1)
)

CAMERA = pi3d.Camera(is_3d=False)
KEYBOARD = pi3d.Keyboard()

shader = pi3d.Shader("uv_flat")
font = pi3d.Font("/usr/share/fonts/truetype/freefont/FreeSans.ttf")

text = "Waiting for serial..."

serial_text = pi3d.String(
    camera=CAMERA,
    font=font,
    string=text,
    x=-DISPLAY.width / 2 + 40,
    y=DISPLAY.height / 2 - 80,
    z=0.1,
    size=32
)
serial_text.set_shader(shader)

while DISPLAY.loop_running():

    if KEYBOARD.read() == 27:
        break

    if ser.in_waiting:
        line = ser.readline().decode("utf-8", errors="ignore").strip()

        if line:
            print("SERIAL:", line)

            serial_text.quick_change(line)

    serial_text.draw()

KEYBOARD.close()
ser.close()
DISPLAY.destroy()

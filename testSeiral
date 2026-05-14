import serial
import pi3d

ser = serial.Serial('/dev/ttyUSB0', baudrate=115200, timeout=0)

DISPLAY = pi3d.Display.create(
    frames_per_second=60,
    background=(0, 0, 0, 1)
)

CAMERA = pi3d.Camera(is_3d=False)

font = pi3d.Font("fonts/FreeSans.ttf", color=(255, 255, 255, 255))

serial_text = pi3d.String(
    font=font,
    string="Waiting for serial...",
    x=-DISPLAY.width / 2 + 30,
    y=DISPLAY.height / 2 - 50,
    z=1.0,
    size=32
)

serial_text.set_shader(pi3d.Shader("uv_flat"))

while DISPLAY.loop_running():

    if ser.in_waiting:
        try:
            line = ser.readline().decode("utf-8", errors="ignore").strip()

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
                serial_text.set_shader(pi3d.Shader("uv_flat"))

        except Exception as e:
            print("Serial error:", e)

    serial_text.draw()

ser.close()
DISPLAY.destroy()

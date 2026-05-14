import time
import math
import pi3d

DISPLAY = pi3d.Display.create(
    frames_per_second=60,
    background=(0.0, 0.0, 0.0, 1.0)
)

# Camera and shader
CAMERA = pi3d.Camera()
shader = pi3d.Shader("uv_light")

# Light
light = pi3d.Light(
    lightpos=(2, -3, -4),
    lightcol=(1.0, 1.0, 1.0),
    lightamb=(0.3, 0.3, 0.3)
)

# Load texture
texture = pi3d.Texture("Meshy_AI_Eye_of_the_Machine_0514103702_texture.png")

# Load OBJ model
model = pi3d.Model(
    file_string="Meshy_AI_Eye_of_the_Machine_0514103702_texture.obj",
    name="object",
    x=0,
    y=0,
    z=5,
    sx=1,
    sy=1,
    sz=1
)

model.set_shader(shader)
model.set_normal_shine(texture, 16.0)

# Keyboard
keys = pi3d.Keyboard()
start_time = time.time()

intensity = 1.0
scale = 1.0

while DISPLAY.loop_running():
    t = time.time() - start_time

    yaw = math.sin(t * 0.45) * 10.0 * intensity
    pitch = math.sin(t * 0.31 + 1.2) * 5.0 * intensity
    roll = math.sin(t * 0.19 + 0.7) * 1.5 * intensity

    model.rotateToX(pitch)
    model.rotateToY(yaw)
    model.rotateToZ(roll)

    model.scale(scale, scale, scale)

    model.draw()

    key = keys.read()

    if key == 27:  # ESC
        break

    elif key == ord('a'):
        intensity += 0.1
        print("Intensity:", round(intensity, 2))

    elif key == ord('z'):
        intensity = max(0.0, intensity - 0.1)
        print("Intensity:", round(intensity, 2))

    elif key == ord('s'):
        scale += 0.05
        print("Scale:", round(scale, 2))

    elif key == ord('x'):
        scale = max(0.05, scale - 0.05)
        print("Scale:", round(scale, 2))

keys.close()
DISPLAY.destroy()

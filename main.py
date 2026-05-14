import pi3d

# Display setup
DISPLAY = pi3d.Display.create(
    background=(0.05, 0.05, 0.08, 1.0),
    w=800,
    h=600
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
texture = pi3d.Texture("model_texture.png")

# Load OBJ model
model = pi3d.Model(
    file_string="model.obj",
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

while DISPLAY.loop_running():
    model.rotateIncY(1.0)
    model.rotateIncX(0.3)

    model.draw()

    key = keys.read()
    if key == 27:  # ESC
        break

keys.close()
DISPLAY.destroy()

import time
import math
import pi3d

OBJ_A = "eyeOpen.obj"
OBJ_B = "eyeClosed.obj"
TEXTURE = "eyeTexture .png"

DISPLAY = pi3d.Display.create(
    frames_per_second=60,
    background=(0.0, 0.0, 0.0, 1.0)
)

CAMERA = pi3d.Camera()

VERT_SHADER = """
#ifdef GL_ES
precision mediump float;
#endif

attribute vec3 vertex;     // positionA
attribute vec3 normal;     // positionB
attribute vec2 texcoord;

uniform mat4 modelviewmatrix;
uniform vec3 unif[20];

varying vec2 uv;

void main(void) {

    float morphAmount = unif[16].x;

    vec3 positionA = vertex;
    vec3 positionB = normal;

    vec3 pos = mix(positionA, positionB, morphAmount);

    gl_Position = modelviewmatrix * vec4(pos, 1.0);

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

    vec4 tex = texture2D(tex0, uv);

    gl_FragColor = tex;
}
"""

shader = pi3d.Shader(
    vshader_source=VERT_SHADER,
    fshader_source=FRAG_SHADER
)

texture = pi3d.Texture(TEXTURE)

modelA = pi3d.Model(
    file_string=OBJ_A,
    x=0,
    y=0,
    z=5.0,
    sx=1,
    sy=1,
    sz=1
)

modelB = pi3d.Model(file_string=OBJ_B)

modelA.set_shader(shader)
modelA.set_draw_details(shader, [texture])

# Copy target vertices into normal buffer
for bufA, bufB in zip(modelA.buf, modelB.buf):

    if len(bufA.array_buffer) != len(bufB.array_buffer):
        raise ValueError(
            "OBJ files must have identical topology"
        )

    positionB = bufB.array_buffer[:, 0:3]

    # overwrite normals with morph target positions
    bufA.re_init(normals=positionB)

keys = pi3d.Keyboard()

start_time = time.time()

motion = 1.0
scale = 1.0
morphAmount = 0.0

while DISPLAY.loop_running():

    t = time.time() - start_time

    # lissajous-style fake camera orbit
    yaw = math.sin(t * 0.45) * 10.0 * motion
    pitch = math.sin(t * 0.31 + 1.2) * 5.0 * motion
    roll = math.sin(t * 0.19 + 0.7) * 1.5 * motion

    modelA.rotateToX(pitch)
    modelA.rotateToY(yaw)
    modelA.rotateToZ(roll)

    modelA.scale(scale, scale, scale)

    # shader custom uniform
    modelA.set_custom_data(
        48,  # unif[16]
        [morphAmount, 0.0, 0.0]
    )

    modelA.draw()

    key = keys.read()

    if key == 27:
        break

    # motion
    elif key == ord("a"):
        motion += 0.1
        print("Motion:", round(motion, 2))

    elif key == ord("z"):
        motion = max(0.0, motion - 0.1)
        print("Motion:", round(motion, 2))

    # scale
    elif key == ord("s"):
        scale += 0.05
        print("Scale:", round(scale, 2))

    elif key == ord("x"):
        scale = max(0.05, scale - 0.05)
        print("Scale:", round(scale, 2))

    # morph
    elif key == ord("d"):
        morphAmount = min(1.0, morphAmount + 0.05)
        print("Morph:", round(morphAmount, 2))

    elif key == ord("c"):
        morphAmount = max(0.0, morphAmount - 0.05)
        print("Morph:", round(morphAmount, 2))

keys.close()
DISPLAY.destroy()

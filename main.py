import time
import math
import pi3d

OBJ_A = "eyeOpen.obj"
OBJ_B = "eyeOpen.obj"

DISPLAY = pi3d.Display.create(
    frames_per_second=60,
    background=(0.0, 0.0, 0.0, 1.0)
)

VERT_SHADER = """
#ifdef GL_ES
precision mediump float;
#endif

attribute vec3 vertex;
attribute vec3 normal;

uniform mat4 modelviewmatrix[2];
uniform vec3 unif[20];

void main(void) {
    float morphAmount = unif[16].x;

    vec3 positionA = vertex;
    vec3 positionB = normal;

    vec3 pos = mix(positionA, positionB, morphAmount);

    gl_Position = modelviewmatrix[1] * modelviewmatrix[0] * vec4(pos, 1.0);
}
"""

FRAG_SHADER = """
#ifdef GL_ES
precision mediump float;
#endif

void main(void) {
    gl_FragColor = vec4(1.0, 0.75, 0.25, 1.0);
}
"""

shader = pi3d.Shader(
    vshader_source=VERT_SHADER,
    fshader_source=FRAG_SHADER
)

modelA = pi3d.Model(
    file_string=OBJ_A,
    x=0,
    y=0,
    z=8.0,
    sx=1.0,
    sy=1.0,
    sz=1.0
)

modelB = pi3d.Model(file_string=OBJ_B)

if len(modelA.buf) != len(modelB.buf):
    raise ValueError("OBJ files must have the same number of buffers")

for bufA, bufB in zip(modelA.buf, modelB.buf):
    if len(bufA.array_buffer) != len(bufB.array_buffer):
        raise ValueError("OBJ files must have identical vertex count/order")

    # GPU-side positionB stored in normal attribute
    positionB = bufB.array_buffer[:, 0:3]
    bufA.re_init(normals=positionB)

modelA.set_shader(shader)
modelA.set_material((1.0, 1.0, 1.0))

keys = pi3d.Keyboard()

start_time = time.time()

motion = 1.0
scale = 1.0
morphAmount = 0.0

while DISPLAY.loop_running():
    t = time.time() - start_time

    yaw = math.sin(t * 0.45) * 10.0 * motion
    pitch = math.sin(t * 0.31 + 1.2) * 5.0 * motion
    roll = math.sin(t * 0.19 + 0.7) * 1.5 * motion

    modelA.rotateToX(pitch)
    modelA.rotateToY(yaw)
    modelA.rotateToZ(roll)

    modelA.scale(scale, scale, scale)

    # unif[16].x
    modelA.set_custom_data(48, [morphAmount, 0.0, 0.0])

    modelA.draw()

    key = keys.read()

    if key == 27:
        break

    elif key == ord("a"):
        motion += 0.1
        print("Motion:", round(motion, 2))

    elif key == ord("z"):
        motion = max(0.0, motion - 0.1)
        print("Motion:", round(motion, 2))

    elif key == ord("s"):
        scale += 0.05
        print("Scale:", round(scale, 2))

    elif key == ord("x"):
        scale = max(0.05, scale - 0.05)
        print("Scale:", round(scale, 2))

    elif key == ord("d"):
        morphAmount = min(1.0, morphAmount + 0.05)
        print("Morph:", round(morphAmount, 2))

    elif key == ord("c"):
        morphAmount = max(0.0, morphAmount - 0.05)
        print("Morph:", round(morphAmount, 2))

keys.close()
DISPLAY.destroy()

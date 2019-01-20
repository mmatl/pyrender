DEFAULT_Z_NEAR = 0.05     # Near clipping plane, in meters
DEFAULT_Z_FAR = 100.0     # Far clipping plane, in meters
MAX_N_LIGHTS = 4          # Maximum number of lights of each type allowed
OPEN_GL_MAJOR = 4         # Target OpenGL Major Version
OPEN_GL_MINOR = 1         # Target OpenGL Minor Version
FLOAT_SZ = 4              # Byte size of GL float32
UINT_SZ = 4               # Byte size of GL uint32
SHADOW_TEX_SZ = 1024      # Width and Height of Shadow Textures

class GLTF(object):
    NEAREST = 9728
    LINEAR = 9729
    NEAREST_MIPMAP_NEAREST = 9984
    LINEAR_MIPMAP_NEAREST = 9985
    NEAREST_MIPMAP_LINEAR = 9986
    LINEAR_MIPMAP_LINEAR = 9987
    CLAMP_TO_EDGE = 33071
    MIRRORED_REPEAT = 33648
    REPEAT = 10497
    POINTS = 0
    LINES = 1
    LINE_LOOP = 2
    LINE_STRIP = 3
    TRIANGLES = 4
    TRIANGLE_STRIP = 5
    TRIANGLE_FAN = 6

class BufFlags(object):
    POSITION = 0
    NORMAL = 1
    TANGENT = 2
    TEXCOORD_0 = 4
    TEXCOORD_1 = 8
    COLOR_0 = 16
    JOINTS_0 = 32
    WEIGHTS_0 = 64

class TexFlags(object):
    NONE = 0
    NORMAL = 1
    OCCLUSION = 2
    EMISSIVE = 4
    BASE_COLOR = 8
    METALLIC_ROUGHNESS = 16
    DIFFUSE = 32
    SPECULAR_GLOSSINESS = 64

# Flags for render type
class RenderFlags(object):
    NONE = 0                    # Normal PBR render
    DEPTH_ONLY = 1              # Only render the depth buffer
    OFFSCREEN = 2               # Render offscreen and return the images rendered
    FLIP_WIREFRAME = 4          # Invert the status of wireframe rendering for each mesh
    ALL_WIREFRAME = 8           # Render all meshes as wireframes
    ALL_SOLID = 16              # Render all meshes as solids
    SHADOWS_DIRECTIONAL = 32    # Perform shadow mapping for directional lights
    SHADOWS_POINT = 64          # Perform shadow mapping for point lights
    SHADOWS_SPOT = 128          # Perform shadow mapping for spot lights
    SHADOWS_ALL = 256           # Perform shadow mapping for all lights
    VERTEX_NORMALS = 512        # Show vertex normals
    FACE_NORMALS = 1024         # Show face normals
    SKIP_CULL_FACES = 2048      # Do not cull back faces

class ProgramFlags:
    NONE = 0
    USE_MATERIAL = 1
    VERTEX_NORMALS = 2
    FACE_NORMALS = 4

class TextAlign:
    NONE = 0
    BOTTOM_LEFT = 1
    BOTTOM_RIGHT = 2
    BOTTOM_CENTER = 3
    TOP_LEFT = 4
    TOP_RIGHT = 5
    TOP_CENTER = 6
    CENTER = 7

DEFAULT_Z_NEAR = 0.05     # Near clipping plane, in meters
DEFAULT_Z_FAR = 100.0     # Far clipping plane, in meters
DEFAULT_SCENE_SCALE = 2.0 # Default scene scale
MAX_N_LIGHTS = 4          # Maximum number of lights of each type allowed
OPEN_GL_MAJOR = 4         # Target OpenGL Major Version
OPEN_GL_MINOR = 1         # Target OpenGL Minor Version
FLOAT_SZ = 4              # Byte size of GL float32
UINT_SZ = 4               # Byte size of GL uint32
SHADOW_TEX_SZ = 1024      # Width and Height of Shadow Textures
TEXT_PADDING = 20         # Width of padding for rendering text (px)


def _flag_value(i):
    if i == 0:
        return 0
    return 2 ** (i - 1)


# Flags for render type
class RenderFlags(object):
    """Flags for rendering in the scene.

    Combine them with the bitwise or. For example,

    >>> flags = OFFSCREEN | SHADOWS_DIRECTIONAL | VERTEX_NORMALS

    would result in an offscreen render with directional shadows and
    vertex normals enabled.
    """
    NONE = _flag_value(0)
    """Normal PBR Render."""
    NO_LIGHTS = _flag_value(1)
    """Do not render lights."""
    NO_MATERIALS = _flag_value(2)
    """Do not render lights."""
    DEPTH_ONLY = NO_LIGHTS | NO_MATERIALS | _flag_value(3)
    """Only render the depth buffer."""
    OFFSCREEN = _flag_value(4)
    """Render offscreen and return the depth and (optionally) color buffers."""
    FLIP_WIREFRAME = _flag_value(5)
    """Invert the status of wireframe rendering for each mesh."""
    ALL_WIREFRAME = _flag_value(6)
    """Render all meshes as wireframes."""
    ALL_SOLID = _flag_value(7)
    """Render all meshes as solids."""
    SHADOWS_DIRECTIONAL = _flag_value(8)
    """Render shadows for directional lights."""
    SHADOWS_POINT = _flag_value(9)
    """Render shadows for point lights."""
    SHADOWS_SPOT = _flag_value(10)
    """Render shadows for spot lights."""
    SHADOWS_ALL = SHADOWS_DIRECTIONAL | SHADOWS_POINT | SHADOWS_SPOT
    """Render shadows for all lights."""
    VERTEX_NORMALS = _flag_value(11)
    """Render vertex normals."""
    FACE_NORMALS = _flag_value(12)
    """Render face normals."""
    SKIP_CULL_FACES = _flag_value(13)
    """Do not cull back faces."""
    RGBA = _flag_value(14)
    """Render the color buffer with the alpha channel enabled."""
    ALL_CAM_COORDS = NO_LIGHTS | NO_MATERIALS | _flag_value(15)
    """Render the camera coordinates of pixels."""


class TextAlign:
    """Text alignment options for captions.

    Only use one at a time.
    """
    CENTER = 0
    """Center the text by width and height."""
    CENTER_LEFT = 1
    """Center the text by height and left-align it."""
    CENTER_RIGHT = 2
    """Center the text by height and right-align it."""
    BOTTOM_LEFT = 3
    """Put the text in the bottom-left corner."""
    BOTTOM_RIGHT = 4
    """Put the text in the bottom-right corner."""
    BOTTOM_CENTER = 5
    """Center the text by width and fix it to the bottom."""
    TOP_LEFT = 6
    """Put the text in the top-left corner."""
    TOP_RIGHT = 7
    """Put the text in the top-right corner."""
    TOP_CENTER = 8
    """Center the text by width and fix it to the top."""


class GLTF(object):
    """Options for GL objects."""
    NEAREST = 9728
    """Nearest neighbor interpolation."""
    LINEAR = 9729
    """Linear interpolation."""
    NEAREST_MIPMAP_NEAREST = 9984
    """Nearest mipmapping."""
    LINEAR_MIPMAP_NEAREST = 9985
    """Linear mipmapping."""
    NEAREST_MIPMAP_LINEAR = 9986
    """Nearest mipmapping."""
    LINEAR_MIPMAP_LINEAR = 9987
    """Linear mipmapping."""
    CLAMP_TO_EDGE = 33071
    """Clamp to the edge of the texture."""
    MIRRORED_REPEAT = 33648
    """Mirror the texture."""
    REPEAT = 10497
    """Repeat the texture."""
    POINTS = 0
    """Render as points."""
    LINES = 1
    """Render as lines."""
    LINE_LOOP = 2
    """Render as a line loop."""
    LINE_STRIP = 3
    """Render as a line strip."""
    TRIANGLES = 4
    """Render as triangles."""
    TRIANGLE_STRIP = 5
    """Render as a triangle strip."""
    TRIANGLE_FAN = 6
    """Render as a triangle fan."""


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


class ProgramFlags:
    NONE = 0
    USE_MATERIAL = 1
    VERTEX_NORMALS = 2
    FACE_NORMALS = 4


__all__ = ['RenderFlags', 'TextAlign', 'GLTF']

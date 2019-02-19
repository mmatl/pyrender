DEFAULT_Z_NEAR = 0.05     # Near clipping plane, in meters
DEFAULT_Z_FAR = 100.0     # Far clipping plane, in meters
MAX_N_LIGHTS = 4          # Maximum number of lights of each type allowed
OPEN_GL_MAJOR = 4         # Target OpenGL Major Version
OPEN_GL_MINOR = 1         # Target OpenGL Minor Version
FLOAT_SZ = 4              # Byte size of GL float32
UINT_SZ = 4               # Byte size of GL uint32
SHADOW_TEX_SZ = 1024      # Width and Height of Shadow Textures
TEXT_PADDING = 20         # Width of padding for rendering text (px)

# Flags for render type
class RenderFlags(object):
    """Flags for rendering in the scene.

    Combine them with the bitwise or. For example,

    >>> flags = OFFSCREEN | SHADOWS_DIRECTIONAL | VERTEX_NORMALS

    would result in an offscreen render with directional shadows and vertex normals
    enabled.
    """
    NONE = 0
    """Normal PBR Render."""
    DEPTH_ONLY = 1
    """Only render the depth buffer."""
    OFFSCREEN = 2               # Render offscreen and return the images rendered
    """Render offscreen and return the depth and (optionally) color buffers."""
    FLIP_WIREFRAME = 4          # Invert the status of wireframe rendering for each mesh
    """Invert the status of wireframe rendering for each mesh."""
    ALL_WIREFRAME = 8           # Render all meshes as wireframes
    """Render all meshes as wireframes."""
    ALL_SOLID = 16              # Render all meshes as solids
    """Render all meshes as solids."""
    SHADOWS_DIRECTIONAL = 32    # Perform shadow mapping for directional lights
    """Render shadows for directional lights."""
    SHADOWS_POINT = 64          # Perform shadow mapping for point lights
    """Render shadows for point lights."""
    SHADOWS_SPOT = 128          # Perform shadow mapping for spot lights
    """Render shadows for spot lights."""
    SHADOWS_ALL = 32 | 64 | 128     # Perform shadow mapping for all lights
    """Render shadows for all lights."""
    VERTEX_NORMALS = 256        # Show vertex normals
    """Render vertex normals."""
    FACE_NORMALS = 512         # Show face normals
    """Render face normals."""
    SKIP_CULL_FACES = 1024      # Do not cull back faces
    """Do not cull back faces."""
    RGBA = 2048
    """Render the color buffer with the alpha channel enabled."""

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

class ProgramFlags:
    NONE = 0
    USE_MATERIAL = 1
    VERTEX_NORMALS = 2
    FACE_NORMALS = 4

__all__ = ['RenderFlags', 'TextAlign']

"""Samplers, conforming to the glTF 2.0 standards as specified in
https://github.com/KhronosGroup/glTF/tree/master/specification/2.0#reference-sampler

Author: Matthew Matl
"""
from .constants import GLTF

class Sampler(object):
    """Texture sampler properties for filtering and wrapping modes.

    Attributes
    ----------
    name : str, optional
        The user-defined name of this object.
    magFilter : int, optional
        Magnification filter. Valid values:
            - `GLTF.NEAREST`
            - `GLTF.LINEAR`
    minFilter : int, optional
        Minification filter. Valid values:
            - `GLTF.NEAREST`
            - `GLTF.LINEAR`
            - `GLTF.NEAREST_MIPMAP_NEAREST`
            - `GLTF.LINEAR_MIPMAP_NEAREST`
            - `GLTF.NEAREST_MIPMAP_LINEAR`
            - `GLTF.LINEAR_MIPMAP_LINEAR`
    wrapS : int, optional
        S (U) wrapping mode. Valid values:
            - `GLTF.CLAMP_TO_EDGE`
            - `GLTF.MIRRORED_REPEAT`
            - `GLTF.REPEAT`
    wrapT : int, optional
        T (V) wrapping mode. Valid values:
            - `GLTF.CLAMP_TO_EDGE`
            - `GLTF.MIRRORED_REPEAT`
            - `GLTF.REPEAT`
    """

    def __init__(self,
                 name=None,
                 magFilter=None,
                 minFilter=None,
                 wrapS=GLTF.REPEAT,
                 wrapT=GLTF.REPEAT):
        self.name = name
        self.magFilter = magFilter
        self.minFilter = minFilter
        self.wrapS = wrapS
        self.wrapT = wrapT

"""Wrapper for offscreen rendering.

Author: Matthew Matl
"""
import os

from .renderer import Renderer
from .platforms import EGLPlatform, OSMesaPlatform, PygletPlatform
from .constants import RenderFlags

class OffscreenRenderer(object):
    """A wrapper for offscreen rendering.

    Attributes
    ----------
    viewport_width : int
        The width of the main viewport, in pixels.
    viewport_height : int
        The height of the main viewport, in pixels
    """

    def __init__(self, viewport_width, viewport_height):
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height

        self._platform = None
        self._renderer = None
        self._create()

    def render(self, scene, flags=RenderFlags.NONE):
        """Render a scene with the given set of flags.

        Parameters
        ----------
        scene : :obj:`Scene`
            A scene to render.
        flags : int
            A specification from `RenderFlags`. Valid flags include:
                - `RenderFlags.NONE`: A normal PBR render
                - `RenderFlags.DEPTH_ONLY`: Render the depth buffer alone.
                - `RenderFlags.FLIP_WIREFRAME`: Invert the status of wireframe rendering for each material.
                - `RenderFlags.ALL_WIREFRAME`: Render all materials in wireframe mode.
                - `RenderFlags.ALL_SOLID`: Render all meshes as solids
                - `RenderFlags.SHADOWS_DIRECTIONAL`: Compute shadowing for directional lights.
                - `RenderFlags.SHADOWS_POINT`: Compute shadowing for point lights.
                - `RenderFlags.SHADOWS_SPOT`: Compute shadowing for spot lights.
                - `RenderFlags.SHADOWS_ALL`: Compute shadowing for all lights.
                - `RenderFlags.VERTEX_NORMALS`: Show vertex normals as blue lines.
                - `RenderFlags.FACE_NORMALS`: Show face normals as blue lines.
                - `RenderFlags.SKIP_CULL_FACES`: Do not cull back faces.

        Returns
        -------
        color_im : (h, w, 3) uint8
            The color buffer in RGB byte format.
        depth_im : (h, w) float32
            The depth buffer in linear units.
        """

        # If platform does not support dynamically-resizing framebuffers,
        # destroy it and restart it
        if (self._platform.viewport_height != self.viewport_height or
            self._platform.viewport_width != self.viewport_width):
            if not self._platform.supports_framebuffers():
                self.delete()
                self._create()

        self._platform.make_current()
        self._renderer.viewport_width = self.viewport_width
        self._renderer.viewport_height = self.viewport_height

        if self._platform.supports_framebuffers():
            flags |= RenderFlags.OFFSCREEN
            color, depth = self._renderer.render(scene, flags)
        else:
            self._renderer.render(scene, flags)
            color = self._renderer.read_color_buf()
            depth = self._renderer.read_depth_buf()

        return color, depth

    def delete(self):
        """Free all OpenGL resources.
        """
        self._renderer.delete()
        self._platform.delete_context()

    def _create(self):
        if not 'PYOPENGL_PLATFORM' in os.environ:
            self._platform = PygletPlatform(self.viewport_width, self.viewport_height)
        elif os.environ['PYOPENGL_PLATFORM'] == 'egl':
            self._platform = EGLPlatform(self.viewport_width, self.viewport_height)
        elif os.environ['PYOPENGL_PLATFORM'] == 'osmesa':
            self._platform = OSMesaPlatform(self.viewport_width, self.viewport_height)
        else:
            raise ValueError('Unsupported PyOpenGL platform: {}'.format(
                os.environ['PYOPENGL_PLATFORM']
            ))
        self._platform.init_context()
        self._platform.make_current()
        self._renderer = Renderer(self.viewport_width, self.viewport_height)


    def __del__(self):
        try:
            self.delete()
        except:
            pass

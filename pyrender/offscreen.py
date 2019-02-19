"""Wrapper for offscreen rendering.

Author: Matthew Matl
"""
import os

from .renderer import Renderer
from .platforms import EGLPlatform, OSMesaPlatform, PygletPlatform
from .constants import RenderFlags


class OffscreenRenderer(object):
    """A wrapper for offscreen rendering.

    Parameters
    ----------
    viewport_width : int
        The width of the main viewport, in pixels.
    viewport_height : int
        The height of the main viewport, in pixels.
    point_size : float
        The size of screen-space points in pixels.
    """

    def __init__(self, viewport_width, viewport_height, point_size=1.0):
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        self.point_size = point_size

        self._platform = None
        self._renderer = None
        self._create()

    @property
    def viewport_width(self):
        """int : The width of the main viewport, in pixels.
        """
        return self._viewport_width

    @viewport_width.setter
    def viewport_width(self, value):
        self._viewport_width = int(value)

    @property
    def viewport_height(self):
        """int : The height of the main viewport, in pixels.
        """
        return self._viewport_height

    @viewport_height.setter
    def viewport_height(self, value):
        self._viewport_height = int(value)

    @property
    def point_size(self):
        """float : The pixel size of points in point clouds.
        """
        return self._point_size

    @point_size.setter
    def point_size(self, value):
        self._point_size = float(value)

    def render(self, scene, flags=RenderFlags.NONE):
        """Render a scene with the given set of flags.

        Parameters
        ----------
        scene : :class:`Scene`
            A scene to render.
        flags : int
            A bitwise or of one or more flags from :class:`.RenderFlags`.

        Returns
        -------
        color_im : (h, w, 3) uint8 or (h, w, 4) uint8
            The color buffer in RGB format, or in RGBA format if
            :attr:`.RenderFlags.RGBA` is set.
            Not returned if flags includes :attr:`.RenderFlags.DEPTH_ONLY`.
        depth_im : (h, w) float32
            The depth buffer in linear units.
        """

        self._platform.make_current()
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
        self._renderer.point_size = self.point_size

        if self._platform.supports_framebuffers():
            flags |= RenderFlags.OFFSCREEN
            return self._renderer.render(scene, flags)
        else:
            self._renderer.render(scene, flags)
            depth = self._renderer.read_depth_buf()
            if flags & RenderFlags.DEPTH_ONLY:
                return depth
            color = self._renderer.read_color_buf()
            return color, depth

    def delete(self):
        """Free all OpenGL resources.
        """
        self._renderer.delete()
        self._platform.delete_context()

    def _create(self):
        if 'PYOPENGL_PLATFORM' not in os.environ:
            self._platform = PygletPlatform(self.viewport_width,
                                            self.viewport_height)
        elif os.environ['PYOPENGL_PLATFORM'] == 'egl':
            self._platform = EGLPlatform(self.viewport_width,
                                         self.viewport_height)
        elif os.environ['PYOPENGL_PLATFORM'] == 'osmesa':
            self._platform = OSMesaPlatform(self.viewport_width,
                                            self.viewport_height)
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
        except Exception:
            pass


__all__ = ['OffscreenRenderer']

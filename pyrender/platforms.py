"""Platforms for generating offscreen OpenGL contexts for rendering.

Author: Matthew Matl
"""
import abc
import ctypes
import os
import six

from .constants import OPEN_GL_MAJOR, OPEN_GL_MINOR


@six.add_metaclass(abc.ABCMeta)
class Platform(object):
    """Base class for all OpenGL platforms.

    Parameters
    ----------
    viewport_width : int
        The width of the main viewport, in pixels.
    viewport_height : int
        The height of the main viewport, in pixels
    """

    def __init__(self, viewport_width, viewport_height):
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height

    @property
    def viewport_width(self):
        """int : The width of the main viewport, in pixels.
        """
        return self._viewport_width

    @viewport_width.setter
    def viewport_width(self, value):
        self._viewport_width = value

    @property
    def viewport_height(self):
        """int : The height of the main viewport, in pixels.
        """
        return self._viewport_height

    @viewport_height.setter
    def viewport_height(self, value):
        self._viewport_height = value

    @abc.abstractmethod
    def init_context(self):
        """Create an OpenGL context.
        """
        pass

    @abc.abstractmethod
    def make_current(self):
        """Make the OpenGL context current.
        """
        pass

    @abc.abstractmethod
    def delete_context(self):
        """Delete the OpenGL context.
        """
        pass

    @abc.abstractmethod
    def supports_framebuffers(self):
        """Returns True if the method supports framebuffer rendering.
        """
        pass

    def __del__(self):
        try:
            self.delete_context()
        except Exception:
            pass


class EGLPlatform(Platform):
    """Renders using EGL (not currently working on Ubuntu).
    """

    def __init__(self, viewport_width, viewport_height):
        super(EGLPlatform, self).__init__(viewport_width, viewport_height)
        self._egl_display = None
        self._egl_context = None

    def init_context(self):
        from OpenGL.EGL import (
            EGL_SURFACE_TYPE, EGL_PBUFFER_BIT, EGL_BLUE_SIZE,
            EGL_RED_SIZE, EGL_GREEN_SIZE, EGL_DEPTH_SIZE,
            EGL_COLOR_BUFFER_TYPE, EGL_RGB_BUFFER,
            EGL_RENDERABLE_TYPE, EGL_OPENGL_BIT, EGL_CONFORMANT,
            EGL_NONE, EGL_DEFAULT_DISPLAY, EGL_NO_CONTEXT,
            EGL_OPENGL_API, EGL_CONTEXT_MAJOR_VERSION,
            EGL_CONTEXT_MINOR_VERSION,
            EGL_CONTEXT_OPENGL_PROFILE_MASK,
            EGL_CONTEXT_OPENGL_CORE_PROFILE_BIT,
            eglGetDisplay, eglInitialize, eglChooseConfig,
            eglBindAPI, eglCreateContext, EGLConfig
        )
        from OpenGL import arrays

        config_attributes = arrays.GLintArray.asArray([
            EGL_SURFACE_TYPE, EGL_PBUFFER_BIT,
            EGL_BLUE_SIZE, 8,
            EGL_RED_SIZE, 8,
            EGL_GREEN_SIZE, 8,
            EGL_DEPTH_SIZE, 24,
            EGL_COLOR_BUFFER_TYPE, EGL_RGB_BUFFER,
            EGL_RENDERABLE_TYPE, EGL_OPENGL_BIT,
            EGL_CONFORMANT, EGL_OPENGL_BIT,
            EGL_NONE
        ])
        context_attributes = arrays.GLintArray.asArray([
            EGL_CONTEXT_MAJOR_VERSION, 4,
            EGL_CONTEXT_MINOR_VERSION, 1,
            EGL_CONTEXT_OPENGL_PROFILE_MASK,
            EGL_CONTEXT_OPENGL_CORE_PROFILE_BIT,
            EGL_NONE
        ])
        major, minor = ctypes.c_long(), ctypes.c_long()
        num_configs = ctypes.c_long()
        configs = (EGLConfig * 1)()

        # Cache DISPLAY if necessary and get an off-screen EGL display
        orig_dpy = None
        if 'DISPLAY' in os.environ:
            orig_dpy = os.environ['DISPLAY']
            del os.environ['DISPLAY']
        self._egl_display = eglGetDisplay(EGL_DEFAULT_DISPLAY)
        if orig_dpy is not None:
            os.environ['DISPLAY'] = orig_dpy

        # Initialize EGL
        assert eglInitialize(self._egl_display, major, minor)
        assert eglChooseConfig(
            self._egl_display, config_attributes, configs, 1, num_configs
        )

        # Bind EGL to the OpenGL API
        assert eglBindAPI(EGL_OPENGL_API)

        # Create an EGL context
        self._egl_context = eglCreateContext(
            self._egl_display, configs[0],
            EGL_NO_CONTEXT, context_attributes
        )

        # Make it current
        self.make_current()

    def make_current(self):
        from OpenGL.EGL import eglMakeCurrent, EGL_NO_SURFACE
        assert eglMakeCurrent(
            self._egl_display, EGL_NO_SURFACE, EGL_NO_SURFACE,
            self._egl_context
        )

    def delete_context(self):
        from OpenGL.EGL import eglDestroyContext, eglTerminate
        if self._egl_display is not None:
            if self._egl_context is not None:
                eglDestroyContext(self._egl_display, self._egl_context)
                self._egl_context = None
            eglTerminate(self._egl_display)
            self._egl_display = None

    def supports_framebuffers(self):
        return True


class PygletPlatform(Platform):
    """Renders on-screen using a 1x1 hidden Pyglet window for getting
    an OpenGL context.
    """

    def __init__(self, viewport_width, viewport_height):
        super(PygletPlatform, self).__init__(viewport_width, viewport_height)
        self._window = None

    def init_context(self):
        import pyglet
        pyglet.options['shadow_window'] = False

        self._window = None
        conf = pyglet.gl.Config(
            sample_buffers=1, samples=4,
            depth_size=24,
            double_buffer=True,
            major_version=OPEN_GL_MAJOR,
            minor_version=OPEN_GL_MINOR
        )
        try:
            self._window = pyglet.window.Window(config=conf, visible=False,
                                                resizable=False,
                                                width=1, height=1)
        except Exception as e:
            raise ValueError(
                'Failed to initialize Pyglet window with an OpenGL >= 3+ '
                'context. If you\'re logged in via SSH, ensure that you\'re '
                'running your script with vglrun (i.e. VirtualGL). The '
                'internal error message was "{}"'.format(e)
            )

    def make_current(self):
        if self._window:
            self._window.switch_to()

    def delete_context(self):
        if self._window is not None:
            try:
                self._window.context.destroy()
                self._window.close()
            except Exception:
                pass
            self._window = None

    def supports_framebuffers(self):
        return True


class OSMesaPlatform(Platform):
    """Renders into a software buffer using OSMesa. Requires special versions
    of OSMesa to be installed, plus PyOpenGL upgrade.
    """

    def __init__(self, viewport_width, viewport_height):
        super(OSMesaPlatform, self).__init__(viewport_width, viewport_height)
        self._context = None
        self._buffer = None

    def init_context(self):
        from OpenGL import arrays
        from OpenGL.osmesa import (
            OSMesaCreateContextAttribs, OSMESA_FORMAT,
            OSMESA_RGBA, OSMESA_PROFILE, OSMESA_CORE_PROFILE,
            OSMESA_CONTEXT_MAJOR_VERSION, OSMESA_CONTEXT_MINOR_VERSION,
            OSMESA_DEPTH_BITS
        )

        attrs = arrays.GLintArray.asArray([
            OSMESA_FORMAT, OSMESA_RGBA,
            OSMESA_DEPTH_BITS, 24,
            OSMESA_PROFILE, OSMESA_CORE_PROFILE,
            OSMESA_CONTEXT_MAJOR_VERSION, 3,
            OSMESA_CONTEXT_MINOR_VERSION, 3,
            0
        ])
        self._context = OSMesaCreateContextAttribs(attrs, None)
        self._buffer = arrays.GLubyteArray.zeros(
            (self.viewport_height, self.viewport_width, 4)
        )

    def make_current(self):
        from OpenGL import GL as gl
        from OpenGL.osmesa import OSMesaMakeCurrent
        assert(OSMesaMakeCurrent(
            self._context, self._buffer, gl.GL_UNSIGNED_BYTE,
            self.viewport_width, self.viewport_height
        ))

    def delete_context(self):
        from OpenGL.osmesa import OSMesaDestroyContext
        OSMesaDestroyContext(self._context)
        self._context = None
        self._buffer = None

    def supports_framebuffers(self):
        return False

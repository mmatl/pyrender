from pyrender.constants import OPEN_GL_MAJOR, OPEN_GL_MINOR
from .base import Platform

import OpenGL


__all__ = ['PygletPlatform']


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

        try:
            pyglet.lib.x11.xlib.XInitThreads()
        except Exception:
            pass

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

    def make_uncurrent(self):
        import pyglet
        pyglet.gl.xlib.glx.glXMakeContextCurrent(self._window.context.x_display, 0, 0, None)

    def delete_context(self):
        if self._window is not None:
            self.make_current()
            cid = OpenGL.contextdata.getContext()
            try:
                self._window.context.destroy()
                self._window.close()
            except Exception:
                pass
            self._window = None
            OpenGL.contextdata.cleanupContext(cid)
            del cid

    def supports_framebuffers(self):
        return True

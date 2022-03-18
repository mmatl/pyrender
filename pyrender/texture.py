"""Textures, conforming to the glTF 2.0 standards as specified in
https://github.com/KhronosGroup/glTF/tree/master/specification/2.0#reference-texture

Author: Matthew Matl
"""
import numpy as np

from OpenGL.GL import *

from .utils import format_texture_source
from .sampler import Sampler


class Texture(object):
    """A texture and its sampler.

    Parameters
    ----------
    name : str, optional
        The user-defined name of this object.
    sampler : :class:`Sampler`
        The sampler used by this texture.
    source : (h,w,c) uint8 or (h,w,c) float or :class:`PIL.Image.Image`
        The image used by this texture. If None, the texture is created
        empty and width and height must be specified.
    source_channels : str
        Either `D`, `R`, `RG`, `GB`, `RGB`, or `RGBA`. Indicates the
        channels to extract from `source`. Any missing channels will be filled
        with `1.0`.
    width : int, optional
        For empty textures, the width of the texture buffer.
    height : int, optional
        For empty textures, the height of the texture buffer.
    tex_type : int
        Either GL_TEXTURE_2D or GL_TEXTURE_CUBE.
    data_format : int
        For now, just GL_FLOAT.
    """

    def __init__(
        self,
        name=None,
        sampler=None,
        source=None,
        source_channels=None,
        width=None,
        height=None,
        tex_type=GL_TEXTURE_2D,
        data_format=GL_UNSIGNED_BYTE,
    ):
        self.source_channels = source_channels
        self.name = name
        self.sampler = sampler
        self.source = source
        self.width = width
        self.height = height
        self.tex_type = tex_type
        self.data_format = data_format

        self._texid = None
        self._is_transparent = False

    @property
    def name(self):
        """str : The user-defined name of this object."""
        return self._name

    @name.setter
    def name(self, value):
        if value is not None:
            value = str(value)
        self._name = value

    @property
    def sampler(self):
        """:class:`Sampler` : The sampler used by this texture."""
        return self._sampler

    @sampler.setter
    def sampler(self, value):
        if value is None:
            value = Sampler()
        self._sampler = value

    @property
    def source(self):
        """(h,w,c) uint8 or float or :class:`PIL.Image.Image` : The image
        used in this texture.
        """
        return self._source

    @source.setter
    def source(self, value):
        if value is None:
            self._source = None
        else:
            self._source = format_texture_source(value, self.source_channels)
        self._is_transparent = False

    @property
    def source_channels(self):
        """str : The channels that were extracted from the original source."""
        return self._source_channels

    @source_channels.setter
    def source_channels(self, value):
        self._source_channels = value

    @property
    def width(self):
        """int : The width of the texture buffer."""
        return self._width

    @width.setter
    def width(self, value):
        self._width = value

    @property
    def height(self):
        """int : The height of the texture buffer."""
        return self._height

    @height.setter
    def height(self, value):
        self._height = value

    @property
    def tex_type(self):
        """int : The type of the texture."""
        return self._tex_type

    @tex_type.setter
    def tex_type(self, value):
        self._tex_type = value

    @property
    def data_format(self):
        """int : The format of the texture data."""
        return self._data_format

    @data_format.setter
    def data_format(self, value):
        self._data_format = value

    def is_transparent(self, cutoff=1.0):
        """bool : If True, the texture is partially transparent."""
        if self._is_transparent is None:
            self._is_transparent = False
            if self.source_channels == "RGBA" and self.source is not None:
                if np.any(self.source[:, :, 3] < cutoff):
                    self._is_transparent = True
        return self._is_transparent

    def delete(self):
        """Remove this texture from the OpenGL context."""
        self._unbind()
        self._remove_from_context()

    ##################
    # OpenGL code
    ##################
    def _add_to_context(self):
        if self._texid is not None:
            raise ValueError("Texture already loaded into OpenGL context")

        fmt = GL_DEPTH_COMPONENT
        if self.source_channels == "R":
            fmt = GL_RED
        elif self.source_channels == "RG" or self.source_channels == "GB":
            fmt = GL_RG
        elif self.source_channels == "RGB":
            fmt = GL_RGB
        elif self.source_channels == "RGBA":
            fmt = GL_RGBA

        # Generate the OpenGL texture
        self._texid = glGenTextures(1)
        glBindTexture(self.tex_type, self._texid)

        # Flip data for OpenGL buffer
        data = None
        width = self.width
        height = self.height
        if self.source is not None:
            data = np.ascontiguousarray(np.flip(self.source, axis=0).flatten())
            width = self.source.shape[1]
            height = self.source.shape[0]

        # Bind texture and generate mipmaps
        glTexImage2D(
            self.tex_type, 0, fmt, width, height, 0, fmt, self.data_format, data
        )
        if self.source is not None:
            glGenerateMipmap(self.tex_type)

        if self.sampler.magFilter is not None:
            glTexParameteri(
                self.tex_type, GL_TEXTURE_MAG_FILTER, self.sampler.magFilter
            )
        else:
            if self.source is not None:
                glTexParameteri(self.tex_type, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            else:
                glTexParameteri(self.tex_type, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        if self.sampler.minFilter is not None:
            glTexParameteri(
                self.tex_type, GL_TEXTURE_MIN_FILTER, self.sampler.minFilter
            )
        else:
            if self.source is not None:
                glTexParameteri(
                    self.tex_type, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR
                )
            else:
                glTexParameteri(self.tex_type, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

        glTexParameteri(self.tex_type, GL_TEXTURE_WRAP_S, self.sampler.wrapS)
        glTexParameteri(self.tex_type, GL_TEXTURE_WRAP_T, self.sampler.wrapT)
        border_color = 255 * np.ones(4).astype(np.uint8)
        if self.data_format == GL_FLOAT:
            border_color = np.ones(4).astype(np.float32)
        glTexParameterfv(self.tex_type, GL_TEXTURE_BORDER_COLOR, border_color)

        # Unbind texture
        glBindTexture(self.tex_type, 0)

    def _remove_from_context(self):
        if self._texid is not None:
            # TODO OPENGL BUG?
            # glDeleteTextures(1, [self._texid])
            glDeleteTextures([self._texid])
            self._texid = None

    def _in_context(self):
        return self._texid is not None

    def _bind(self):
        # TODO HANDLE INDEXING INTO OTHER UV's
        glBindTexture(self.tex_type, self._texid)

    def _unbind(self):
        glBindTexture(self.tex_type, 0)

    def _bind_as_depth_attachment(self):
        glFramebufferTexture2D(
            GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, self.tex_type, self._texid, 0
        )

    def _bind_as_color_attachment(self):
        glFramebufferTexture2D(
            GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, self.tex_type, self._texid, 0
        )

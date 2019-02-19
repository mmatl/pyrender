"""Virtual cameras compliant with the glTF 2.0 specification as described at
https://github.com/KhronosGroup/glTF/tree/master/specification/2.0#reference-camera

Author: Matthew Matl
"""
import abc
import numpy as np
import six

from .constants import DEFAULT_Z_NEAR, DEFAULT_Z_FAR


@six.add_metaclass(abc.ABCMeta)
class Camera(object):
    """Abstract base class for all cameras.

    Note
    ----
    Camera poses are specified in the OpenGL format,
    where the z axis points away from the view direction and the
    x and y axes point to the right and up in the image plane, respectively.

    Parameters
    ----------
    name : str, optional
        The user-defined name of this object.
    znear : float
        The floating-point distance to the near clipping plane.
    zfar : float
        The floating-point distance to the far clipping plane.
        ``zfar`` must be greater than ``znear``.
    """

    def __init__(self,
                 name=None,
                 znear=DEFAULT_Z_NEAR,
                 zfar=DEFAULT_Z_FAR):
        self.name = name
        self.znear = znear
        self.zfar = zfar

    @property
    def name(self):
        """str : The user-defined name of this object.
        """
        return self._name

    @name.setter
    def name(self, value):
        if value is not None:
            value = str(value)
        self._name = value

    @property
    def znear(self):
        """float : The distance to the near clipping plane.
        """
        return self._znear

    @znear.setter
    def znear(self, value):
        if value < 0:
            raise ValueError('z-near must be >= 0.0')
        self._znear = float(value)

    @property
    def zfar(self):
        """float : The distance to the far clipping plane.
        """
        return self._zfar

    @zfar.setter
    def zfar(self, value):
        if value is not None:
            if value <= 0 or value <= self.znear:
                raise ValueError('zfar must be >0 and >znear')
            else:
                value = float(value)

        self._zfar = value

    @abc.abstractmethod
    def get_projection_matrix(self, width=None, height=None):
        """Return the OpenGL projection matrix for this camera.

        Parameters
        ----------
        width : int
            Width of the current viewport, in pixels.
        height : int
            Height of the current viewport, in pixels.
        """
        pass


class PerspectiveCamera(Camera):
    """A perspective camera for perspective projection.

    Parameters
    ----------
    name : str, optional
        The user-defined name of this object.
    znear : float
        The floating-point distance to the near clipping plane.
    zfar : float
        The floating-point distance to the far clipping plane.
        ``zfar`` must be greater than ``znear``.
    yfov : float
        The floating-point vertical field of view in radians.
    aspectRatio : float
        The floating-point aspect ratio of the field of view.
    """

    def __init__(self,
                 name=None,
                 znear=DEFAULT_Z_NEAR,
                 zfar=DEFAULT_Z_FAR,
                 yfov=None,
                 aspectRatio=None):
        super(PerspectiveCamera, self).__init__(
            name=name,
            znear=znear,
            zfar=zfar,
        )

        self.yfov = yfov
        self.aspectRatio = aspectRatio

    @property
    def yfov(self):
        """float : The vertical field of view in radians.
        """
        return self._yfov

    @yfov.setter
    def yfov(self, value):
        if value <= 0.0:
            raise ValueError('Field of view must be positive')
        self._yfov = float(value)

    @property
    def aspectRatio(self):
        """float : The ratio of the width to the height of the field of view.
        """
        return self._aspectRatio

    @aspectRatio.setter
    def aspectRatio(self, value):
        if value is None:
            self._aspectRatio = None
            return
        if value <= 0.0:
            raise ValueError('Aspect ratio must be positive')
        self._aspectRatio = float(value)

    def get_projection_matrix(self, width=None, height=None):
        """Return the OpenGL projection matrix for this camera.

        Parameters
        ----------
        width : int
            Width of the current viewport, in pixels.
        height : int
            Height of the current viewport, in pixels.
        """
        aspect_ratio = self.aspectRatio
        if aspect_ratio is None:
            if width is None or height is None:
                raise ValueError('Aspect ratio of camera must be defined')
            aspect_ratio = float(width) / float(height)

        a = aspect_ratio
        t = np.tan(self.yfov / 2.0)
        n = self.znear
        f = self.zfar

        P = np.zeros((4,4))
        P[0][0] = 1.0 / (a * t)
        P[1][1] = 1.0 / t
        P[3][2] = -1.0

        if f is None:
            P[2][2] = -1.0
            P[2][3] = -2.0 * n
        else:
            P[2][2] = (f + n) / (n - f)
            P[2][3] = (2 * f * n) / (n - f)

        return P


class OrthographicCamera(Camera):
    """A perspective camera for perspective projection.

    Parameters
    ----------
    name : str, optional
        The user-defined name of this object.
    znear : float
        The floating-point distance to the near clipping plane.
    zfar : float
        The floating-point distance to the far clipping plane.
        ``zfar`` must be greater than ``znear``.
    xmag : float
        The floating-point horizontal magnification of the view.
    ymag : float
        The floating-point vertical magnification of the view.
    """

    def __init__(self,
                 name=None,
                 znear=DEFAULT_Z_NEAR,
                 zfar=DEFAULT_Z_FAR,
                 xmag=None,
                 ymag=None):
        super(OrthographicCamera, self).__init__(
            name=name,
            znear=znear,
            zfar=zfar
        )

        self.xmag = xmag
        self.ymag = ymag

    @property
    def xmag(self):
        """float : The horizontal magnification of the view.
        """
        return self._xmag

    @xmag.setter
    def xmag(self, value):
        if value <= 0.0:
            raise ValueError('X magnification must be positive')
        self._xmag = float(value)

    @property
    def ymag(self):
        """float : The vertical magnification of the view.
        """
        return self._ymag

    @ymag.setter
    def ymag(self, value):
        if value <= 0.0:
            raise ValueError('Y magnification must be positive')
        self._ymag = float(value)

    def get_projection_matrix(self, width=None, height=None):
        """Return the OpenGL projection matrix for this camera.

        Parameters
        ----------
        width : int
            Width of the current viewport, in pixels.
        height : int
            Height of the current viewport, in pixels.
        """
        n = self.znear
        f = self.zfar
        P = np.zeros((4,4))
        P[0][0] = 1.0 / self.xmag
        P[1][1] = 1.0 / self.ymag
        P[2][2] = 2.0 / (n - f)
        P[2][3] = (f + n) / (n - f)
        P[3][3] = 1.0
        return P


__all__ = ['Camera', 'PerspectiveCamera', 'OrthographicCamera']

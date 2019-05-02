import numpy as np
import pytest

from pyrender import PerspectiveCamera, OrthographicCamera


def test_perspective_camera():

    # Set up constants
    znear = 0.05
    zfar = 100
    yfov = np.pi / 3.0
    width = 1000.0
    height = 500.0
    aspectRatio = 640.0 / 480.0

    # Test basics
    with pytest.raises(TypeError):
        p = PerspectiveCamera()

    p = PerspectiveCamera(yfov=yfov)
    assert p.yfov == yfov
    assert p.znear == 0.05
    assert p.zfar is None
    assert p.aspectRatio is None
    p.name = 'asdf'
    p.name = None

    with pytest.raises(ValueError):
        p.yfov = 0.0

    with pytest.raises(ValueError):
        p.yfov = -1.0

    with pytest.raises(ValueError):
        p.znear = -1.0

    p.znear = 0.0
    p.znear = 0.05
    p.zfar = 100.0
    assert p.zfar == 100.0

    with pytest.raises(ValueError):
        p.zfar = 0.03

    with pytest.raises(ValueError):
        p.zfar = 0.05

    p.aspectRatio = 10.0
    assert p.aspectRatio == 10.0

    with pytest.raises(ValueError):
        p.aspectRatio = 0.0

    with pytest.raises(ValueError):
        p.aspectRatio = -1.0

    # Test matrix getting/setting

    # NF
    p.znear = 0.05
    p.zfar = 100
    p.aspectRatio = None

    with pytest.raises(ValueError):
        p.get_projection_matrix()

    assert np.allclose(
        p.get_projection_matrix(width, height),
        np.array([
            [1.0 / (width / height * np.tan(yfov / 2.0)), 0.0, 0.0, 0.0],
            [0.0, 1.0 / np.tan(yfov / 2.0), 0.0, 0.0],
            [0.0, 0.0, (zfar + znear) / (znear - zfar),
                (2 * zfar * znear) / (znear - zfar)],
            [0.0, 0.0, -1.0, 0.0]
        ])
    )

    # NFA
    p.aspectRatio = aspectRatio
    assert np.allclose(
        p.get_projection_matrix(width, height),
        np.array([
            [1.0 / (aspectRatio * np.tan(yfov / 2.0)), 0.0, 0.0, 0.0],
            [0.0, 1.0 / np.tan(yfov / 2.0), 0.0, 0.0],
            [0.0, 0.0, (zfar + znear) / (znear - zfar),
                (2 * zfar * znear) / (znear - zfar)],
            [0.0, 0.0, -1.0, 0.0]
        ])
    )
    assert np.allclose(
        p.get_projection_matrix(), p.get_projection_matrix(width, height)
    )

    # N
    p.zfar = None
    p.aspectRatio = None
    assert np.allclose(
        p.get_projection_matrix(width, height),
        np.array([
            [1.0 / (width / height * np.tan(yfov / 2.0)), 0.0, 0.0, 0.0],
            [0.0, 1.0 / np.tan(yfov / 2.0), 0.0, 0.0],
            [0.0, 0.0, -1.0, -2.0 * znear],
            [0.0, 0.0, -1.0, 0.0]
        ])
    )


def test_orthographic_camera():
    xm = 1.0
    ym = 2.0
    n = 0.05
    f = 100.0

    with pytest.raises(TypeError):
        c = OrthographicCamera()

    c = OrthographicCamera(xmag=xm, ymag=ym)

    assert c.xmag == xm
    assert c.ymag == ym
    assert c.znear == 0.05
    assert c.zfar == 100.0
    assert c.name is None

    with pytest.raises(TypeError):
        c.ymag = None

    with pytest.raises(ValueError):
        c.ymag = 0.0

    with pytest.raises(ValueError):
        c.ymag = -1.0

    with pytest.raises(TypeError):
        c.xmag = None

    with pytest.raises(ValueError):
        c.xmag = 0.0

    with pytest.raises(ValueError):
        c.xmag = -1.0

    with pytest.raises(TypeError):
        c.znear = None

    with pytest.raises(ValueError):
        c.znear = 0.0

    with pytest.raises(ValueError):
        c.znear = -1.0

    with pytest.raises(ValueError):
        c.zfar = 0.01

    assert np.allclose(
        c.get_projection_matrix(),
        np.array([
            [1.0 / xm, 0, 0, 0],
            [0, 1.0 / ym, 0, 0],
            [0, 0, 2.0 / (n - f), (f + n) / (n - f)],
            [0, 0, 0, 1.0]
        ])
    )

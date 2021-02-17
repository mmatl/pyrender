import numpy as np
import pytest

from pyrender import (DirectionalLight, SpotLight, PointLight, Texture,
                      PerspectiveCamera, OrthographicCamera)
from pyrender.constants import SHADOW_TEX_SZ


def test_directional_light():

    d = DirectionalLight()
    assert d.name is None
    assert np.all(d.color == 1.0)
    assert d.intensity == 1.0

    d.name = 'direc'
    with pytest.raises(ValueError):
        d.color = None
    with pytest.raises(TypeError):
        d.intensity = None

    d = DirectionalLight(color=[0.0, 0.0, 0.0])
    assert np.all(d.color == 0.0)

    d._generate_shadow_texture()
    st = d.shadow_texture
    assert isinstance(st, Texture)
    assert st.width == st.height == SHADOW_TEX_SZ

    sc = d._get_shadow_camera(scene_scale=5.0)
    assert isinstance(sc, OrthographicCamera)
    assert sc.xmag == sc.ymag == 5.0
    assert sc.znear == 0.01 * 5.0
    assert sc.zfar == 10 * 5.0


def test_spot_light():

    s = SpotLight()
    assert s.name is None
    assert np.all(s.color == 1.0)
    assert s.intensity == 1.0
    assert s.innerConeAngle == 0.0
    assert s.outerConeAngle == np.pi / 4.0
    assert s.range is None

    with pytest.raises(ValueError):
        s.range = -1.0

    with pytest.raises(ValueError):
        s.range = 0.0

    with pytest.raises(ValueError):
        s.innerConeAngle = -1.0

    with pytest.raises(ValueError):
        s.innerConeAngle = np.pi / 3.0

    with pytest.raises(ValueError):
        s.outerConeAngle = -1.0

    with pytest.raises(ValueError):
        s.outerConeAngle = np.pi

    s.range = 5.0
    s.outerConeAngle = np.pi / 2 - 0.05
    s.innerConeAngle = np.pi / 3
    s.innerConeAngle = 0.0
    s.outerConeAngle = np.pi / 4.0

    s._generate_shadow_texture()
    st = s.shadow_texture
    assert isinstance(st, Texture)
    assert st.width == st.height == SHADOW_TEX_SZ

    sc = s._get_shadow_camera(scene_scale=5.0)
    assert isinstance(sc, PerspectiveCamera)
    assert sc.znear == 0.01 * 5.0
    assert sc.zfar == 10 * 5.0
    assert sc.aspectRatio == 1.0
    assert np.allclose(sc.yfov, np.pi / 16.0 * 9.0)  # Plus pi / 16


def test_point_light():

    s = PointLight()
    assert s.name is None
    assert np.all(s.color == 1.0)
    assert s.intensity == 1.0
    assert s.range is None

    with pytest.raises(ValueError):
        s.range = -1.0

    with pytest.raises(ValueError):
        s.range = 0.0

    s.range = 5.0

    with pytest.raises(NotImplementedError):
        s._generate_shadow_texture()

    with pytest.raises(NotImplementedError):
        s._get_shadow_camera(scene_scale=5.0)

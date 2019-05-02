import numpy as np
import pytest
from trimesh import transformations

from pyrender import (DirectionalLight, PerspectiveCamera, Mesh, Node)


def test_nodes():

    x = Node()
    assert x.name is None
    assert x.camera is None
    assert x.children == []
    assert x.skin is None
    assert np.allclose(x.matrix, np.eye(4))
    assert x.mesh is None
    assert np.allclose(x.rotation, [0,0,0,1])
    assert np.allclose(x.scale, np.ones(3))
    assert np.allclose(x.translation, np.zeros(3))
    assert x.weights is None
    assert x.light is None

    x.name = 'node'

    # Test node light/camera/mesh tests
    c = PerspectiveCamera(yfov=2.0)
    m = Mesh([])
    d = DirectionalLight()
    x.camera = c
    assert x.camera == c
    with pytest.raises(TypeError):
        x.camera = m
        x.camera = d
    x.camera = None
    x.mesh = m
    assert x.mesh == m
    with pytest.raises(TypeError):
        x.mesh = c
        x.mesh = d
    x.light = d
    assert x.light == d
    with pytest.raises(TypeError):
        x.light = m
        x.light = c

    # Test transformations getters/setters/etc...
    # Set up test values
    x = np.array([1.0, 0.0, 0.0])
    y = np.array([0.0, 1.0, 0.0])
    t = np.array([1.0, 2.0, 3.0])
    s = np.array([0.5, 2.0, 1.0])

    Mx = transformations.rotation_matrix(np.pi / 2.0, x)
    qx = np.roll(transformations.quaternion_about_axis(np.pi / 2.0, x), -1)
    Mxt = Mx.copy()
    Mxt[:3,3] = t
    S = np.eye(4)
    S[:3,:3] = np.diag(s)
    Mxts = Mxt.dot(S)

    My = transformations.rotation_matrix(np.pi / 2.0, y)
    qy = np.roll(transformations.quaternion_about_axis(np.pi / 2.0, y), -1)
    Myt = My.copy()
    Myt[:3,3] = t

    x = Node(matrix=Mx)
    assert np.allclose(x.matrix, Mx)
    assert np.allclose(x.rotation, qx)
    assert np.allclose(x.translation, np.zeros(3))
    assert np.allclose(x.scale, np.ones(3))

    x.matrix = My
    assert np.allclose(x.matrix, My)
    assert np.allclose(x.rotation, qy)
    assert np.allclose(x.translation, np.zeros(3))
    assert np.allclose(x.scale, np.ones(3))
    x.translation = t
    assert np.allclose(x.matrix, Myt)
    assert np.allclose(x.rotation, qy)
    x.rotation = qx
    assert np.allclose(x.matrix, Mxt)
    x.scale = s
    assert np.allclose(x.matrix, Mxts)

    x = Node(matrix=Mxt)
    assert np.allclose(x.matrix, Mxt)
    assert np.allclose(x.rotation, qx)
    assert np.allclose(x.translation, t)
    assert np.allclose(x.scale, np.ones(3))

    x = Node(matrix=Mxts)
    assert np.allclose(x.matrix, Mxts)
    assert np.allclose(x.rotation, qx)
    assert np.allclose(x.translation, t)
    assert np.allclose(x.scale, s)

    # Individual element getters
    x.scale[0] = 0
    assert np.allclose(x.scale[0], 0)

    x.translation[0] = 0
    assert np.allclose(x.translation[0], 0)

    x.matrix = np.eye(4)
    x.matrix[0,0] = 500
    assert x.matrix[0,0] == 1.0

    # Failures
    with pytest.raises(ValueError):
        x.matrix = 5 * np.eye(4)
    with pytest.raises(ValueError):
        x.matrix = np.eye(5)
    with pytest.raises(ValueError):
        x.matrix = np.eye(4).dot([5,1,1,1])
    with pytest.raises(ValueError):
        x.rotation = np.array([1,2])
    with pytest.raises(ValueError):
        x.rotation = np.array([1,2,3])
    with pytest.raises(ValueError):
        x.rotation = np.array([1,2,3,4])
    with pytest.raises(ValueError):
        x.translation = np.array([1,2,3,4])
    with pytest.raises(ValueError):
        x.scale = np.array([1,2,3,4])

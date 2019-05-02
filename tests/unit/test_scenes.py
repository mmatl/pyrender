import numpy as np
import pytest
import trimesh

from pyrender import (Mesh, PerspectiveCamera, DirectionalLight,
                      SpotLight, PointLight, Scene, Node, OrthographicCamera)


def test_scenes():

    # Basics
    s = Scene()
    assert np.allclose(s.bg_color, np.ones(4))
    assert np.allclose(s.ambient_light, np.zeros(3))
    assert len(s.nodes) == 0
    assert s.name is None
    s.name = 'asdf'
    s.bg_color = None
    s.ambient_light = None
    assert np.allclose(s.bg_color, np.ones(4))
    assert np.allclose(s.ambient_light, np.zeros(3))

    assert s.nodes == set()
    assert s.cameras == set()
    assert s.lights == set()
    assert s.point_lights == set()
    assert s.spot_lights == set()
    assert s.directional_lights == set()
    assert s.meshes == set()
    assert s.camera_nodes == set()
    assert s.light_nodes == set()
    assert s.point_light_nodes == set()
    assert s.spot_light_nodes == set()
    assert s.directional_light_nodes == set()
    assert s.mesh_nodes == set()
    assert s.main_camera_node is None
    assert np.all(s.bounds == 0)
    assert np.all(s.centroid == 0)
    assert np.all(s.extents == 0)
    assert np.all(s.scale == 0)

    # From trimesh scene
    tms = trimesh.load('tests/data/WaterBottle.glb')
    s = Scene.from_trimesh_scene(tms)
    assert len(s.meshes) == 1
    assert len(s.mesh_nodes) == 1

    # Test bg color formatting
    s = Scene(bg_color=[0, 1.0, 0])
    assert np.allclose(s.bg_color, np.array([0.0, 1.0, 0.0, 1.0]))

    # Test constructor for nodes
    n1 = Node()
    n2 = Node()
    n3 = Node()
    nodes = [n1, n2, n3]
    s = Scene(nodes=nodes)
    n1.children.append(n2)
    s = Scene(nodes=nodes)
    n3.children.append(n2)
    with pytest.raises(ValueError):
        s = Scene(nodes=nodes)
    n3.children = []
    n2.children.append(n3)
    n3.children.append(n2)
    with pytest.raises(ValueError):
        s = Scene(nodes=nodes)

    # Test node accessors
    n1 = Node()
    n2 = Node()
    n3 = Node()
    nodes = [n1, n2]
    s = Scene(nodes=nodes)
    assert s.has_node(n1)
    assert s.has_node(n2)
    assert not s.has_node(n3)

    # Test node poses
    for n in nodes:
        assert np.allclose(s.get_pose(n), np.eye(4))
    with pytest.raises(ValueError):
        s.get_pose(n3)
    with pytest.raises(ValueError):
        s.set_pose(n3, np.eye(4))
    tf = np.eye(4)
    tf[:3,3] = np.ones(3)
    s.set_pose(n1, tf)
    assert np.allclose(s.get_pose(n1), tf)
    assert np.allclose(s.get_pose(n2), np.eye(4))

    nodes = [n1, n2, n3]
    tf2 = np.eye(4)
    tf2[:3,:3] = np.diag([-1,-1,1])
    n1.children.append(n2)
    n1.matrix = tf
    n2.matrix = tf2
    s = Scene(nodes=nodes)
    assert np.allclose(s.get_pose(n1), tf)
    assert np.allclose(s.get_pose(n2), tf.dot(tf2))
    assert np.allclose(s.get_pose(n3), np.eye(4))

    n1 = Node()
    n2 = Node()
    n3 = Node()
    n1.children.append(n2)
    s = Scene()
    s.add_node(n1)
    with pytest.raises(ValueError):
        s.add_node(n2)
    s.set_pose(n1, tf)
    assert np.allclose(s.get_pose(n1), tf)
    assert np.allclose(s.get_pose(n2), tf)
    s.set_pose(n2, tf2)
    assert np.allclose(s.get_pose(n2), tf.dot(tf2))

    # Test node removal
    n1 = Node()
    n2 = Node()
    n3 = Node()
    n1.children.append(n2)
    n2.children.append(n3)
    s = Scene(nodes=[n1, n2, n3])
    s.remove_node(n2)
    assert len(s.nodes) == 1
    assert n1 in s.nodes
    assert len(n1.children) == 0
    assert len(n2.children) == 1
    s.add_node(n2, parent_node=n1)
    assert len(n1.children) == 1
    n1.matrix = tf
    n3.matrix = tf2
    assert np.allclose(s.get_pose(n3), tf.dot(tf2))

    # Now test ADD function
    s = Scene()
    m = Mesh([], name='m')
    cp = PerspectiveCamera(yfov=2.0)
    co = OrthographicCamera(xmag=1.0, ymag=1.0)
    dl = DirectionalLight()
    pl = PointLight()
    sl = SpotLight()

    n1 = s.add(m, name='mn')
    assert n1.mesh == m
    assert len(s.nodes) == 1
    assert len(s.mesh_nodes) == 1
    assert n1 in s.mesh_nodes
    assert len(s.meshes) == 1
    assert m in s.meshes
    assert len(s.get_nodes(node=n2)) == 0
    n2 = s.add(m, pose=tf)
    assert len(s.nodes) == len(s.mesh_nodes) == 2
    assert len(s.meshes) == 1
    assert len(s.get_nodes(node=n1)) == 1
    assert len(s.get_nodes(node=n1, name='mn')) == 1
    assert len(s.get_nodes(name='mn')) == 1
    assert len(s.get_nodes(obj=m)) == 2
    assert len(s.get_nodes(obj=m, obj_name='m')) == 2
    assert len(s.get_nodes(obj=co)) == 0
    nsl = s.add(sl, name='sln')
    npl = s.add(pl, parent_name='sln')
    assert nsl.children[0] == npl
    ndl = s.add(dl, parent_node=npl)
    assert npl.children[0] == ndl
    nco = s.add(co)
    ncp = s.add(cp)

    assert len(s.light_nodes) == len(s.lights) == 3
    assert len(s.point_light_nodes) == len(s.point_lights) == 1
    assert npl in s.point_light_nodes
    assert len(s.spot_light_nodes) == len(s.spot_lights) == 1
    assert nsl in s.spot_light_nodes
    assert len(s.directional_light_nodes) == len(s.directional_lights) == 1
    assert ndl in s.directional_light_nodes
    assert len(s.cameras) == len(s.camera_nodes) == 2
    assert s.main_camera_node == nco
    s.main_camera_node = ncp
    s.remove_node(ncp)
    assert len(s.cameras) == len(s.camera_nodes) == 1
    assert s.main_camera_node == nco
    s.remove_node(n2)
    assert len(s.meshes) == 1
    s.remove_node(n1)
    assert len(s.meshes) == 0
    s.remove_node(nsl)
    assert len(s.lights) == 0
    s.remove_node(nco)
    assert s.main_camera_node is None

    s.add_node(n1)
    s.clear()
    assert len(s.nodes) == 0

    # Trigger final errors
    with pytest.raises(ValueError):
        s.main_camera_node = None
    with pytest.raises(ValueError):
        s.main_camera_node = ncp
    with pytest.raises(ValueError):
        s.add(m, parent_node=n1)
    with pytest.raises(ValueError):
        s.add(m, name='asdf')
        s.add(m, name='asdf')
        s.add(m, parent_name='asdf')
    with pytest.raises(ValueError):
        s.add(m, parent_name='asfd')
    with pytest.raises(TypeError):
        s.add(None)

    s.clear()
    # Test bounds
    m1 = Mesh.from_trimesh(trimesh.creation.box())
    m2 = Mesh.from_trimesh(trimesh.creation.box())
    m3 = Mesh.from_trimesh(trimesh.creation.box())
    n1 = Node(mesh=m1)
    n2 = Node(mesh=m2, translation=[1.0, 0.0, 0.0])
    n3 = Node(mesh=m3, translation=[0.5, 0.0, 1.0])
    s.add_node(n1)
    s.add_node(n2)
    s.add_node(n3)
    assert np.allclose(s.bounds, [[-0.5, -0.5, -0.5], [1.5, 0.5, 1.5]])
    s.clear()
    s.add_node(n1)
    s.add_node(n2, parent_node=n1)
    s.add_node(n3, parent_node=n2)
    assert np.allclose(s.bounds, [[-0.5, -0.5, -0.5], [2.0, 0.5, 1.5]])
    tf = np.eye(4)
    tf[:3,3] = np.ones(3)
    s.set_pose(n3, tf)
    assert np.allclose(s.bounds, [[-0.5, -0.5, -0.5], [2.5, 1.5, 1.5]])
    s.remove_node(n2)
    assert np.allclose(s.bounds, [[-0.5, -0.5, -0.5], [0.5, 0.5, 0.5]])
    s.clear()
    assert np.allclose(s.bounds, 0.0)

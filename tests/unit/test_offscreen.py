import numpy as np
import trimesh

from pyrender import (OffscreenRenderer, PerspectiveCamera, DirectionalLight,
                      SpotLight, Mesh, Node, Scene)


def test_offscreen_renderer(tmpdir):

    # Fuze trimesh
    fuze_trimesh = trimesh.load('examples/models/fuze.obj')
    fuze_mesh = Mesh.from_trimesh(fuze_trimesh)

    # Drill trimesh
    drill_trimesh = trimesh.load('examples/models/drill.obj')
    drill_mesh = Mesh.from_trimesh(drill_trimesh)
    drill_pose = np.eye(4)
    drill_pose[0,3] = 0.1
    drill_pose[2,3] = -np.min(drill_trimesh.vertices[:,2])

    # Wood trimesh
    wood_trimesh = trimesh.load('examples/models/wood.obj')
    wood_mesh = Mesh.from_trimesh(wood_trimesh)

    # Water bottle trimesh
    bottle_gltf = trimesh.load('examples/models/WaterBottle.glb')
    bottle_trimesh = bottle_gltf.geometry[list(bottle_gltf.geometry.keys())[0]]
    bottle_mesh = Mesh.from_trimesh(bottle_trimesh)
    bottle_pose = np.array([
        [1.0, 0.0, 0.0, 0.1],
        [0.0, 0.0, -1.0, -0.16],
        [0.0, 1.0, 0.0, 0.13],
        [0.0, 0.0, 0.0, 1.0],
    ])

    boxv_trimesh = trimesh.creation.box(extents=0.1 * np.ones(3))
    boxv_vertex_colors = np.random.uniform(size=(boxv_trimesh.vertices.shape))
    boxv_trimesh.visual.vertex_colors = boxv_vertex_colors
    boxv_mesh = Mesh.from_trimesh(boxv_trimesh, smooth=False)
    boxf_trimesh = trimesh.creation.box(extents=0.1 * np.ones(3))
    boxf_face_colors = np.random.uniform(size=boxf_trimesh.faces.shape)
    boxf_trimesh.visual.face_colors = boxf_face_colors
    # Instanced
    poses = np.tile(np.eye(4), (2,1,1))
    poses[0,:3,3] = np.array([-0.1, -0.10, 0.05])
    poses[1,:3,3] = np.array([-0.15, -0.10, 0.05])
    boxf_mesh = Mesh.from_trimesh(boxf_trimesh, poses=poses, smooth=False)

    points = trimesh.creation.icosphere(radius=0.05).vertices
    point_colors = np.random.uniform(size=points.shape)
    points_mesh = Mesh.from_points(points, colors=point_colors)

    direc_l = DirectionalLight(color=np.ones(3), intensity=1.0)
    spot_l = SpotLight(color=np.ones(3), intensity=10.0,
                       innerConeAngle=np.pi / 16, outerConeAngle=np.pi / 6)

    cam = PerspectiveCamera(yfov=(np.pi / 3.0))
    cam_pose = np.array([
        [0.0, -np.sqrt(2) / 2, np.sqrt(2) / 2, 0.5],
        [1.0, 0.0, 0.0, 0.0],
        [0.0, np.sqrt(2) / 2, np.sqrt(2) / 2, 0.4],
        [0.0, 0.0, 0.0, 1.0]
    ])

    scene = Scene(ambient_light=np.array([0.02, 0.02, 0.02]))

    fuze_node = Node(mesh=fuze_mesh, translation=np.array([
        0.1, 0.15, -np.min(fuze_trimesh.vertices[:,2])
    ]))
    scene.add_node(fuze_node)
    boxv_node = Node(mesh=boxv_mesh, translation=np.array([-0.1, 0.10, 0.05]))
    scene.add_node(boxv_node)
    boxf_node = Node(mesh=boxf_mesh)
    scene.add_node(boxf_node)

    _ = scene.add(drill_mesh, pose=drill_pose)
    _ = scene.add(bottle_mesh, pose=bottle_pose)
    _ = scene.add(wood_mesh)
    _ = scene.add(direc_l, pose=cam_pose)
    _ = scene.add(spot_l, pose=cam_pose)
    _ = scene.add(points_mesh)

    _ = scene.add(cam, pose=cam_pose)

    r = OffscreenRenderer(viewport_width=640, viewport_height=480)
    color, depth = r.render(scene)

    assert color.shape == (480, 640, 3)
    assert depth.shape == (480, 640)
    assert np.max(depth.data) > 0.05
    assert np.count_nonzero(depth.data) > (0.2 * depth.size)
    r.delete()

# Pyrender

[![Build Status](https://travis-ci.org/mmatl/pyrender.svg?branch=master)](https://travis-ci.org/mmatl/pyrender)
[![Documentation Status](https://readthedocs.org/projects/pyrender/badge/?version=latest)](https://pyrender.readthedocs.io/en/latest/?badge=latest)

Pyrender is a pure Python (2.7 - 3.3+) library for visualizing and rendering
3D scenes using OpenGL and physically-based rendering (PBR).
It is designed around the [glTF 2.0 specification from
Khronos](https://www.khronos.org/gltf/) and is mostly compliant with that
specification.
Pyrender is designed to lightweight, easy to install, and simple to use so that
you can get started visualizing 3D data instantly.

Extensive API documentation is provided [here](https://pyrender.readthedocs.io/en/latest/).

<p align="center">
  <img src="https://github.com/mmatl/pyrender/blob/master/docs/source/_static/rotation.gif?raw=true" alt="GIF of Viewer"/>
</p>

## Installation
You can install pyrender directly from pip.

```bash
pip install pyrender
```

If you plan to use pyrender for long runs of generating data, I'd recommend
installing my fork of pyglet first, as the existing version has a memory leak:

```bash
git clone https://github.com/mmatl/pyglet.git
cd pyglet
python setup.py install
```

## Features

Despite being lightweight, pyrender has lots of features, including:

* Simple interoperation with the amazing [trimesh](https://github.com/mikedh/trimesh) project.
* An easy-to-use scene viewer with support for animation, showing face and vertex
normals, toggling lighting conditions, and saving images and GIFs.
* An offscreen rendering module for generating images of 3D scenes.
* Support for several types of lighting, including point, spot, and directional
lights.
* Shadows (for directional and spot lights only, for now).
* Metallic-roughness materials for physically-based rendering, including several
types of texture and normal mapping.
* Transparency.
* Depth and color image generation.

## Sample Usage
Sample usage of the library is shown below:

```python
import os
import numpy as np
import trimesh

from pyrender import PerspectiveCamera,\
                     DirectionalLight, SpotLight, PointLight,\
                     MetallicRoughnessMaterial,\
                     Primitive, Mesh, Node, Scene,\
                     Viewer, OffscreenRenderer

#==============================================================================
# Mesh creation
#==============================================================================

#------------------------------------------------------------------------------
# Creating textured meshes from trimeshes
#------------------------------------------------------------------------------

# Fuze trimesh
fuze_trimesh = trimesh.load('./models/fuze.obj', process=False)
fuze_mesh = Mesh.from_trimesh(fuze_trimesh)

# Drill trimesh
drill_trimesh = trimesh.load('./models/drill.obj', process=False)
drill_mesh = Mesh.from_trimesh(drill_trimesh)
drill_pose = np.eye(4)
drill_pose[0,3] = 0.1
drill_pose[2,3] = -np.min(drill_trimesh.vertices[:,2])

# Wood trimesh
wood_trimesh = trimesh.load('./models/wood.obj', process=False)
wood_mesh = Mesh.from_trimesh(wood_trimesh)

# Water bottle trimesh
bottle_gltf = trimesh.load('./models/WaterBottle.glb', process=False)
bottle_trimesh = bottle_gltf.geometry[list(bottle_gltf.geometry.keys())[0]]
bottle_mesh = Mesh.from_trimesh(bottle_trimesh)
bottle_pose = np.array([
    [1.0, 0.0,  0.0, 0.1],
    [0.0, 0.0, -1.0, -0.16],
    [0.0, 1.0,  0.0, 0.13],
    [0.0, 0.0,  0.0, 1.0],
])

#------------------------------------------------------------------------------
# Creating meshes with per-vertex colors
#------------------------------------------------------------------------------
boxv_trimesh = trimesh.creation.box(extents=0.1*np.ones(3))
boxv_vertex_colors = np.random.uniform(size=(boxv_trimesh.vertices.shape))
boxv_trimesh.visual.vertex_colors = boxv_vertex_colors
boxv_mesh = Mesh.from_trimesh(boxv_trimesh, smooth=False)

#------------------------------------------------------------------------------
# Creating meshes with per-face colors
#------------------------------------------------------------------------------
boxf_trimesh = trimesh.creation.box(extents=0.1*np.ones(3))
boxf_face_colors = np.random.uniform(size=boxf_trimesh.faces.shape)
boxf_trimesh.visual.face_colors = boxf_face_colors
boxf_mesh = Mesh.from_trimesh(boxf_trimesh, smooth=False)

#------------------------------------------------------------------------------
# Creating meshes from point clouds
#------------------------------------------------------------------------------
points = trimesh.creation.icosphere(radius=0.05).vertices
point_colors = np.random.uniform(size=points.shape)
points_mesh = Mesh.from_points(points, colors=point_colors)

#==============================================================================
# Light creation
#==============================================================================

direc_l = DirectionalLight(color=np.ones(3), intensity=1.0)
spot_l = SpotLight(color=np.ones(3), intensity=10.0,
                   innerConeAngle=np.pi/16, outerConeAngle=np.pi/6)
point_l = PointLight(color=np.ones(3), intensity=10.0)

#==============================================================================
# Camera creation
#==============================================================================

cam = PerspectiveCamera(yfov=(np.pi / 3.0))
cam_pose = np.array([
    [0.0,  -np.sqrt(2)/2, np.sqrt(2)/2, 0.5],
    [1.0, 0.0,           0.0,           0.0],
    [0.0,  np.sqrt(2)/2,  np.sqrt(2)/2, 0.4],
    [0.0,  0.0,           0.0,          1.0]
])

#==============================================================================
# Scene creation
#==============================================================================

scene = Scene(ambient_light=np.array([0.02, 0.02, 0.02]))

#==============================================================================
# Adding objects to the scene
#==============================================================================

#------------------------------------------------------------------------------
# By manually creating nodes
#------------------------------------------------------------------------------
fuze_node = Node(mesh=fuze_mesh, translation=np.array([0.1, 0.15, -np.min(fuze_trimesh.vertices[:,2])]))
scene.add_node(fuze_node)
boxv_node = Node(mesh=boxv_mesh, translation=np.array([-0.1, 0.10, 0.05]))
scene.add_node(boxv_node)
boxf_node = Node(mesh=boxf_mesh, translation=np.array([-0.1, -0.10, 0.05]))
scene.add_node(boxf_node)

#------------------------------------------------------------------------------
# By using the add() utility function
#------------------------------------------------------------------------------
drill_node = scene.add(drill_mesh, pose=drill_pose)
bottle_node = scene.add(bottle_mesh, pose=bottle_pose)
wood_node = scene.add(wood_mesh)
direc_l_node = scene.add(direc_l, pose=cam_pose)
spot_l_node = scene.add(spot_l, pose=cam_pose)

#==============================================================================
# Using the viewer with a default camera
#==============================================================================

v = Viewer(scene, shadows=True)

#==============================================================================
# Using the viewer with a pre-specified camera
#==============================================================================
cam_node = scene.add(cam, pose=cam_pose)
v = Viewer(scene, central_node=drill_node)

#==============================================================================
# Rendering offscreen from that camera
#==============================================================================

r = OffscreenRenderer(viewport_width=640*2, viewport_height=480*2)
color, depth = r.render(scene)
r.delete()

import matplotlib.pyplot as plt
plt.figure()
plt.imshow(color)
plt.show()
```

## Viewer Keyboard and Mouse Controls

When using the viewer, the basic controls for moving about the scene are as follows:

* To rotate the camera about the center of the scene, hold the left mouse button and drag the cursor.
* To rotate the camera about its viewing axis, hold `CTRL` left mouse button and drag the cursor.
* To pan the camera, do one of the following:
    * Hold `SHIFT`, then hold the left mouse button and drag the cursor.
    * Hold the middle mouse button and drag the cursor.
* To zoom the camera in or out, do one of the following:
    * Scroll the mouse wheel.
    * Hold the right mouse button and drag the cursor.

The available keyboard commands are as follows:

* `a`: Toggles rotational animation mode.
* `c`: Toggles backface culling.
* `f`: Toggles fullscreen mode.
* `h`: Toggles shadow rendering.
* `i`: Toggles axis display mode (no axes, world axis, mesh axes, all axes).
* `l`: Toggles lighting mode (scene lighting, Raymond lighting, or direct lighting).
* `m`: Toggles face normal visualization.
* `n`: Toggles vertex normal visualization.
* `o`: Toggles orthographic camera mode.
* `q`: Quits the viewer.
* `r`: Starts recording a GIF, and pressing again stops recording and opens a file dialog.
* `s`: Opens a file dialog to save the current view as an image.
* `w`: Toggles wireframe mode (scene default, flip wireframes, all wireframe, or all solid).
* `z`: Resets the camera to the default view.

As a note, displaying shadows significantly slows down rendering, so if you're
experiencing low framerates, just kill shadows or reduce the number of lights in
your scene.

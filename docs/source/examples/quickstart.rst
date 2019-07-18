.. _quickstart_guide:

Quickstart
==========


Minimal Example for 3D Viewer
-----------------------------
Here is a minimal example of loading and viewing a triangular mesh model
in pyrender.

>>> import trimesh
>>> import pyrender
>>> fuze_trimesh = trimesh.load('examples/models/fuze.obj')
>>> mesh = pyrender.Mesh.from_trimesh(fuze_trimesh)
>>> scene = pyrender.Scene()
>>> scene.add(mesh)
>>> pyrender.Viewer(scene, use_raymond_lighting=True)

.. image:: /_static/fuze.png


Minimal Example for Offscreen Rendering
---------------------------------------
.. note::
   If you're using a headless server, make sure that you followed the guide
   for installing OSMesa. See :ref:`osmesa`.

Here is a minimal example of rendering a mesh model offscreen in pyrender.
The only additional necessities are that you need to add lighting and a camera.

>>> import numpy as np
>>> import trimesh
>>> import pyrender
>>> import matplotlib.pyplot as plt

>>> fuze_trimesh = trimesh.load('examples/models/fuze.obj')
>>> mesh = pyrender.Mesh.from_trimesh(fuze_trimesh)
>>> scene = pyrender.Scene()
>>> scene.add(mesh)
>>> camera = pyrender.PerspectiveCamera(yfov=np.pi / 3.0, aspectRatio=1.0)
>>> s = np.sqrt(2)/2
>>> camera_pose = np.array([
...    [0.0, -s,   s,   0.3],
...    [1.0,  0.0, 0.0, 0.0],
...    [0.0,  s,   s,   0.35],
...    [0.0,  0.0, 0.0, 1.0],
... ])
>>> scene.add(camera, pose=camera_pose)
>>> light = pyrender.SpotLight(color=np.ones(3), intensity=3.0,
...                            innerConeAngle=np.pi/16.0,
...                            outerConeAngle=np.pi/6.0)
>>> scene.add(light, pose=camera_pose)
>>> r = pyrender.OffscreenRenderer(400, 400)
>>> color, depth = r.render(scene)
>>> plt.figure()
>>> plt.subplot(1,2,1)
>>> plt.axis('off')
>>> plt.imshow(color)
>>> plt.subplot(1,2,2)
>>> plt.axis('off')
>>> plt.imshow(depth, cmap=plt.cm.gray_r)
>>> plt.show()

.. image:: /_static/minexcolor.png
   :width: 45%
   :align: left
.. image:: /_static/minexdepth.png
   :width: 45%
   :align: right


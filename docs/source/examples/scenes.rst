.. _scene_guide:

Creating Scenes
===============

Before you render anything, you need to put all of your lights, cameras,
and meshes into a scene. The :class:`.Scene` object keeps track of the relative
poses of these primitives by inserting them into :class:`.Node` objects and
keeping them in a directed acyclic graph.

Adding Objects
--------------

To create a :class:`.Scene`, simply call the constructor. You can optionally
specify an ambient light color and a background color:

>>> scene = pyrender.Scene(ambient_light=[0.02, 0.02, 0.02],
...                        bg_color=[1.0, 1.0, 1.0])

You can add objects to a scene by first creating a :class:`.Node` object
and adding the object and its pose to the :class:`.Node`. Poses are specified
as 4x4 homogenous transformation matrices that are stored in the node's
:attr:`.Node.matrix` attribute. Note that the :class:`.Node`
constructor requires you to specify whether you're adding a mesh, light,
or camera.

>>> mesh = pyrender.Mesh.from_trimesh(tm)
>>> light = pyrender.PointLight(color=[1.0, 1.0, 1.0], intensity=2.0)
>>> cam = pyrender.PerspectiveCamera(yfov=np.pi / 3.0, aspectRatio=1.414)
>>> nm = pyrender.Node(mesh=mesh, matrix=np.eye(4))
>>> nl = pyrender.Node(light=light, matrix=np.eye(4))
>>> nc = pyrender.Node(camera=cam, matrix=np.eye(4))
>>> scene.add_node(nm)
>>> scene.add_node(nl)
>>> scene.add_node(nc)

You can also add objects directly to a scene with the :meth:`.Scene.add` function,
which takes care of creating a :class:`.Node` for you.

>>> scene.add(mesh, pose=np.eye(4))
>>> scene.add(light, pose=np.eye(4))
>>> scene.add(cam, pose=np.eye(4))

Nodes can be hierarchical, in which case the node's :attr:`.Node.matrix`
specifies that node's pose relative to its parent frame. You can add nodes to
a scene hierarchically by specifying a parent node in your calls to
:meth:`.Scene.add` or :meth:`.Scene.add_node`:

>>> scene.add_node(nl, parent_node=nc)
>>> scene.add(cam, parent_node=nm)

If you add multiple cameras to a scene, you can specify which one to render from
by setting the :attr:`.Scene.main_camera_node` attribute.

Updating Objects
----------------

You can update the poses of existing nodes with the :meth:`.Scene.set_pose`
function. Simply call it with a :class:`.Node` that is already in the scene
and the new pose of that node with respect to its parent as a 4x4 homogenous
transformation matrix:

>>> scene.set_pose(nl, pose=np.eye(4))

If you want to get the local pose of a node, you can just access its
:attr:`.Node.matrix` attribute. However, if you want to the get
the pose of a node *with respect to the world frame*, you can call the
:meth:`.Scene.get_pose` method.

>>> tf = scene.get_pose(nl)

Removing Objects
----------------

Finally, you can remove a :class:`.Node` and all of its children from the
scene with the :meth:`.Scene.remove_node` function:

>>> scene.remove_node(nl)

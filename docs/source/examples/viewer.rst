.. _viewer_guide:

Live Scene Viewer
=================

Standard Usage
--------------
In addition to the offscreen renderer, Pyrender comes with a live scene viewer.
In its standard invocation, calling the :class:`.Viewer`'s constructor will
immediately pop a viewing window that you can navigate around in.

>>> pyrender.Viewer(scene)

By default, the viewer uses your scene's lighting. If you'd like to start with
some additional lighting that moves around with the camera, you can specify that
with:

>>> pyrender.Viewer(scene, use_raymond_lighting=True)

For a full list of the many options that the :class:`.Viewer` supports, check out its
documentation.

.. image:: /_static/rotation.gif

Running the Viewer in a Separate Thread
---------------------------------------
If you'd like to animate your models, you'll want to run the viewer in a
separate thread so that you can update the scene while the viewer is running.
To do this, first pop the viewer in a separate thread by calling its constructor
with the ``run_in_thread`` option set:

>>> v = pyrender.Viewer(scene, run_in_thread=True)

Then, you can manipulate the :class:`.Scene` while the viewer is running to
animate things. However, be careful to acquire the viewer's
:attr:`.Viewer.render_lock` before editing the scene to prevent data corruption:

>>> i = 0
>>> while True:
...     pose = np.eye(4)
...     pose[:3,3] = [i, 0, 0]
...     v.render_lock.acquire()
...     scene.set_pose(mesh_node, pose)
...     v.render_lock.release()
...     i += 0.01

.. image:: /_static/scissors.gif

You can wait on the viewer to be closed manually:

>>> while v.is_active:
...     pass

Or you can close it from the main thread forcibly.
Make sure to still loop and block for the viewer to actually exit before using
the scene object again.

>>> v.close_external()
>>> while v.is_active:
...     pass


.. _camera_guide:

Creating Cameras
================

Pyrender supports two camera types -- :class:`.PerspectiveCamera` types,
which render scenes as a human would see them, and
:class:`.OrthographicCamera` types, which preserve distances between points.

Creating cameras is easy -- just specify their basic attributes:

>>> pc = pyrender.PerspectiveCamera(yfov=np.pi / 3.0, aspectRatio=1.414)
>>> oc = pyrender.OrthographicCamera(xmag=1.0, ymag=1.0)

For more information, see the Khronos group's documentation here_:

.. _here: https://github.com/KhronosGroup/glTF/tree/master/specification/2.0#projection-matrices

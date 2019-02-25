.. _offscreen_guide:

Offscreen Rendering
===================

.. note::
   If you're using a headless server, you'll need to use either EGL (for
   GPU-accelerated rendering) or OSMesa (for CPU-only software rendering).
   If you're using OSMesa, be sure that you've installed it properly. See
   :ref:`osmesa` for details.

Choosing a Backend
------------------

Once you have a scene set up with its geometry, cameras, and lights,
you can render it using the :class:`.OffscreenRenderer`. Pyrender supports
three backends for offscreen rendering:

- Pyglet, the same engine that runs the viewer. This requires an active
  display manager, so you can't run it on a headless server. This is the
  default option.
- OSMesa, a software renderer.
- EGL, which allows for GPU-accelerated rendering without a display manager.

If you want to use OSMesa or EGL, you need to set the ``PYOPENGL_PLATFORM``
environment variable before importing pyrender or any other OpenGL library.
You can do this at the command line:

.. code-block:: bash

   PYOPENGL_PLATFORM=osmesa python render.py

or at the top of your Python script:

.. code-block:: bash

   # Top of main python script
   import os
   os.environ['PYOPENGL_PLATFORM'] = 'egl'

The handle for EGL is ``egl``, and the handle for OSMesa is ``osmesa``.

Running the Renderer
--------------------

Once you've set your environment variable appropriately, create your scene and
then configure the :class:`.OffscreenRenderer` object with a window width,
a window height, and a size for point-cloud points:

>>> r = pyrender.OffscreenRenderer(viewport_width=640,
...                                viewport_height=480,
...                                point_size=1.0)

Then, just call the :meth:`.OffscreenRenderer.render` function:

>>> color, depth = r.render(scene)

.. image:: /_static/scene.png

This will return a ``(w,h,3)`` channel floating-point color image and
a ``(w,h)`` floating-point depth image rendered from the scene's main camera.

You can customize the rendering process by using flag options from
:class:`.RenderFlags` and bitwise or-ing them together. For example,
the following code renders a color image with an alpha channel
and enables shadow mapping for all directional lights:

>>> flags = RenderFlags.RGBA | RenderFlags.SHADOWS_DIRECTIONAL
>>> color, depth = r.render(scene, flags=flags)

Once you're done with the offscreen renderer, you need to close it before you
can run a different renderer or open the viewer for the same scene:

>>> r.delete()

Google CoLab Examples
---------------------

For a minimal working example of offscreen rendering using OSMesa,
see the `OSMesa Google CoLab notebook`_.

.. _OSMesa Google CoLab notebook: https://colab.research.google.com/drive/1Z71mHIc-Sqval92nK290vAsHZRUkCjUx

For a minimal working example of offscreen rendering using EGL,
see the `EGL Google CoLab notebook`_.

.. _EGL Google CoLab notebook: https://colab.research.google.com/drive/1rTLHk0qxh4dn8KNe-mCnN8HAWdd2_BEh

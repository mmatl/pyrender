.. _offscreen_guide:

Offscreen Rendering
===================
Once you have a scene set up with its geometry, cameras, and lights,
you can render it using the :class:`.OffscreenRenderer`.

Configure the renderer with a window width, a window height, and a size for
point-cloud points:

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
can run a different renderer or open the viewer:

>>> r.delete()

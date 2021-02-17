Installation Guide
==================

Python Installation
-------------------

This package is available via ``pip``.

.. code-block:: bash

   pip install pyrender

If you're on MacOS, you'll need
to pre-install my fork of ``pyglet``, as the version on PyPI hasn't yet included
my change that enables OpenGL contexts on MacOS.

.. code-block:: bash

   git clone https://github.com/mmatl/pyglet.git
   cd pyglet
   pip install .

.. _osmesa:

Getting Pyrender Working with OSMesa
------------------------------------
If you want to render scenes offscreen but don't want to have to
install a display manager or deal with the pains of trying to get
OpenGL to work over SSH, you have two options.

The first (and preferred) option is using EGL, which enables you to perform
GPU-accelerated rendering on headless servers.
However, you'll need EGL 1.5 to get modern OpenGL contexts.
This comes packaged with NVIDIA's current drivers, but if you are having issues
getting EGL to work with your hardware, you can try using OSMesa,
a software-based offscreen renderer that is included with any Mesa
install.

If you want to use OSMesa with pyrender, you'll have to perform two additional
installation steps:

- :ref:`installmesa`
- :ref:`installpyopengl`

Then, read the offscreen rendering tutorial. See :ref:`offscreen_guide`.

.. _installmesa:

Installing OSMesa
*****************

As a first step, you'll need to rebuild and re-install Mesa with support
for fast offscreen rendering and OpenGL 3+ contexts.
I'd recommend installing from source, but you can also try my ``.deb``
for Ubuntu 16.04 and up.

Installing from a Debian Package
********************************

If you're running Ubuntu 16.04 or newer, you should be able to install the
required version of Mesa from my ``.deb`` file.

.. code-block:: bash

   sudo apt update
   sudo wget https://github.com/mmatl/travis_debs/raw/master/xenial/mesa_18.3.3-0.deb
   sudo dpkg -i ./mesa_18.3.3-0.deb || true
   sudo apt install -f

If this doesn't work, try building from source.

Building From Source
********************

First, install build dependencies via `apt` or your system's package manager.

.. code-block:: bash

   sudo apt-get install llvm-6.0 freeglut3 freeglut3-dev

Then, download the current release of Mesa from here_.
Unpack the source and go to the source folder:

.. _here: https://archive.mesa3d.org/mesa-18.3.3.tar.gz

.. code-block:: bash

   tar xfv mesa-18.3.3.tar.gz
   cd mesa-18.3.3

Replace ``PREFIX`` with the path you want to install Mesa at.
If you're not worried about overwriting your default Mesa install,
a good place is at ``/usr/local``.

Now, configure the installation by running the following command:

.. code-block:: bash

   ./configure --prefix=PREFIX                                   \
               --enable-opengl --disable-gles1 --disable-gles2   \
               --disable-va --disable-xvmc --disable-vdpau       \
               --enable-shared-glapi                             \
               --disable-texture-float                           \
               --enable-gallium-llvm --enable-llvm-shared-libs   \
               --with-gallium-drivers=swrast,swr                 \
               --disable-dri --with-dri-drivers=                 \
               --disable-egl --with-egl-platforms= --disable-gbm \
               --disable-glx                                     \
               --disable-osmesa --enable-gallium-osmesa          \
               ac_cv_path_LLVM_CONFIG=llvm-config-6.0

Finally, build and install Mesa.

.. code-block:: bash

   make -j8
   make install

Finally, if you didn't install Mesa in the system path,
add the following lines to your ``~/.bashrc`` file after
changing ``MESA_HOME`` to your mesa installation path (i.e. what you used as
``PREFIX`` during the configure command).

.. code-block:: bash

   MESA_HOME=/path/to/your/mesa/installation
   export LIBRARY_PATH=$LIBRARY_PATH:$MESA_HOME/lib
   export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$MESA_HOME/lib
   export C_INCLUDE_PATH=$C_INCLUDE_PATH:$MESA_HOME/include/
   export CPLUS_INCLUDE_PATH=$CPLUS_INCLUDE_PATH:$MESA_HOME/include/

.. _installpyopengl:

Installing a Compatible Fork of PyOpenGL
****************************************

Next, install and use my fork of ``PyOpenGL``.
This fork enables getting modern OpenGL contexts with OSMesa.
My patch has been included in ``PyOpenGL``, but it has not yet been released
on PyPI.

.. code-block:: bash

   git clone https://github.com/mmatl/pyopengl.git
   pip install ./pyopengl


Building Documentation
----------------------

The online documentation for ``pyrender`` is automatically built by Read The Docs.
Building ``pyrender``'s documentation locally requires a few extra dependencies --
specifically, `sphinx`_ and a few plugins.

.. _sphinx: http://www.sphinx-doc.org/en/master/

To install the dependencies required, simply change directories into the `pyrender` source and run

.. code-block:: bash

    $ pip install .[docs]

Then, go to the ``docs`` directory and run ``make`` with the appropriate target.
For example,

.. code-block:: bash

    $ cd docs/
    $ make html

will generate a set of web pages. Any documentation files
generated in this manner can be found in ``docs/build``.

# from pyrender.platforms import egl


def tmp_test_default_device():
    egl.get_default_device()


def tmp_test_query_device():
    devices = egl.query_devices()
    assert len(devices) > 0


def tmp_test_init_context():
    device = egl.query_devices()[0]
    platform = egl.EGLPlatform(128, 128, device=device)
    platform.init_context()

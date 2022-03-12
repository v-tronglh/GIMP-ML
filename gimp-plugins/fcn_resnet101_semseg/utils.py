import numpy as np

import GPUtil
from gimpfu import NORMAL_MODE, gimp


def find_gpu_with_max_free_memory():
    ids = GPUtil.getAvailable(order='memory', maxLoad=1.0, maxMemory=1.0)
    id_ = ids[0] if ids else 0
    return id_


def gimp_to_numpy(layer):
    region = layer.get_pixel_rgn(0, 0, layer.width, layer.height)
    pix_chars = region[:, :]
    bpp = region.bpp
    return np.frombuffer(pix_chars, dtype=np.uint8).reshape(layer.height, layer.width, bpp)


def create_result_layer(img, name, result):
    rl_bytes = np.uint8(result).tobytes()
    rl = gimp.Layer(img, name, img.width, img.height, img.active_layer.type, 100, NORMAL_MODE)
    region = rl.get_pixel_rgn(0, 0, rl.width, rl.height, True)
    region[:, :] = rl_bytes
    img.add_layer(rl, 0)
    gimp.displays_flush()

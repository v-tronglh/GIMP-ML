import os.path as osp
import sys

sys.path.append(
    osp.join(
        osp.dirname(osp.realpath(__file__)),
        'fcn_resnet101_semseg',
        'env',
        'lib',
        'python2.7',
        'site-packages',
    )
)

import torch  # noqa: E402
from fcn_resnet101_semseg.model import FCNSemSeg  # noqa: E402
from fcn_resnet101_semseg.utils import (create_result_layer,  # noqa: E402
                                        find_gpu_with_max_free_memory,  # noqa: E402
                                        gimp_to_numpy)  # noqa: E402
from gimpfu import PF_BOOL, PF_DRAWABLE, PF_IMAGE, PF_INT, main, register  # noqa: E402


def run(img, layer, im_size, force_cpu):
    device = 'cuda:{}'.format(find_gpu_with_max_free_memory()) if not force_cpu and torch.cuda.is_available() else 'cpu'
    model = FCNSemSeg(im_size, device)
    im = gimp_to_numpy(layer)
    im = model(im)
    create_result_layer(img, 'semseg mask', im)


register(
    'semseg_fcn_resnet101',
    'Semseg FCN ResNet101',
    'Semantic Segmentation using FCN ResNet101',
    'Trong Le Huu',
    'VinAI',
    '2022',
    'FCN ResNet101 Semseg...',
    'RGB',
    [
        (PF_IMAGE, 'image', 'Input image', None),
        (PF_DRAWABLE, 'drawable', 'Input drawable', None),
        (PF_INT, 'imsize', 'Image size of model input', 128),
        (PF_BOOL, 'cpu', 'Force CPU', False),
    ],
    [],
    run,
    menu='<Image>/Layer/GIML-ML',
)

main()

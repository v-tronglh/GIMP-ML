import sys
import tempfile
from pathlib import Path

import gi

gi.require_version('Gimp', '3.0')
sys.path.append(str(Path(__file__).resolve().parent))
sys.path.append(str(Path(__file__).resolve().parent.joinpath('env', 'lib', 'python3.8', 'site-packages')))

import cv2  # noqa: E402
import torch  # noqa: E402
from gi.repository import Gimp, GLib, GObject  # noqa: E402
from model import FCNSemSeg  # noqa: E402
from utils import create_result_layer  # noqa: E402
from utils import (find_gpu_with_max_free_memory, get_params,  # noqa: E402
                   save_image)


class FCNSemSegPlugIn(Gimp.PlugIn):
    __gproperties__ = {
        'force_cpu': (
            bool,
            'Force CPU',
            'Force CPU',
            False,
            GObject.ParamFlags.READWRITE,
        ),
        'im_size': (
            int,
            'Image size',
            'Image size of model input',
            0,
            512,
            128,
            GObject.ParamFlags.READWRITE,
        ),
    }

    def add_args(self, procedure):
        # Ignore prop read_channel, write_channel
        for prop_name in dir(self.props)[:-2]:
            procedure.add_argument_from_property(self, prop_name)

    def do_query_procedures(self):
        return ['plug-in-fcn-resnet101-semseg']

    def do_create_procedure(self, name):
        procedure = Gimp.ImageProcedure.new(
            self,
            name,
            Gimp.PDBProcType.PLUGIN,
            self.run,
            None,
        )

        procedure.set_image_types('RGB')
        procedure.set_sensitivity_mask(Gimp.ProcedureSensitivityMask.DRAWABLE)

        procedure.set_menu_label('FCN ResNet101 Semseg...')
        procedure.add_menu_path('<Image>/Layer/GIMP-ML')

        procedure.set_documentation('Semseg FCN ResNet101',
                                    'Semantic Segmentation (VOC) using FCN ResNet101',
                                    name)
        procedure.set_attribution('Trong Le Huu', 'VinAI', '2021')
        self.add_args(procedure)
        return procedure

    def run(self, procedure, run_mode, image, n_drawables, drawables, args, run_data):
        if n_drawables != 1:
            msg = f'Procedure {procedure.get_name()} only works with one drawable.'
            error = GLib.Error.new_literal(Gimp.PlugIn.error_quark(), msg, 0)
            return procedure.new_return_values(Gimp.PDBStatusType.CALLING_ERROR, error)

        if run_mode == Gimp.RunMode.INTERACTIVE:
            # Cache image to disk
            _, tmp_im_file = tempfile.mkstemp(suffix='.png')
            save_image(image, drawables, tmp_im_file)

            params = get_params(
                image,
                procedure,
                run_mode,
                args,
                title='FCN ResNet101 Semseg',
                logo_file=None,
                license='PLUGIN LICENSE: MIT',
            )

            if params is not None:
                force_cpu, im_size = params
                device = ('cpu' if force_cpu or not torch.cuda.is_available()
                          else f'cuda:{find_gpu_with_max_free_memory()}')
                model = FCNSemSeg(im_size, device)
                img = cv2.imread(tmp_im_file)
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                im_result = model(img)
                im_result = cv2.cvtColor(im_result, cv2.COLOR_RGB2BGR)

                # Cache result to disk
                _, tmp_im_file = tempfile.mkstemp(suffix='.png')
                cv2.imwrite(tmp_im_file, im_result)

                create_result_layer(image, tmp_im_file, 'SegMask')

            return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())


Gimp.main(FCNSemSegPlugIn.__gtype__, sys.argv)

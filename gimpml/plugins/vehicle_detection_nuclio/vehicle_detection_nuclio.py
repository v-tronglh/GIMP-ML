import sys
import tempfile
from pathlib import Path

import gi

gi.require_version('Gimp', '3.0')
sys.path.append(str(Path(__file__).resolve().parent))
sys.path.append(str(Path(__file__).resolve().parent.joinpath('env', 'lib', 'python3.8', 'site-packages')))

import cv2  # noqa: E402
from gi.repository import Gimp, GLib, GObject  # noqa: E402
from model import VehicleDetection  # noqa: E402
from utils import create_result_layer, save_image  # noqa: E402


class VehicleDetectionPlugIn(Gimp.PlugIn):
    def do_query_procedures(self):
        return ['plug-in-vehicle-detection']

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

        procedure.set_menu_label('Vehicle Detection...')
        procedure.add_menu_path('<Image>/Layer/GIMP-ML')

        procedure.set_documentation('Vehicle Detection',
                                    'Vehicle Detection',
                                    name)
        procedure.set_attribution('Trong Le Huu', 'VinAI', '2021')
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

            model = VehicleDetection()
            im_result = model(tmp_im_file)

            # Cache result to disk
            _, tmp_im_file = tempfile.mkstemp(suffix='.png')
            cv2.imwrite(tmp_im_file, im_result)

            create_result_layer(image, tmp_im_file, 'Detection')

            return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())


Gimp.main(VehicleDetectionPlugIn.__gtype__, sys.argv)

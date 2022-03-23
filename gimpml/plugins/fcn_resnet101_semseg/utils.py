from pathlib import Path

import gi
import GPUtil

gi.require_version('Gimp', '3.0')
gi.require_version('GimpUi', '3.0')
gi.require_version('Gtk', '3.0')

from gi.repository import Gimp, GimpUi, Gio, GObject, Gtk  # noqa: E402


def find_gpu_with_max_free_memory():
    ids = GPUtil.getAvailable(order='memory', maxLoad=1.0, maxMemory=1.0)
    id_ = ids[0] if ids else 0
    return id_


def save_image(image, drawable, file_path):
    interlace, compression = 0, 2
    Gimp.get_pdb().run_procedure(
        'file-png-save',
        [
            GObject.Value(Gimp.RunMode, Gimp.RunMode.NONINTERACTIVE),
            GObject.Value(Gimp.Image, image),
            GObject.Value(GObject.TYPE_INT, 1),
            GObject.Value(
                Gimp.ObjectArray, Gimp.ObjectArray.new(Gimp.Drawable, drawable, 0)
            ),
            GObject.Value(
                Gio.File,
                Gio.File.new_for_path(file_path),
            ),
            GObject.Value(GObject.TYPE_BOOLEAN, interlace),
            GObject.Value(GObject.TYPE_INT, compression),

            GObject.Value(GObject.TYPE_BOOLEAN, True),
            GObject.Value(GObject.TYPE_BOOLEAN, True),
            GObject.Value(GObject.TYPE_BOOLEAN, False),
            GObject.Value(GObject.TYPE_BOOLEAN, True),
        ],
    )


def get_params(image, procedure, run_mode, args, title, logo_file, license):
    config = procedure.create_config()

    # Skip run-mode, image, num-drawables, drawables
    for i, arg_info in enumerate(procedure.get_arguments()[4:]):
        config.set_property(arg_info.name.replace('-', '_'), args.index(i))

    config.begin_run(image, run_mode, args)

    # Create UI
    GimpUi.init('utils.py')
    use_header_bar = Gtk.Settings.get_default().get_property('gtk-dialogs-use-header')

    # Create dialog
    dialog = GimpUi.Dialog(
        use_header_bar=use_header_bar,
        title=title,
    )

    # Add buttons
    dialog.add_button('_Cancel', Gtk.ResponseType.CANCEL)
    dialog.add_button('_Run Inference', Gtk.ResponseType.OK)

    vbox = Gtk.Box(
        orientation=Gtk.Orientation.VERTICAL,
        homogeneous=False,
        spacing=10,
    )
    dialog.get_content_area().add(vbox)
    vbox.show()

    # Create grid to set all the properties inside.
    grid = Gtk.Grid()
    grid.set_column_homogeneous(False)
    grid.set_border_width(10)
    grid.set_column_spacing(10)
    grid.set_row_spacing(10)
    vbox.add(grid)
    grid.show()

    # Add parameters
    # Skip run-mode, image, num-drawables, drawables
    row = 0
    for i, arg_info in enumerate(procedure.get_arguments()[4:]):
        if arg_info.value_type.name == 'gboolean':
            label = Gtk.Label.new_with_mnemonic(arg_info.blurb)
            grid.attach(label, 0, row, 1, 1)
            label.show()
            spin = GimpUi.prop_check_button_new(config, arg_info.name.replace('-', '_'), '')
            grid.attach(spin, 1, row, 1, 1)
            spin.show()
        elif arg_info.value_type.name == 'gint':
            label = Gtk.Label.new_with_mnemonic(arg_info.blurb)
            grid.attach(label, 0, row, 1, 1)
            label.show()
            spin = GimpUi.prop_spin_button_new(
                config,
                arg_info.name.replace('-', '_'),
                step_increment=1,
                page_increment=10,
                digits=0,
            )
            grid.attach(spin, 1, row, 1, 1)
            spin.show()
        else:
            raise TypeError(f'Unsupported type {arg_info.value_type}.')
        row += 1

    # Show Logo
    if logo_file and Path(logo_file).exists():
        logo = Gtk.Image.new_from_file(logo_file)
        vbox.pack_start(logo, False, False, 1)
        logo.show()

    # Show License
    if license:
        label = Gtk.Label(label=license)
        vbox.pack_start(label, False, False, 1)
        label.show()

    # Wait for user to click
    dialog.show()
    while True:
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            params = []

            # Skip run-mode, image, num-drawables, drawables
            for i, arg_info in enumerate(procedure.get_arguments()[4:]):
                params.append(config.get_property(arg_info.name.replace('-', '_')))

            config.end_run(Gimp.PDBStatusType.SUCCESS)
            return params
        else:
            dialog.destroy()
            return None


def create_result_layer(image, im_file, layer_name):
    result = Gimp.file_load(
        Gimp.RunMode.NONINTERACTIVE,
        Gio.file_new_for_path(im_file),
    )
    result_layer = result.get_active_layer()
    copy = Gimp.Layer.new_from_drawable(result_layer, image)
    copy.set_name(layer_name)
    copy.set_mode(Gimp.LayerMode.NORMAL_LEGACY)
    image.insert_layer(copy, None, -1)

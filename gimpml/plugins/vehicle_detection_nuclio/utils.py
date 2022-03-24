import gi

gi.require_version('Gimp', '3.0')
gi.require_version('GimpUi', '3.0')
gi.require_version('Gtk', '3.0')

from gi.repository import Gimp, GimpUi, Gio, GObject, Gtk  # noqa: E402


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

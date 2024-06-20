import utils as Utils
from drawing_area import DrawingArea
from gi.repository import Adw, Gio, Gtk  # type:ignore
from palette_bar import PaletteBar
from shared import Box, ToolbarView
from state import State
from toolbar import Toolbar
from new_dialog import NewDialog


class Window(Adw.ApplicationWindow):
    def __init__(self) -> None:
        super().__init__()
        State.main_window = self
        self.set_application(State.application)
        State.icon_theme = Gtk.IconTheme.get_for_display(self.get_display())
        State.icon_theme.add_search_path("data/icons")
        self.__build_ui()

    def __build_ui(self) -> None:
        self.set_title("Grid")
        self.props.height_request = 200
        self.props.width_request = 360
        self.set_default_size(800, 600)

        # Content
        save_img_btn: Gtk.Button = Gtk.Button(
            tooltip_text="Save", icon_name="document-save-symbolic"
        )
        save_img_btn.connect("clicked", self.__on_save_img_btn_clicked)

        new_btn: Gtk.Button = Gtk.Button(
            tooltip_text="New", icon_name="grid-new-symbolic"
        )
        new_btn.connect("clicked", self.__on_new_btn_clicked)

        open_btn: Gtk.Button = Gtk.Button(
            tooltip_text="Open", icon_name="grid-open-symbolic"
        )
        open_btn.connect("clicked", self.__on_open_btn_clicked)

        hb: Adw.HeaderBar = Adw.HeaderBar()
        hb.pack_start(new_btn)
        hb.pack_start(open_btn)
        hb.pack_start(save_img_btn)

        self.set_content(
            ToolbarView(
                top_bars=[hb],
                content=Box(
                    children=[
                        PaletteBar(),
                        Gtk.Separator(orientation=Gtk.Orientation.VERTICAL),
                        Gtk.ScrolledWindow(child=DrawingArea(), hexpand=True),
                        Gtk.Separator(orientation=Gtk.Orientation.VERTICAL),
                        Toolbar(),
                    ]
                ),
                top_bar_style=Adw.ToolbarStyle.RAISED_BORDER,
            )
        )

    def __on_save_img_btn_clicked(self, _) -> None:
        def __save_cb(dialog: Gtk.FileDialog, res: Gio.Task) -> None:
            try:
                path: str = dialog.save_finish(res).get_path()
                Utils.save_png(path)
            except BaseException as e:
                print(e)

        Gtk.FileDialog(
            initial_name="untitled.png",
            default_filter=Gtk.FileFilter(patterns=["*.png"]),
        ).save(self, None, __save_cb)

    def __on_new_btn_clicked(self, _) -> None:
        if not State.new_dialog:
            State.new_dialog = NewDialog()
        State.new_dialog.present(self)

    def __on_open_btn_clicked(self, _) -> None:
        def __open_cb(dialog: Gtk.FileDialog, res: Gio.Task) -> None:
            try:
                path: str = dialog.open_finish(res).get_path()
                pixel_data: list[list[str]] = Utils.load_png(path)
                State.drawing_area.load_image(pixel_data)
            except BaseException as e:
                print(e)

        Gtk.FileDialog(default_filter=Gtk.FileFilter(patterns=["*.png"])).open(
            self, None, __open_cb
        )

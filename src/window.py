import utils as Utils
from drawing_area import DrawingArea
from gi.repository import Adw, Gtk  # type:ignore
from palette_bar import PaletteBar
from shared import Box, ToolbarView
from state import State
from toolbar import Toolbar


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
        hb: Adw.HeaderBar = Adw.HeaderBar()
        save_img_btn: Gtk.Button = Gtk.Button(
            tooltip_text="Save", icon_name="document-save-symbolic"
        )
        save_img_btn.connect("clicked", self.__on_save_img_btn_clicked)
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
        dialog: Gtk.FileDialog = Gtk.FileDialog(initial_name="untitled.png")

        def __save_cb(res) -> None:
            try:
                path: str = dialog.save_finish(res).get_path()
                Utils.save_png(path)
            except BaseException:
                pass

        dialog.save(self, None, __save_cb)

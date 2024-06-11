from gi.repository import Adw, Gtk  # type:ignore
from state import State
from utils import Utils
from drawing_area import DrawingArea
from palette_bar import PaletteBar


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
        save_img_btn.connect("clicked", Utils.save_png)
        hb.pack_start(save_img_btn)

        toolbar_view: Adw.ToolbarView = Adw.ToolbarView(
            content=Gtk.ScrolledWindow(child=DrawingArea(), hexpand=True),
        )
        toolbar_view.add_top_bar(hb)
        split_view = Adw.OverlaySplitView(
            sidebar=PaletteBar(),
            content=toolbar_view,
            max_sidebar_width=100,
            min_sidebar_width=20,
        )
        self.set_content(split_view)

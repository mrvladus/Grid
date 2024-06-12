from gi.repository import Adw, Gtk  # type:ignore
from state import State
from toolbar import Toolbar
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

        hbox = Gtk.Box()
        hbox.append(PaletteBar())
        hbox.append(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL))
        hbox.append(Gtk.ScrolledWindow(child=DrawingArea(), hexpand=True))
        hbox.append(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL))
        hbox.append(Toolbar())

        toolbar_view: Adw.ToolbarView = Adw.ToolbarView(
            content=hbox, top_bar_style=Adw.ToolbarStyle.RAISED_BORDER
        )
        toolbar_view.add_top_bar(hb)

        self.set_content(toolbar_view)

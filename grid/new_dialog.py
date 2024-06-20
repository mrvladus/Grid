from gi.repository import Adw, Gtk  # type:ignore
from state import State
from shared import Box, Button, ToolbarView


class NewDialog(Adw.Dialog):
    bg_color: str = "#00000000"

    def __init__(self) -> None:
        super().__init__()
        self.__build_ui()

    def __build_ui(self) -> None:
        self.set_content_width(360)
        # Presets
        x8_btn = Button(
            label="8x8",
            css_classes=["flat"],
            on_click=lambda *_: self.__create_new_sprite(8, 8),
        )
        x16_btn = Button(
            label="16x16",
            css_classes=["flat"],
            on_click=lambda *_: self.__create_new_sprite(16, 16),
        )
        x32_btn = Button(
            label="32x32",
            css_classes=["flat"],
            on_click=lambda *_: self.__create_new_sprite(32, 32),
        )
        x64_btn = Button(
            label="64x64",
            css_classes=["flat"],
            on_click=lambda *_: self.__create_new_sprite(64, 64),
        )

        presets_group = Adw.PreferencesGroup(title="Presets")
        presets_group.add(
            Adw.PreferencesRow(
                child=Box(
                    children=[x8_btn, x16_btn, x32_btn, x64_btn],
                    css_classes=["toolbar"],
                    halign=Gtk.Align.CENTER,
                    homogeneous=True,
                ),
                activatable=False,
            )
        )

        # Custom size
        width = Adw.SpinRow(
            title="Width",
            adjustment=Gtk.Adjustment(
                lower=0, step_increment=1, page_increment=10, upper=10000
            ),
            value=16,
            numeric=True,
            activatable=False,
        )
        height = Adw.SpinRow(
            title="Height",
            adjustment=Gtk.Adjustment(
                lower=0, step_increment=1, page_increment=10, upper=10000
            ),
            value=16,
            numeric=True,
            activatable=False,
        )
        custom_size_btn = Button(
            label="Create",
            css_classes=["pill", "suggested-action"],
            halign=Gtk.Align.CENTER,
            on_click=lambda *_: self.__create_new_sprite(
                int(width.get_value()), int(height.get_value())
            ),
        )

        custom_size_group = Adw.PreferencesGroup(title="Custom Size")
        custom_size_group.add(width)
        custom_size_group.add(height)

        self.set_child(
            ToolbarView(
                top_bars=[
                    Adw.HeaderBar(title_widget=Adw.WindowTitle(title="New Sprite"))
                ],
                content=Box(
                    children=[presets_group, custom_size_group, custom_size_btn],
                    orientation=Gtk.Orientation.VERTICAL,
                    spacing=12,
                    margin_start=12,
                    margin_end=12,
                    margin_bottom=12,
                ),
            )
        )

    def __create_new_sprite(self, width: int, height: int) -> None:
        self.close()
        State.main_window.welcome_page.set_visible(False)
        pixel_data: list[list[str]] = [[self.bg_color] * width for _ in range(height)]
        State.drawing_area.load_image(pixel_data)

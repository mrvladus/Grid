from gi.repository import Adw, Gtk  # type:ignore
from shared import Box, ToolbarView


class NewDialog(Adw.Dialog):
    def __init__(self) -> None:
        super().__init__()
        self.__build_ui()

    def __build_ui(self) -> None:
        self.set_content_width(360)
        # Presets
        x8_btn = Gtk.Button(label="8x8", css_classes=["flat"])
        x8_btn.connect("clicked", self.__create_new_sprite, 8, 8)
        x16_btn = Gtk.Button(label="16x16", css_classes=["flat"])
        x16_btn.connect("clicked", self.__create_new_sprite, 16, 16)
        x32_btn = Gtk.Button(label="32x32", css_classes=["flat"])
        x32_btn.connect("clicked", self.__create_new_sprite, 32, 32)
        x64_btn = Gtk.Button(label="64x64", css_classes=["flat"])
        x64_btn.connect("clicked", self.__create_new_sprite, 64, 64)

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
        custom_size_btn = Gtk.Button(
            label="Create",
            css_classes=["pill", "suggested-action"],
            halign=Gtk.Align.CENTER,
        )
        custom_size_btn.connect(
            "clicked",
            lambda *_: self.__create_new_sprite(
                None, int(width.get_value()), int(height.get_value())
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

    def __create_new_sprite(self, _, width: int, height: int) -> None:
        print(width, height)

"""Example showing the Ask User dialog controls and overall usage."""

import fusionless as fu

dialog = fu.AskUserDialog("Example Ask User Dialog")
dialog.add_text("text", default="Default text value")
dialog.add_position("position", default=(0.2, 0.8))
dialog.add_slider("slider", default=0.5, min=-10, max=10)
dialog.add_screw("screw")
dialog.add_file_browse("file", default="C:/path/to/foo")
dialog.add_path_browse("path")
dialog.add_clip_browse("clip")
dialog.add_checkbox("checkbox", name="Do not check this!")
dialog.add_dropdown("dropdown", options=["A", "B", "C"])
dialog.add_multibutton("multibutton", options=["Foo", "Bar", "Nugget"])
result = dialog.show()

if result is None:
    # Dialog was cancelled
    pass
else:
    checked = result['checkbox']
    if checked:
        print("You sure are living on the edge!")

    import pprint
    pprint.pprint(result)

"""Sets all Backgrounds in the currently active comp to 1920x1080 (32 bit).

This example shows how to list tool of a specific type and set some of its
inputs. Additionally this shows off how `fusionless` is able to automatically
interpret an enum value (like "float32" for image depth) to the corresponding
float value that Fusion requires to be set internally.

"""

import fusionless as fu
import fusionless.context as fuCtx

c = fu.Comp()
with fuCtx.lock_and_undo_chunk(c, "Set all backgrounds to 1920x1080 (32 bit)"):

    # Get all backgrounds in the current comp
    tools = c.get_tool_list(selected=False,
                            node_type="Background")

    for tool in tools:
        tool.input("Width").set_value(1920)
        tool.input("Height").set_value(1080)

        # Set the depth to "float32". Note that
        # fusion internally uses float value indices
        # for the different values. `fusionless` will
        # automatically convert enum values to their
        # corresponding float value when possible.
        tool.input("Depth").set_value("float32")

        # So the depth would internally get set like
        # tool.input("Depth").set_value(4.0)
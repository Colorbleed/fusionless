"""Disconnect all inputs for selected tools"""

import fusionless as fu
import fusionless.context as fuCtx

c = fu.Comp()
with fuCtx.lock_and_undo_chunk(c, "Disconnect inputs"):

    for tool in c.get_selected_tools():
        for input in tool.inputs():
            input.disconnect()
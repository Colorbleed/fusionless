"""Enable the 'Loop' input for all selected loaders"""

import fusionless as fu
import fusionless.context as fuCtx

c = fu.Comp()
with fuCtx.lock_and_undo_chunk(c, "Set loaders to loop"):

    for tool in c.get_selected_tools(node_type="Loader"):
        loop = tool.input("Loop").set_value(True)

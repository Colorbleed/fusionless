import fusionscript as fu
import fusionscript.context as fuCtx

with fuCtx.LockAndUndoChunk("Disconnect inputs"):

    c = fu.Comp()
    for tool in c.get_selected_tools():
        for input in tool.inputs():
            input.disconnect()
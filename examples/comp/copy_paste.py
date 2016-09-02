import fusionless as fu

comp = fu.Comp()
tools = comp.get_selected_tools()
comp.copy(tools)
comp.paste()

"""
    Contains the main `PyNode` base class.
    And for now also all its derived classes.
"""

class PyNode(object):

    _reference = None   # reference to PyRemoteObject

    def __new__(cls, reference=None):
        # If no arguments provided assume reference to fusion's comp
        if reference is None:
            reference = comp

        # Acquire an attribute to check for type (start prefix)
        attrs = reference.GetAttrs()
        data_type = next(iter(attrs))

        # Define the new class type
        newcls = None
        if data_type.startswith("COMP"):
            newcls = Comp
        elif data_type.startswith("TOOL"):
            newcls = Tool

        # Ensure we convert to a type preferred by the user
        # eg. currently Tool() would come out as Comp() since no arguments are provided.
        #     so instead we provide a TypeError() to be clear in those instances.
        if cls is not PyNode:
            if not issubclass(newcls, cls):
                raise TypeError("PyNode did not convert to preferred type. '{0}' is not an instance of '{1}'".format(newcls, cls))

        # Instantiate class and return
        if newcls:
            klass = super(PyNode, cls).__new__(newcls)
            klass._reference = reference
            return klass

        return None

    def set_attr(self, key, value):
        self._reference.SetAttrs({key: value})

    def __getattr__(self, attr):
        return getattr(self._reference, attr)

    def __repr__(self):
        return '{0}("{1}")'.format(self.__class__.__name__, str(self._reference.Name))


class Comp(PyNode):

    def get_current_time(self):
        return self._reference.CurrentTime

    def get_selected_tools(self, node_type=None):
        args = (node_type,) if node_type is not None else tuple()
        return [Tool(x) for x in self._reference.GetToolList(True, *args).values()]

    def get_active_tool(self):
        return self._reference.ActiveTool

    def set_active_tool(self, tool):
        self._reference.setActiveTool(tool)

    def create_node(self, node_type, attrs=None, insert=False):
        args = (-32768, -32768) if insert else tuple()
        tool = Tool(comp.AddTool(node_type, *args))
        if attrs:
            tool._reference.SetAttrs(attrs)
        return tool

    def __repr__(self):
        filename = self._reference.GetAttrs()['COMPS_FileName']
        return '{0}("{1}")'.format(self.__class__.__name__, filename)


class Tool(PyNode):
    def get_pos(self):
        flow = comp.CurrentFrame.FlowView
        return flow.GetPosTable(self._reference).values()

    def set_pos(self, pos):
        flow = comp.CurrentFrame.FlowView
        flow.SetPos(self._reference, *pos)

    def connect_to(self, tool, from_index=1, to_index=1):
        assert isinstance(tool, Tool)
        id = tool._reference.FindMainInput(1).ID
        tool._reference[id] = self._reference.FindMainOutput(1)

    def inputs(self):
        """ Return all Inputs of this Tools """
        raise NotImplementedError()

    def outputs(self):
        """ Return all Outputs of this Tools """
        raise NotImplementedError()

    def connections(self, inputs=True, outputs=True):
        """ Return all Connections of Inputs and Outputs of this Tools """
        raise NotImplementedError()

    def disconnect_all(self):
        """ Disconnect all inputs and outputs """
        raise NotImplementedError()

    def rename(self, name):
        self._reference.SetAttrs({'TOOLB_NameSet': True, 'TOOLS_Name': name})

    def clear_name(self):
        self._reference.SetAttrs({'TOOLB_NameSet': False, 'TOOLS_Name': ''})

    def set_text_color(self, color):
        """ Sets the Tool's text color.

        For example:
            >> tool.set_text_color({'R':0.5, 'G':0.1, 'B': 0.0})
            >> tool.set_text_color(None)
        """
        self._reference.TextColor = color

    def set_tile_color(self, color):
        """ Sets the Tool's tile color.

        For example:
            >> tool.set_tile_color({'R':0.5, 'G':0.1, 'B': 0.0})
            >> tool.set_tile_color(None)
        """
        self._reference.TileColor = color


class Flow(PyNode):
    pass


class Attribute(PyNode):
    def disconnect(self):
        pass


class Input(Attribute):
    pass


class Output(Attribute):
    pass

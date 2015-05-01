"""
    Contains the main `PyNode` base class.
    And for now also all its derived classes.

    Note that this package is an early release (consider it pre-alpha public development).
    Here's a community-built list of Fusion's built-in classes:
    http://www.steakunderwater.com/VFXPedia/96.0.243.189/index8c76.html?title=Eyeon:Script/Reference/Applications/Fusion/Classes

    Most of the methods and class types available in Fusion will still have to be added and implemented in this
    `fusionscript` package.

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
        elif data_type.startswith("INP"):
            newcls = Input
        elif data_type.startswith("OUT"):
            newcls = Output
        elif data_type.startswith("VIEW"):
            newcls = Flow

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

    def copy(self, tools):
        return self._reference.Copy([tool._reference for tool in tools])

    def paste(self, values=None):
        args = tuple() if values is None else (values,)
        return self._reference.Paste(*args)

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

    def connect_main(self, tool, from_index=1, to_index=1):
        assert isinstance(tool, Tool)
        id = tool._reference.FindMainInput(1).ID
        tool._reference[id] = self._reference.FindMainOutput(1)

    def attr(self, id):
        return Attribute(self._reference[id])

    def inputs(self):
        """ Return all Inputs of this Tools """
        return [Input(x) for x in self._reference.GetInputList().values()]

    def outputs(self):
        """ Return all Outputs of this Tools """
        return [Output(x) for x in self._reference.GetOutputList().values()]

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

    def delete(self):
        self._reference.Delete()

    def refresh(self):
        self._reference.Refresh()

    def parent(self):
        """ Return the parent Group this Tool belongs to, if any. """
        return self._reference.ParentTool

    def save_settings(self, path=None):
        """ Saves the tool's settings to a dict, or to a .setting file specified by the path argument.

        :param path: A valid path to the location where a .setting file will be saved.
        :type path: str
        :return:
            If a path is given, the tool's settings will be saved to that file, and a boolean is returned to indicate success.
            If no path is given, SaveSettings() will return a table of the tool's settings instead.
        """
        args = tuple() if path is None else (path,)
        return self._reference.SaveSettings(*args)

    def load_settings(self, settings):
        """ The LoadSettings function is used to load .setting files or tables into a tool.

        This is potentially useful for any number of applications, such as loading curve data into fusion, for which
        there is currently no simple way to script interactively in Fusion. Beyond that, it could possibly be used to
        sync updates to tools over project management systems.

        :param settings: The path to a valid .setting file or a settings dictionary.
                         A valid table of settings, such as produced by SaveSettings() or read from a .setting file.
        :return: None
        """
        self._reference.LoadSettings(settings)

    def comp(self):
        """ Return the Comp this Tool belongs to. """
        return Comp(self._reference.Composition)

    def set_text_color(self, color):
        """ Sets the Tool's text color.

        Example
            >>> tool.set_text_color({'R':0.5, 'G':0.1, 'B': 0.0})
            >>> tool.set_text_color(None)
        """
        self._reference.TextColor = color

    def set_tile_color(self, color):
        """ Sets the Tool's tile color.

        Example
            >>> tool.set_tile_color({'R':0.5, 'G':0.1, 'B': 0.0})
            >>> tool.set_tile_color(None)   # reset
        """
        self._reference.TileColor = color


class Flow(PyNode):
    def set_pos(self, tool, pos):
        """ Reposition the given Tool to the position in the FlowView.

        :param tool: This argument should contain the tool that will be repositioned in the FlowView.
        :type tool: Tool
        :param pos: Numeric values specifying the x and y co-ordinates for the tool in the FlowView.
        :type pos: list(float, float)
        """

        if not isinstance(tool, Tool):
            tool = Tool(tool)

        self._reference.SetPos(tool._reference, pos[0], pos[1])

    def get_pos(self, tool):
        """ This function will return the X and Y position of a tool's tile in the FlowView.

        :param tool: This argument should contain the tool object the function will return the position of.
        :type tool: Tool
        :return: This function returns two numeric values containing the X and Y co-ordinates of the tool.
        :rtype: list(float, float)
        """
        if not isinstance(tool, Tool):
            tool = Tool(tool)

        return self._reference.GetPos(tool._reference)

    def get_scale(self):
        """ Return the current scale of the FlowView.

        :return: This function returns a numeric value indicating the current scale of the FlowView.
        :rtype: float
        """
        return self._reference.GetScale()

    def set_scale(self, scale):
        """ Rescales the FlowView to the amount specified.

        A value of 1 for the scale argument would set the FlowView to 100%.
        While a value of 0.1 would set it to 10% of the default scale.

        :type scale: float
        """
        return self._reference.SetScale(scale)

    def frame_all(self):
        """ This function will rescale and reposition the FlowView to contain all tools. """
        self._reference.FrameAll()


class Attribute(PyNode):
    # GetTool               Get Tool this Attribute belongs to

    def get(self, time=None):
        """ Get the value of this Attribute.

            If time is provided the value is evaluated at that specific time, otherwise current time is used.
        """
        if time is None:
            time = self.tool().comp().get_current_time()

        return self._reference[time]

    def disconnect(self):
        pass

    def tool(self):
        """ Return the Tool this Attribute belongs to """
        return Tool(self._reference.GetTool())


class Input(Attribute):
    # GetExpression
    # SetExpression
    # WindowControlsVisible
    # HideWindowControls
    # ViewControlsVisible
    # HideViewControls
    # GetConnectedOutput
    # GetKeyFrames
    # ConnectTo
    # input[time] == value
    def connect_output(self, output):
        if not isinstance(output, Output):
            output = Output(output)

        self._reference.ConnectTo

    def connection(self):
        other = self._reference.GetConnectedOutput()
        if other:
            return Output(other)

    def get_expression(self):
        """ This function returns the expression string shown within the Input's Expression field.

        :return: Returns the simple expression string from a given input if any, or an empty string if not.
        :rtype: str
        """
        return self._reference.GetExpression()

    def set_expression(self, expression):
        """ This function set the Expression field for the Input to the given string.

        :param expression: A simple expression string.
        :type expression: str
        """
        self._reference.SetExpression(expression)

    def get_keyframes(self):
        return self._reference.GetKeyFrames().values()

    def is_connected(self):
        return bool(self._reference.GetConnectedOutput())


class Output(Attribute):
    # GetValue	            Retrieve the Output's value at the given time
    # GetValueMemBlock	    Retrieve the Output's value as a MemBlock
    # EnableDiskCache	    Controls disk-based caching
    # ClearDiskCache	    Clears frames from the disk cache
    # ShowDiskCacheDlg	    Displays the Cache-To-Disk dialog for user interaction
    # GetConnectedInputs	Returns a table of Inputs connected to this Output
    def connections(self):
        return [Input(x) for x in self._reference.GetConnectedInputs().values()]

    def is_connected(self):
        return any(self._reference.GetConnectedInputs().values())

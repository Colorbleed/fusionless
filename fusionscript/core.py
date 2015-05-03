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
        # TODO: Check if could be optimized (micro-optimization) by getting something that returns less values or \
        #       might already be retrievable from the PyRemoteObject.
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

    def name(self):
        """ The internal Fusion Name as string of the node this PyNode references.

        :return: A string value containing the internal Name of this node.
        :rtype: str
        """
        return self._reference.Name

    def id(self):
        """ The internal Fusion ID as string of the node this PyNode references.

        :return: A string value containing the internal ID of this node.
        :rtype: str
        """
        return self._reference.ID

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
    """ A Tool is a single operator/node in your composition.

    You can use this object to perform changes to a single tool (or make connections with another) or query information.
    For example renaming, deleting, connecting and retrieving its inputs/outputs.
    """
    def get_pos(self):
        """ This function will return the X and Y position this tool in the FlowView.

        :return: This function returns two numeric values containing the X and Y co-ordinates of the tool.
        :rtype: list(float, float)
        """
        flow = comp.CurrentFrame.FlowView
        return flow.GetPosTable(self._reference).values()

    def set_pos(self, pos):
        """ Reposition this tool.

        :param pos: Numeric values specifying the x and y co-ordinates for the tool in the FlowView.
        :type pos: list(float, float)
        """
        flow = comp.CurrentFrame.FlowView
        flow.SetPos(self._reference, *pos)

    def connect_main(self, tool, from_index=1, to_index=1):
        """ Helper function that quickly connects main outputs to another tool's main inputs.

        :param tool: The other tool to connect to.
        :param from_index: The index of the main output on thjis tool. (Indices start at 1)
        :param to_index:  The index of the main input on the other tool. (Indices start at 1)
        """
        if not isinstance(tool, Tool):
            tool = Tool(tool)

        id = tool._reference.FindMainInput(1).ID
        tool._reference[id] = self._reference.FindMainOutput(1)     # connect

    # def attr(self, id):
    #     # TODO: Fusion differentiaties between Outputs and Inputs so a 'global' attr function is confusing.
    #     #       Maybe opt for self.input(id) and self.output(id) to retrieve the respective types.
    #     return Attribute(self._reference[id])

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
        """ Sets the name for this Tool to `name`.

        :param name: The name to change to.
        :type name: str
        """
        self._reference.SetAttrs({'TOOLB_NameSet': True, 'TOOLS_Name': name})

    def clear_name(self):
        """ Clears the user-defined name for this tool and resets it to automated internal name. """
        self._reference.SetAttrs({'TOOLB_NameSet': False, 'TOOLS_Name': ''})

    def delete(self):
        """ Removes the tool from the composition.

        Note:
        This also releases the handle to the Fusion Tool object, setting it to nil.
        This directly invalidates this Tool instance.
        """
        self._reference.Delete()

    def refresh(self):
        """ Refreshes the tool, showing updated user controls.

        Note:
        Internally calling Refresh in Fusion will invalidate the handle to internal object this tool references.
        You have to save the new handle that is returned (even though the documentation above says nothing is returned).
        Calling this function on this Tool will invalidate other Tool instances referencing this same object.
        But it will update the reference in this instance on which the function call is made.
        """
        new_ref = self._reference.Refresh()
        self._reference = new_ref

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
        """ Return the Comp this Tool associated with. """
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

    # TODO: Implement `Tool.get_input(id)` or something similar to easily retrieve a specific input (or list_input()?)
    # TODO: Implement `Tool.get_input(id)` or something similar to easily retrieve a specific output


class Flow(PyNode):
    """ The Flow is the node-based overview of you Composition.

    Fusion's internal name: `FlowView`
    """

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

    def queue_set_pos(self, tool, pos):
        """ Queues the moving of a tool to a new position.

        This function improves performance if you want to move a lot of tools at the same time.
        For big graphs and loops this is preferred over `set_pos` and `get_pos`

        Added in Fusion 6.1: FlowView::QueueSetPos()

        Example
            >>> c = Comp()
            >>> tools = c.get_selected_tools()
            >>> flow = c.flow()
            >>> for i, tool in enumerate(tools):
            >>>     pos = [i, 0]
            >>>     flow.queue_set_pos(tool, pos)
            >>> flow.flush_set_pos()    # here the tools are actually moved
        """
        return self._reference.QueueSetPos(tool._reference, pos[0], pos[1])

    def flush_set_pos_queue(self, tool, pos):
        """ Moves all tools queued with `queue_set_pos`.

        This function improves performance if you want to move a lot of tools at the same time.
        For big graphs and loops this is preferred over `set_pos` and `get_pos`.

        Added in Fusion 6.1: FlowView::FlushSetPosQueue()
        """
        return self._reference.FlushSetPosQueue()

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

    def select(self, tool=None, state=True):
        """ Select or deselect tools or clear the selection in this Flow.

        This function will add or remove the tool specified in it's first argument from the current tool selection set.
        The second argument should be set to False to remove the tool from the selection, or to True to add it.
        If called with no arguments, the function will clear all tools from the current selection.

        :param tool:
        :type tool: Tool
        :param state: Setting this argument to false will deselect the tool specified in the first argument. O
                      Otherwise the default value of true is used, which selects the tool.
        :type state: bool
        :return: This function does not return a value.
        """
        if tool is None:
            return self._reference.Select() # clear selection
        elif not isinstance(tool, Tool):
            tool = Tool(tool)

        self._reference.Select(tool._reference, state)


class Attribute(PyNode):
    """ The Attribute is the base class for Fusion's Input and Output types. """

    def tool(self):
        """ Return the Tool this Attribute belongs to """
        return Tool(self._reference.GetTool())

    # TODO: Implement `Attribute.connections` if such method/implementation would make sense for both Input/Output
    # def connections(self):
    #     raise NotImplementError()


class Input(Attribute):
    """ An Input is any attributes that can be set or connected to by the user on the incoming side of a tool.

    .. note:: These are the input knobs in the Flow view, but also the input values inside the Control view for a Tool.

    Because of the way node-graphs work any value that goes into a Tool required to process the information should
    result (in most scenarios) in a reproducible output under the same conditions.
    """
    def get_value(self, time=None):
        """ Get the value of this Input at the given time.

            If time is provided the value is evaluated at that specific time, otherwise current time is used.
        """
        if time is None:
            time = self._reference.GetTool().Composition.CurrentTime # optimize over going through PyNodes (??)
            # time = self.tool().comp().get_current_time()

        return self._reference[time]

    def connect_to(self, output):
        """ Connect this Input to another Output setting an incoming connection for this tool.

        :param output: The Output to connect to.
        :type output: Output
        """

        # disconnect
        if output is None:
            self._reference.ConnectTo(None)
            return

        # or connect
        if not isinstance(output, Output):
            output = Output(output)

        self._reference.ConnectTo(output._reference)

    def disconnect(self):
        """ Disconnect the Output this Input is connected to, if any. """
        self.connect_to(None)

    def get_connected_output(self):
        """ Returns the output that is connected to a given input.

        :return: Output this Input is connected to if any, else None.
        """
        other = self._reference.GetConnectedOutput()
        if other:
            return Output(other)

    def get_expression(self):
        """ Returns the expression string shown within the Input's Expression field.

        :return: Returns the simple expression string from a given input if any, or an empty string if not.
        :rtype: str
        """
        return self._reference.GetExpression()

    def set_expression(self, expression):
        """ Set the Expression field for the Input to the given string.

        :param expression: A simple expression string.
        :type expression: str
        """
        self._reference.SetExpression(expression)

    def get_keyframes(self):
        """ Return the times at which this Input has keys.

        :return: List of int values indicating frames.
        :rtype: list
        """
        return self._reference.GetKeyFrames().values()

    def is_connected(self):
        """ Return whether the Input is an incoming connection from an Output

        :return: True if connected, otherwise False
        :rtype: bool
        """
        return bool(self._reference.GetConnectedOutput())

    def data_type(self):
        """ Returns the type of Parameter (e.g. Number, Point, Text, Image) this Input accepts.

        :return: Type of parameter.
        :rtype: str
        """
        return self._reference.GetAttrs()['OUTS_DataType']

    # TODO: implement `Input.WindowControlsVisible`
    # TODO: implement `Input.HideWindowControls`
    # TODO: implement `Input.ViewControlsVisible`
    # TODO: implement `Input.HideViewControls`


class Output(Attribute):
    """ An Output is any attributes that is a result from a Tool that can be connected as input to another Tool.

    .. note:: These are the output knobs in the Flow view.
    """
    def get_value(self, time=None):
        """ Get the value of this Output at the given time.

            If time is provided the value is evaluated at that specific time, otherwise current time is used.

        :param time: Time at which to evaluate the Output. If none provided current time will be used.
        """
        return self.get_value_attrs(time=time)[0]

    def get_value_attrs(self, time=None):
        """ Return a tuple of value and attrs for this Output.

         `value` may be None, or a variety of different types:

            Number 	- returns a number
            Point 	- returns a table with X and Y members
            Text 	- returns a string
            Clip 	- returns the filename string
            Image 	- returns an Image object

        `attrs` is a dictionary with the following entries:

            Valid 	- table with numeric Start and End entries
            DataType 	- string ID for the parameter type
            TimeCost 	- time take to render this parameter

        :param time: Time at which to evaluate the Output. If none provided current time will be used.
        :return: value and attributes of this output at the given time.
        """
        if time is None:
            time = self._reference.GetTool().Composition.CurrentTime # optimize over going through PyNodes (??)
            # time = self.tool().comp().get_current_time()

        return self._reference.GetValue(time)

    def get_time_cost(self, time=None):
        """ Return the time taken to render this parameter at the given time.

        .. note:: This will evaluate the output and could be computationally expensive.

        :param time: Time at which to evaluate the Output. If none provided current time will be used.
        :return: Time taken to render this Output.
        :rtype: float
        """
        return self.get_value_attrs(time=time)[1]['TimeCost']

    def disconnect(self, inputs=None):
        """ Disconnect all the Inputs this Output is connected to (or only those given as Inputs). """

        if inputs is None:      # disconnect all (if any)
            inputs = self.get_connected_inputs()
        else:                   # disconnect a subset of the connections (if valid)
            # ensure iterable
            if not isinstance(inputs, (list, tuple)):
                inputs = [inputs]

            # ensure all are Inputs
            inputs = [Input(input) for input in inputs]

            # ensure Inputs are connected to this output
            connected_inputs = set(self._reference.GetConnectedInputs().values())
            inputs = [input for input in inputs if input._reference in connected_inputs]

        for input in inputs:
            input._reference.ConnectTo(None)

    def get_connected_inputs(self):
        """ Returns a list of all Inputs that are connected to this Output.

        :return: List of Inputs connected to this Output.
        :rtype: list
        """
        return [Input(x) for x in self._reference.GetConnectedInputs().values()]

    def get_dod(self):
        """ Return the Domain of Definition for this output.

        :return: The domain of definition for this output in the as list of integers ordered: left, bottom, right, top.
        :rtype: [int, int, int, int]
        """
        return self._reference.GetDoD()

    # region connections
    def connect_to(self, input):
        """ Connect this Output to another Input gaining an outgoing connection for this tool.

        :param input: The Input to connect to.
        :type input: Input
        """
        if not isinstance(input, Input):
            input = Input(input)

        input.connect_to(self)

    def is_connected(self):
        """ Return whether the Output has any outgoing connection to any Inputs.

        :return: True if connected, otherwise False
        :rtype: bool
        """
        return any(self._reference.GetConnectedInputs().values())

    def data_type(self):
        """ Returns the type of Parameter (e.g. Number, Point, Text, Image) this Output accepts.

        :return: Type of parameter.
        :rtype: str
        """
        return self._reference.GetAttrs()['INPS_DataType']

    # TODO: implement `Output.GetValueMemBlock`	    Retrieve the Output's value as a MemBlock
    # TODO: implement `Output.EnableDiskCache`      Controls disk-based caching
    # TODO: implement `Output.ClearDiskCache`       Clears frames from the disk cache
    # TODO: implement `Output.ShowDiskCacheDlg`     Displays the Cache-To-Disk dialog for user interaction

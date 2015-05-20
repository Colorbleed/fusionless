"""
    Contains the main `PyNode` base class.
    And for now also all its derived classes.

    Note that this package is an early release (consider it pre-alpha public development).
    Here's a community-built list of Fusion's built-in classes:
    http://www.steakunderwater.com/VFXPedia/96.0.243.189/index8c76.html?title=Eyeon:Script/Reference/Applications/Fusion/Classes

    Most of the methods and class types available in Fusion will still have to be added and implemented in this
    `fusionscript` package.

"""


class PyObject(object):
    """ This is the base class for all classes referencing Fusion's classes.

    Upon initialization of any PyObject class it checks whether the referenced data is of the correct type using
    Python's special `__new__` method. This way we convert the instance to correct class type based on the internal
    Fusion type.

    The `PyObject` is *fusionscript*'s class representation of Fusion's internal Object class.
    All the other classes representing Fusion objects are derived from PyObject.

    Example
        >>> node = PyObject(comp)
        >>> print type(node)
        >>> # Comp()

    At any time you can access Fusion's python object from the instance using the `_reference` attribute.

    Example
        >>> node = PyObject()
        >>> reference = node._reference
        >>> print reference
    """

    _reference = None   # reference to PyRemoteObject
    _default_reference = None

    def __new__(cls, *args, **kwargs):

        reference = args[0] if args else None
        if isinstance(reference, cls):  # if argument provided is already of correct class type return it
            return reference
        elif reference is None:           # if no arguments assume reference to default type for cls (if any)
            if cls._default_reference is not None:
                reference = cls._default_reference
            else:
                raise ValueError("Can't instantiate a PyObject with a reference to None")

        # Acquire an attribute to check for type (start prefix)
        # TODO: Check if could be optimized (micro-optimization) by getting something that returns less values or \
        #       might already be retrievable from the PyRemoteObject.

        # Check if the reference is a PyRemoteObject. Since we don't have access to the class type that fusion returns
        # outside of Fusion we use a hack based on its name
        if type(reference).__name__ != 'PyRemoteObject':
            raise TypeError("Reference is not of type PyRemoteObject but {0}".format(type(reference).__name__))

        newcls = None
        attrs = reference.GetAttrs()
        if attrs:
            # Comp, Tool, Input, Output, View, etc. all return attributes that define its type
            data_type = next(iter(attrs))

            # Define the new class type
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

        else:
            # Image (output value) does not return attributes from GetAttrs() so we use some data from the PyRemoteObject
            str_data_type = str(reference).split(' ', 1)[0]

            if str_data_type == "Image":
                newcls = Image

        # Ensure we convert to a type preferred by the user
        # eg. currently Tool() would come out as Comp() since no arguments are provided.
        #     so instead we provide a TypeError() to be clear in those instances.
        if cls is not PyObject:
            if not issubclass(newcls, cls):
                raise TypeError("PyObject did not convert to preferred type. '{0}' is not an instance of '{1}'".format(newcls, cls))

        # Instantiate class and return
        if newcls:
            klass = super(PyObject, cls).__new__(newcls)
            klass._reference = reference
            return klass

        return None

    def set_attr(self, key, value):
        self._reference.SetAttrs({key: value})

    def get_attrs(self):
        return self._reference.GetAttrs()

    def name(self):
        """ The internal Fusion Name as string of the node this PyObject references.

        :return: A string value containing the internal Name of this node.
        :rtype: str
        """
        return self._reference.Name

    def get_help(self):
        """ Returns a formatted string of internal help information to Fusion.

        :return: internal Fusion information
        :rtype: str
        """
        return self._reference.GetHelp()

    def get_reg(self):
        """ Returns the related Registry instance for this PyObject.

        :return: The registry related to this object.
        :rtype: Registry
        """
        return self._reference.GetReg()

    def id(self):
        """ The internal Fusion ID as string of the node this PyObject references.

        .. note:: This uses the internal `GetID()` method on the `Object` instance.

        :return: A string value containing the internal ID of this node.
        :rtype: str
        """
        return self._reference.GetID()

    def __getattr__(self, attr):
        """ Allow access to Fusion's built-in methods on the reference directly.

        .. note:: Since the normal behaviour is to raise a very confusing TypeError whenever an unknown method is called
                  on the PyRemoteObject so we added a raise a more explanatory error if we retrieve unknown data.
        """
        result = getattr(self._reference, attr)
        if result is None:
            raise AttributeError("{0} object has no attribute '{1}'".format(self, attr))

        return result

    def __repr__(self):
        return '{0}("{1}")'.format(self.__class__.__name__, str(self._reference.Name))

    # TODO: Implement PyObject.GetApp
    # TODO: Implement PyObject.Comp/Composition
    # TODO: Implement PyObject.SetData
    # TODO: Implement PyObject.GetData
    # TODO: Implement PyObject.TriggerEvent


class Comp(PyObject):
    """ A Comp instance refers to a Fusion composition.

    Here you can perform the global changes to the current composition.
    """
    _default_reference = comp

    # TODO: Finish the `Comp` docstring documentations
    # TODO: Implement the rest of the `Comp` methods.

    def get_current_time(self):
        return self._reference.CurrentTime

    def get_selected_tools(self, node_type=None):
        args = (node_type,) if node_type is not None else tuple()
        return [Tool(x) for x in self._reference.GetToolList(True, *args).values()]

    def get_active_tool(self):
        """
        :return: Turrently active tool on this comp
        """
        return Tool(self._reference.ActiveTool)

    def set_active_tool(self, tool):

        if tool is None:
            self._reference.SetActiveTool(None)
            return

        if not isinstance(tool, Tool):
            tool = Tool(tool)

        self._reference.SetActiveTool(tool._reference)

    def create_tool(self, node_type, attrs=None, insert=False, name=None):
        """ Creates a new node in the composition based on the node type.

        :param node_type:
        :type node_type: str
        :param attrs: A dictionary of input values to set.
        :type attrs: dict
        :param insert: If True the node gets created and automatically inserted/connected to the active tool.
        :type insert: bool
        :param name: If name provided the created node is automatically renamed to the provided name.
        :type name: str

        :return: The created Tool instance.
        :rtype: Tool
        """
        args = (-32768, -32768) if insert else tuple()
        tool = Tool(self._reference.AddTool(node_type, *args))
        if attrs:
            tool._reference.SetAttrs(attrs)

        if name:
            tool.rename(name)

        return tool

    def copy(self, tools):
        return self._reference.Copy([tool._reference for tool in tools])

    def paste(self, values=None):
        args = tuple() if values is None else (values,)
        return self._reference.Paste(*args)

    def lock(self):
        """ Sets the composition to a locked state.

        Sets a composition to non-interactive ("batch", or locked) mode.
        This makes Fusion suppress any dialog boxes which may appear, and additionally prevents any re-rendering in
        response to changes to the controls. A locked composition can be unlocked with the unlock() function, which
        returns the composition to interactive mode.

        It is often useful to surround a script with Lock() and Unlock(), especially when adding tools or modifying a
        composition. Doing this ensures Fusion won't pop up a dialog to ask for user input, e.g. when adding a Loader,
        and can also speed up the operation of the script since no time will be spent rendering until the comp is
        unlocked.

        For convenience this is also available as a Context Manager as `fusionscript.context.LockComp`.
        """
        self._reference.Lock()

    def unlock(self):
        """ Sets the composition to an unlocked state. """
        self._reference.Unlock()

    def redo(self, num=1):
        """ Redo one or more changes to the composition.

        :param num: Amount of changes to redo.
        :type num: int
        """
        self._reference.Redo(num)

    def undo(self, num):
        """ Undo one or more changes to the composition.

        :param num: Amount of changes to undo.
        :type num: int
        """
        self._reference.Undo(num)

    def start_undo(self, name):
        """
        The StartUndo() function is always paired with an EndUndo() function.
        Any changes made to the composition by the lines of script between StartUndo() and EndUndo() are stored as a
        single Undo event.

        Changes captured in the undo event can be undone from the GUI using CTRL-Z, or the Edit menu.
        They can also be undone from script, by calling the `undo()` method.

        .. note::
            If the script exits before `end_undo()` is called Fusion will automatically close the undo event.

        :param name: specifies the name displayed in the Edit/Undo menu of the Fusion GUI a string containing the
                     complete path and name of the composition to be saved.
        :type name: str
        """
        self._reference.StartUndo(name)

    def end_undo(self, keep):
        """
        The `start_undo()` is always paired with an `end_undo()` call.
        Any changes made to the composition by the lines of script between `start_undo()` and `end_undo()` are stored as
        a single Undo event.

        Changes captured in the undo event can be undone from the GUI using CTRL-Z, or the Edit menu.
        They can also be undone from script, by calling the `undo()` method.

        Specifying 'True' results in the undo event being added to the undo stack, and appearing in the appropriate
        menu. Specifying False' will result in no undo event being created. This should be used sparingly, as the user
        (or script) will have no way to undo the preceding commands.

        .. note::
            If the script exits before `end_undo()` is called Fusion will automatically close the undo event.

        :param keep: Determines whether the captured undo event is to kept or discarded.
        :type keep: bool
        """
        self._reference.EndUndo(keep)

    def clear_undo(self):
        """ Use this function to clear the undo/redo history for the composition. """
        self._reference.ClearUndo()

    def save(self):
        """ Save the composition. """
        self._reference.Save()

    def play(self):
        """ This function is used to turn on the play control in the playback controls of the composition. """
        self._reference.Play()

    def stop(self):
        """ This function is used to turn off the play control in the playback controls of the composition. """
        self._reference.Stop()

    def render(self, wait_for_render, **kwargs):
        """ Renders the composition.

        Args:
            wait_for_render (bool): Whether the script should wait for the render to complete or continue processing
                                    once the render has begun. Defaults to False

        Kwargs:
            start (int): The frame to start rendering at. Default: Comp's render start settings.
            end (int): The frame to stop rendering at. Default: Comp's render end settings.
            high_quality (bool): Render in High Quality (HiQ). Default True.
            render_all (bool): Render all tools, even if not required by a saver. Default False.
            motion_blur (bool): Do motion blur in render, where specified in tools. Default true.
            size_type (int): Resize the output:
                                -1. Custom (only used by PreviewSavers during a preview render)
                                 0. Use prefs setting
                                 1. Full Size (default)
                                 2. Half Size
                                 3. Third Size
                                 4. Quarter Size
            width (int): Width of result when doing a Custom preview (defaults to pref)
            height (int): Height of result when doing a Custom preview (defaults to pref)
            keep_aspect (bool): Maintains the frame aspect when doing a Custom preview.
                                Defaults to Preview prefs setting.
            step_render (bool): Render only 1 out of every X frames ("shoot on X frames") or render every frame.
                                Defaults to False.
            steps (int): If step rendering, how many to step. Default 5.
            use_network (bool): Enables rendering with the network. Default False.
            groups (str):
            flags (number):
            tool (Tool): A tool to render up to. If this is specified only sections of the comp up to this tool will be
                         rendered. eg you could specify comp.Saver1 to only render *up to* Saver1, ignoring any tools
                         (including savers) after it.
            frame_range (str): Describes which frames to render. (eg "1..100,150..180").
                               Defaults to "Start".."End"

        Returns:
            True if the composition rendered successfully, None if it failed to start or complete.
        """
        # convert our 'Pythonic' keyword arguments to Fusion's internal ones.
        conversion = {'start': 'Start',
                      'end': 'End',
                      'high_quality': 'HiQ',
                      'render_all': 'RenderAll',
                      'motion_blur': 'MotionBlur',
                      'size_type': 'SizeType',
                      'width': 'Width',
                      'height': 'Height',
                      'keep_aspect': 'KeepAspect',
                      'step_render': 'StepRender',
                      'steps': 'Steps',
                      'use_network': 'UseNetwork',
                      'groups': 'Groups',
                      'flags': 'Flags ',
                      'tool': 'Tool ',
                      'frame_range': 'FrameRange'}
        for key, new_key in conversion.iteritems():
            if key in kwargs:
                value = kwargs.pop(key)
                kwargs[new_key] = value

        # use our required argument
        required_kwargs = {'Wait': wait_for_render}
        kwargs.update(required_kwargs)

        return self._reference.Render(**kwargs)

    def render_range(self, wait_to_render, start, end, steps=1, **kwargs):
        """ A render that specifies an explicit render range.

        Args:
            wait_for_render (bool): Whether the script should wait for the render to complete or continue processing
                                    once the render has begun. Defaults to False
            start (int): The frame to start rendering at.
            end (int): The frame to stop rendering at.
            steps (int): If step rendering, how many to step. Default 1.

        Kwargs:
            See `Comp.render()` method.

        Returns:
            True if the composition rendered successfully, None if it failed to start or complete.
        """
        range_kwargs = {'start': start,
                        'end': end,
                        'steps': steps}
        kwargs.update(range_kwargs)

        return self.render(wait_to_render=wait_to_render, **kwargs)

    def run_script(self, filename):
        """ Run a script within the composition's script context

        Use this function to run a script in the composition environment.
        This is similar to launching a script from the comp's Scripts menu.

        The script will be started with 'fusion' and 'composition' variables set to the Fusion and currently active
        Composition objects. The filename given may be fully specified, or may be relative to the comp's Scripts: path.

        Since version 6.3.2 you can run Python and eyeonScripts.
        Fusion supports .py .py2 and .py3 extensions to differentiate python script versions.

        :param filename: The filename of a script to be run in the composition environment.
        :type filename: str
        """
        self._reference.RunScript(filename)

    def is_rendering(self):
        """ Returns True if the comp is busy rendering.

        Use this method to determine whether a composition object is currently rendering.
        It will return True if it is playing, rendering, or just rendering a tool after trying to view it.

        :rtype: bool
        """
        return self._reference.IsRendering()

    def is_playing(self):
        """ Returns True if the comp is being played.

        Use this method to determine whether a composition object is currently playing.

        :rtype: bool
        """
        return self._reference.IsPlaying()

    def is_locked(self):
        """ Returns True if the comp is being played.

        Use this method to see whether a composition is locked or not.

        :rtype: bool
        """
        return self._reference.IsPlaying()

    def __repr__(self):
        filename = self._reference.GetAttrs()['COMPS_FileName']
        return '{0}("{1}")'.format(self.__class__.__name__, filename)


class Tool(PyObject):
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

    # region inputs
    def main_input(self, index):
        """ Returns the main (visible) Input knob of the tool, by index.

        .. note:: The index starts at 1!

        :param index: numerical index of the knob
        :type index: int
        :return: Input at the given index.
        :rtype: Input
        """
        return Input(self._reference.FindMainInput(index))

    def input(self, id):
        """ Returns an Input by ID.

        :param id: ID of the Input
        :type id: str
        :return: Output at the given index.
        :rtype: Output
        """
        return Input(self._reference[id])

    def inputs(self):
        """ Return all Inputs of this Tools """
        return [Input(x) for x in self._reference.GetInputList().values()]
    # endregion

    # region outputs
    def main_output(self, index):
        """ Returns the main (visible) Output knob of the tool, by index.

        .. note:: The index starts at 1!

        :param index: numerical index of the knob
        :type index: int
        :return: Output at the given index.
        :rtype: Output
        """
        return Output(self._reference.FindMainOutput(index))

    def output(self, id):
        """ Returns the Output knob by ID.

        :param id: ID of the Output.
        :type id: str
        :return: Output at the given index.
        :rtype: Output
        """
        # TODO: Optimize `Tool.output(id)`, there must be a more optimized way than doing it like this.
        output_reference = next(x for x in self.outputs() if x.ID == id)
        if not output_reference:
            return None
        else:
            return Output(output_reference)

    def outputs(self):
        """ Return all Outputs of this Tools """
        return [Output(x) for x in self._reference.GetOutputList().values()]
    # endregion

    # region connections
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

    def disconnect(self, inputs=True, outputs=True):
        """ Disconnect all inputs and outputs of this tool. """
        if inputs:
            for input in self.inputs():
                input.disconnect()

        if outputs:
            for output in self.outputs():
                output.disconnect()

    # TODO: Implement 'Tool.connections()'
    def connections(self, inputs=True, outputs=True):
        """ Return all Connections of Inputs and Outputs of this Tools """
        raise NotImplementedError()
    # endregion

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

    def get_text_color(self):
        """ Gets the Tool's text color. """
        return self._reference.TextColor

    def set_text_color(self, color):
        """ Sets the Tool's text color.

        Example
            >>> tool.set_text_color({'R':0.5, 'G':0.1, 'B': 0.0})
            >>> tool.set_text_color(None)
        """
        self._reference.TextColor = color

    def get_tile_color(self):
        """ Gets the Tool's tile color. """
        return self._reference.TileColor

    def set_tile_color(self, color):
        """ Sets the Tool's tile color.

        Example
            >>> tool.set_tile_color({'R':0.5, 'G':0.1, 'B': 0.0})
            >>> tool.set_tile_color(None)   # reset
        """
        self._reference.TileColor = color

    # TODO: Implement `Tool.get_input(id)` or something similar to easily retrieve a specific input (or list_input()?)
    # TODO: Implement `Tool.get_output(id)` or something similar to easily retrieve a specific output
    # TODO: Implement `Tool.has_keys()` to easily retrieve whether the tool has any keys
    # TODO: Implement `Tool.remove_keys()` to easily remove all keys on all inputs


class Flow(PyObject):
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


class Link(PyObject):
    """ The Link is the base class for Fusion's Input and Output types. """

    def tool(self):
        """ Return the Tool this Link belongs to """
        return Tool(self._reference.GetTool())

    # TODO: Implement `Link.connections` if such method/implementation would make sense for both Input/Output
    # def connections(self):
    #     raise NotImplementError()


class Input(Link):
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

        .. note:: This function behaves similarly to right clicking on a property, selecting Connect To, and selecting
                  the property you wish to connect the input to. In that respect, if you try to connect non-similar
                  data types (a path's value to a polygon's level, for instance) it will not connect the values.
                  Such an action will yield NO error message.

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


class Output(Link):
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

        .. note:: This function behaves similarly to right clicking on a property, selecting Connect To, and selecting
                  the property you wish to connect the input to. In that respect, if you try to connect non-similar
                  data types (a path's value to a polygon's level, for instance) it will not connect the values.
                  Such an action will yield NO error message.

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


class Parameter(PyObject):
    """ Base class for all parameter (values) types """
    pass


class Image(Parameter):
    pass


class TransformMatrix(Parameter):
    pass


class Fusion(PyObject):
    _default_reference = fusion
    # TODO: Implement Fusion methods: http://www.steakunderwater.com/VFXPedia/96.0.243.189/index5522.html?title=Eyeon:Script/Reference/Applications/Fusion/Classes/Fusion


class Registry(PyObject):
    """ Represents a type of object within Fusion """
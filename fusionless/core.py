"""
Contains the main `PyNode` base class and its derived classes.

### Reference

For a community-built class list of Fusion's built-in classes:
http://www.steakunderwater.com/VFXPedia/96.0.243.189/index8c76.html?title=Eyeon:Script/Reference/Applications/Fusion/Classes
"""

import sys


class PyObject(object):
    """This is the base class for all classes referencing Fusion's classes.

    Upon initialization of any PyObject class it checks whether the referenced
    data is of the correct type usingbPython's special `__new__` method.

    This way we convert the instance to correct class type based on the
    internal Fusion type.

    The `PyObject` is *fusionscript*'s class representation of Fusion's
    internal Object class. All the other classes representing Fusion objects
    are derived from PyObject.

    Example
        >>> node = PyObject(comp)
        >>> print type(node)
        >>> # Comp()

    At any time you can access Fusion's python object from the instance using
    the `_reference` attribute.

    Example
        >>> node = PyObject()
        >>> reference = node._reference
        >>> print reference
        
    """

    _reference = None   # reference to PyRemoteObject
    _default_reference = None

    def __new__(cls, *args, **kwargs):
        """Convert the class instantiation to the correct type.

        This is where the magic happens that automatically maps any of the
        PyNode objects to the correct class type.

        """

        reference = args[0] if args else None
        # if argument provided is already of correct class type return it
        if isinstance(reference, cls):
            return reference
        # if no arguments assume reference to default type for cls (if any)
        elif reference is None:
            if cls._default_reference is not None:
                reference = cls._default_reference()
                if reference is None:
                    raise RuntimeError("No default reference for: "
                                       "{0}".format(type(reference).__name__))
            else:
                raise ValueError("Can't instantiate a PyObject with a "
                                 "reference to None")

        # Python crashes whenever you perform `type()` or `dir()` on the
        # PeyeonScript.scripapp() retrieved applications. As such we try to
        # get the attributes before that check before type-checking in case
        # of errors.
        attrs = None
        try:
            attrs = reference.GetAttrs()
        except AttributeError:
            # Check if the reference is a PyRemoteObject.
            # Since we don't have access to the class type that fusion returns
            # outside of Fusion we use a hack based on its name
            if type(reference).__name__ != 'PyRemoteObject':
                raise TypeError("Reference is not of type PyRemoteObject "
                                "but {0}".format(type(reference).__name__))

        newcls = None
        if attrs:
            # Acquire an attribute to check for type (start prefix)
            # Comp, Tool, Input, Output, View, etc. all return attributes
            # that define its type
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
            elif data_type.startswith("FUSION"):
                newcls = Fusion

        else:
            # Image (output value) does not return attributes from GetAttrs()
            # so we use some data from the PyRemoteObject
            str_data_type = str(reference).split(' ', 1)[0]

            if str_data_type == "Image":
                newcls = Image

        # Ensure we convert to a type preferred by the user
        # eg. Tool() would come out as Comp() since no arguments are provided.
        #     so instead we raise a TypeError() to be clear in those cases.
        if cls is not PyObject:
            if not issubclass(newcls, cls):
                raise TypeError("PyObject did not convert to preferred "
                                "type. '{0}' is not an instance "
                                "of '{1}'".format(newcls, cls))

        # Instantiate class and return
        if newcls:
            klass = super(PyObject, cls).__new__(newcls)
            klass._reference = reference
            return klass

        return None

    def set_attr(self, key, value):
        self.set_attrs({key: value})

    def get_attr(self, key):
        attrs = self.get_attrs()
        return attrs[key]

    def set_attrs(self, attr_values):
        self._reference.SetAttrs(attr_values)

    def get_attrs(self):
        return self._reference.GetAttrs()

    def set_data(self, name, value):
        """ Set persistent data on this object.

        Persistent data is a very useful way to store names, dates, filenames, notes, flags, or anything else, in such a
        way that they are permanently associated with this instance of the object, and are stored along with the object.
        This data can be retrieved at any time by using `get_data()`.

        The method of storage varies by object:
        - Fusion application:
            SetData() called on the Fusion app itself will save its data in the  Fusion.prefs file, and will be
            available whenever that copy of Fusion is running.

        - Objects associated with a composition:
            Calling SetData() on any object associated with a Composition will cause the data to be saved in the .comp
            file, or in any settings files that may be saved directly from that object.

        - Ephemeral objects not associated with composition:
            Some ephemeral objects that are not associated with any composition and are not otherwise saved in any way,
            may not have their data permanently stored at all, and the data will only persist as long as the object
            itself does.

        .. note::
            You can use SetData to add a key called HelpPage to any tool. Its value can be a URL to a web page (for
            example a link to a page on Vfxpedia) and will override this tool's default help when the user presses F1
            (requires Fusion 6.31 or later). It's most useful for macros.

            Example
                >>> PyNode(comp).set_data('HelpPage', 'https://github.com/BigRoy/fusionscript')

        :param name: This is the name of the attribute to set. As of 5.1, this name can be in "table.subtable" format,
                     to allow setting persistent data within subtables.
        :param value: This is the value to be recorded in the object's persistent data. It can be of almost any type.
        """
        self._reference.SetData(name, value)

    def get_data(self, name):
        """ Get persistent data from this object.

        Args:
            name (str): The name of the attribute to fetch.

        Returns:
            The value fetched from the object's persistent data.
            It can be of almost any type.

        """
        return self._reference.GetData(name)

    def name(self):
        """The internal Fusion Name as string of the node this PyObject
        references.

        Returns:
            str: A string value containing the internal Name of this node.

        """
        return self._reference.Name

    def get_help(self):
        """Returns a formatted string of internal help information to Fusion.

        Returns:
            str: internal Fusion information

        """
        return self._reference.GetHelp()

    def get_reg(self):
        """ Returns the related Registry instance for this PyObject.

        Returns:
            Registry: The registry related to this object.

        """
        return self._reference.GetReg()

    def id(self):
        """Returns the internal Fusion ID as string.

        .. note:: This uses the internal `GetID()` method on the object
            instance that this PyObject references.

        Returns:
            str: Internal ID of the referenced Fusion object

        """
        return self._reference.GetID()

    def comp(self):
        """ Return the Comp this instance belongs to.

        Returns:
            Comp: The composition from this instance.

        """
        return Comp(self._reference.Comp())

    def __getattr__(self, attr):
        """Allow access to Fusion's built-in methods on the reference directly.

        .. note::
            Since the normal behaviour is to raise a very confusing TypeError
            whenever an unknown method is called on the PyRemoteObject so we
            added a raise a more explanatory error if we retrieve unknown data.

        """
        result = getattr(self._reference, attr)
        if result is None:
            raise AttributeError("{0} object has no attribute "
                                 "'{1}'".format(self, attr))

        return result

    def __repr__(self):
        return '{0}("{1}")'.format(self.__class__.__name__,
                                   str(self._reference.Name))

    # TODO: Implement PyObject.GetApp
    # TODO: Implement PyObject.TriggerEvent


class Comp(PyObject):
    """ A Comp instance refers to a Fusion composition.

    Here you can perform the global changes to the current composition.
    """
    # TODO: Implement the rest of the `Comp` methods and its documentations.

    @staticmethod
    def _default_reference():
        """Fallback for the default reference"""
        # this would be accessible within Fusion as "comp"
        return getattr(sys.modules["__main__"], "comp", None)

    def get_current_time(self):
        """ Returns the current time in this composition.

        :return: Current time.
        :rtype: int
        """
        return self._reference.CurrentTime

    def get_tool_list(self, selected=False, node_type=None):
        """ Returns the tool list of this composition.

        Args:
            selected (bool): Whether to return only tools from the current
                selection. When False all tools in the composition will be
                considered.
            node_type (str): If provided filter to only tools of this type.

        Returns:
            list: A list of Tool instances

        """
        args = (node_type,) if node_type is not None else tuple()
        return [Tool(x) for x in self._reference.GetToolList(selected, *args).values()]

    def get_selected_tools(self, node_type=None):
        """Returns the currently selected tools.

        .. warning::
            Fusion does NOT return the selected tool list in the order of
            selection!

        Returns:
            list: A list of selected Tool instances

        """
        return self.get_tool_list(True, node_type=node_type)

    def current_frame(self):
        """ Returns the currently active ChildFrame for this composition.

        ..note ::
            This does not return the current time, but a UI element.
            To get the current time use `get_current_time()`

        Returns:
            The currently active ChildFrame for this Composition.

        """
        return self.CurrentFrame

    def get_active_tool(self):
        """ Return active tool.

        Returns:
            Tool or None: Currently active tool on this comp

        """
        tool = self._reference.ActiveTool
        return Tool(tool) if tool else None

    def set_active_tool(self, tool):
        """ Set the current active tool in the composition to the given tool.

        If tool is None it ensure nothing is active.

        Args:
            tool (Tool): The tool instance to make active.
                If None provided active tool will be deselected.

        Returns:
            None

        """
        if tool is None:    # deselect if None
            self._reference.SetActiveTool(None)
            return

        if not isinstance(tool, Tool):
            tool = Tool(tool)

        self._reference.SetActiveTool(tool._reference)

    def create_tool(self, node_type, attrs=None, insert=False, name=None):
        """ Creates a new node in the composition based on the node type.

        Args:
            node_type (str): The type id of the node to create.
            attrs (dict): A dictionary of input values to set.
            insert (bool): When True the node gets created and automatically
                inserted/connected to the active tool.
            name (str): When provided the created node is automatically
                renamed to the provided name.

        Returns:
            Tool: The created Tool instance.

        """

        # Fusion internally uses the magic 'position' (-32768, -32768) to trigger an automatic connection and insert
        # when creating a new node. So we use that internal functionality when `insert` parameter is True.
        args = (-32768, -32768) if insert else tuple()
        tool = Tool(self._reference.AddTool(node_type, *args))

        if attrs:   # Directly set attributes if any provided
            tool.set_attrs(attrs)

        if name:    # Directly set a name if any provided
            tool.rename(name)

        return tool

    def copy(self, tools):
        """Copy a list of tools to the Clipboard.

        The copied Tools can be pasted into the Composition by using its
        corresponding `paste` method.

        Args:
            tools (list): The Tools list to be copied to the clipboard

        """
        return self._reference.Copy([tool._reference for tool in tools])

    def paste(self, settings=None):
        """Pastes a tool from the Clipboard or a settings table.

        Args:
            settings (dict or None): If settings dictionary provided it will be
                used as the settings table to be copied, instead of using the
                Comp's current clipboard.

        Returns:
            None

        """
        args = tuple() if settings is None else (settings,)
        return self._reference.Paste(*args)

    def lock(self):
        """Sets the composition to a locked state.

        Sets a composition to non-interactive ("batch", or locked) mode.
        This makes Fusion suppress any dialog boxes which may appear, and
        additionally prevents any re-rendering in response to changes to the
        controls. A locked composition can be unlocked with the unlock()
        function, which returns the composition to interactive mode.

        It is often useful to surround a script with Lock() and Unlock(),
        especially when adding tools or modifying a composition. Doing this
        ensures Fusion won't pop up a dialog to ask for user input, e.g. when
        adding a Loader, and can also speed up the operation of the script
        since no time will be spent rendering until the comp is unlocked.

        For convenience this is also available as a Context Manager as
        `fusionscript.context.LockComp`.

        """
        self._reference.Lock()

    def unlock(self):
        """Sets the composition to an unlocked state."""
        self._reference.Unlock()

    def redo(self, num=1):
        """Redo one or more changes to the composition.

        Args:
            num (int): Amount of redo changes to perform.

        """
        self._reference.Redo(num)

    def undo(self, num):
        """ Undo one or more changes to the composition.

        Args:
            num (int): Amount of undo changes to perform.

        """
        self._reference.Undo(num)

    def start_undo(self, name):
        """Start an undo block.

        This should always be paired with an end_undo call.

        The StartUndo() function is always paired with an EndUndo() function.
        Any changes made to the composition by the lines of script between
        StartUndo() and EndUndo() are stored as a single Undo event.

        Changes captured in the undo event can be undone from the GUI using
        CTRL-Z, or the Edit menu. They can also be undone from script, by
        calling the `undo()` method.

        .. note::
            If the script exits before `end_undo()` is called Fusion will
            automatically close the undo event.

        Args:
            name (str): Specifies the name displayed in the Edit/Undo menu of
                the Fusion GUI a string containing the complete path and name
                of the composition to be saved.

        """
        self._reference.StartUndo(name)

    def end_undo(self, keep=True):
        """Close an undo block.

        This should always be paired with a start_undo call.

        The `start_undo()` is always paired with an `end_undo()` call.
        Any changes made to the composition by the lines of script between
        `start_undo()` and `end_undo()` are stored as a single Undo event.

        Changes captured in the undo event can be undone from the GUI using
        CTRL-Z, or the Edit menu. They can also be undone from script, by
        calling the `undo()` method.

        Specifying 'True' results in the undo event being added to the undo
        stack, and appearing in the appropriate menu. Specifying False' will
        result in no undo event being created. This should be used sparingly,
        as the user (or script) will have no way to undo the preceding
        commands.

        .. note::
            If the script exits before `end_undo()` is called Fusion will
            automatically close the undo event.

        Args:
            keep (bool): Determines whether the captured undo event is to kept
                or discarded.

        Returns:
            None

        """
        self._reference.EndUndo(keep)

    def clear_undo(self):
        """Use this function to clear the undo/redo history for the
        composition."""
        self._reference.ClearUndo()

    def save(self):
        """Save the composition."""
        self._reference.Save()

    def play(self):
        """This function is used to turn on the play control in the playback
        controls of the composition.
        """
        self._reference.Play()

    def stop(self):
        """This function is used to turn off the play control in the playback
        controls of the composition.
        """
        self._reference.Stop()

    def loop(self, mode):
        """This function is used to turn on the loop control in the playback
        controls of the composition.

        Args:
            mode (bool): Enables looping interactive playback.

        Returns:
            None

        """
        self._reference.Loop(mode)

    def render(self, wait_for_render, **kwargs):
        """ Renders the composition.

        Args:
            wait_for_render (bool): Whether the script should wait for the
                render to complete or continue processing once the render has
                begun. Defaults to False.

        Kwargs:
            start (int): The frame to start rendering at.
                Default: Comp's render start settings.
            end (int): The frame to stop rendering at.
                Default: Comp's render end settings.
            high_quality (bool): Render in High Quality (HiQ).
                Default True.
            render_all (bool): Render all tools, even if not required by a
                saver. Default False.
            motion_blur (bool): Do motion blur in render, where specified in
                tools. Default true.
            size_type (int): Resize the output:
                                -1. Custom (only used by PreviewSavers during
                                            preview render)
                                 0. Use prefs setting
                                 1. Full Size (default)
                                 2. Half Size
                                 3. Third Size
                                 4. Quarter Size
            width (int): Width of result when doing a Custom preview
                (defaults to pref)
            height (int): Height of result when doing a Custom preview
                (defaults to pref)
            keep_aspect (bool): Maintains the frame aspect when doing a Custom
                preview. Defaults to Preview prefs setting.
            step_render (bool): Render only 1 out of every X frames ("shoot on
                X frames") or render every frame. Defaults to False.
            steps (int): If step rendering, how many to step. Default 5.
            use_network (bool): Enables rendering with the network.
                Defaults to False.
            groups (str): Use these network slave groups to render on (when
                net rendering). Default "all".
            flags (number): Number specifying render flags, usually 0
                (the default). Most flags are specified by other means, but a
                value of 262144 is used for preview renders.
            tool (Tool): A tool to render up to. If this is specified only
                sections of the comp up to this tool will be rendered. eg you
                could specify comp.Saver1 to only render *up to* Saver1,
                ignoring any tools (including savers) after it.
            frame_range (str): Describes which frames to render.
                (eg "1..100,150..180"). Defaults to "Start".."End"

        Returns:
            True if the composition rendered successfully, None if it failed
            to start or complete.

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

        Returns:
             bool: Whether comp is currently being played.
        """
        return self._reference.IsPlaying()

    def is_locked(self):
        """ Returns True if the comp is locked.

        Use this method to see whether a composition is locked or not.

        Returns:
             bool: Whether comp is currently locked.
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
        flow = self.comp().current_frame().FlowView
        # possible optimization: self._reference.Comp.CurrentFrame.FlowView
        return flow.GetPosTable(self._reference).values()

    def set_pos(self, pos):
        """ Reposition this tool.

        :param pos: Numeric values specifying the x and y co-ordinates for the tool in the FlowView.
        :type pos: list(float, float)
        """
        flow = self.comp().current_frame().FlowView
        # possible optimization: self._reference.Comp.CurrentFrame.FlowView
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

    def connections_iter(self, inputs=True, outputs=True):
        """ Yield each Input and Output connection for this Tool instance.

        Each individual connection is yielded in the format: `(Output, Input)`

        :param inputs: If True include the inputs of this Tool, else they are excluded.
        :param outputs: If True include the outputs of this Tool, else they are excluded.
        :yield: (Output, Input) representing a connection to or from this Tool.
        """
        if inputs:
            for input in self.inputs():
                connected_output = input.get_connected_output()
                if connected_output:
                    yield (connected_output, input)

        if outputs:
            for output in self.outputs():
                connected_inputs = output.get_connected_inputs()
                if connected_inputs:
                    for connected_input in connected_inputs:
                        yield (output, connected_input)

    def connections(self, inputs=True, outputs=True):
        """Return all Input and Output connections of this Tools.

        Each individual connection is a 2-tuple in the list in the format:
            `(Output, Input)`

        For example:
            `[(Output, Input), (Output, Input), (Output, Input)]`

        Args:
            inputs (bool): If True include the inputs of this Tool, else they
                are excluded.
            outputs (bool): If True include the outputs of this Tool, else they
                are excluded.

        Returns:
            A list of 2-tuples (Output, Input) representing each connection to
            or from this Tool.
        """
        return list(self.connections_iter(inputs=inputs, outputs=outputs))
    # endregion

    def rename(self, name):
        """Sets the name for this Tool to `name`.

        Args:
            name (str): The new name to change to.

        """
        self._reference.SetAttrs({'TOOLB_NameSet': True, 'TOOLS_Name': name})

    def clear_name(self):
        """Clears user-defined name reverting to automated internal name."""
        self._reference.SetAttrs({'TOOLB_NameSet': False, 'TOOLS_Name': ''})

    def delete(self):
        """Removes the tool from the composition.

        .. note::
            This also releases the handle to the Fusion Tool object, setting it to nil.
            This directly invalidates this Tool instance.

        """
        self._reference.Delete()

    def refresh(self):
        """Refreshes the tool, showing updated user controls.

        .. note::
            Internally calling Refresh in Fusion will invalidate the handle to
            internal object this tool references. You'd have to save the new
            handle that is returned (even though the documentation says nothing
            is returned). Calling this function on this Tool will invalidate
            other Tool instances referencing this same object. But it will
            update the reference in this instance on which the function call
            is made.

        """
        new_ref = self._reference.Refresh()
        self._reference = new_ref

    def parent(self):
        """Return the parent Group this Tool belongs to, if any."""
        return self._reference.ParentTool

    def save_settings(self, path=None):
        """Saves the tool's settings to a dict, or to a .setting file
        specified by the path argument.

        :param path: A valid path to the location where a .setting file will be saved.
        :type path: str
        :return:
            If a path is given, the tool's settings will be saved to that file,
            and a boolean is returned to indicate success.
            If no path is given, SaveSettings() will return a table of the
            tool's settings instead.

        """
        args = tuple() if path is None else (path,)
        return self._reference.SaveSettings(*args)

    def load_settings(self, settings):
        """Loads .setting files or settings dict into the tool.

        This is potentially useful for any number of applications, such as
        loading curve data into fusion, for which there is currently no simple
        way to script interactively in Fusion. Beyond that, it could possibly
        be used to sync updates to tools over project management systems.

        Args:
            settings (str, dict): The path to a valid .setting file or a
            settings dict. A valid dict of settings, such as produced by
            SaveSettings() or read from a .setting file.

        Returns:
            None

        """
        self._reference.LoadSettings(settings)

    def comp(self):
        """ Return the Comp this Tool associated with. """
        return Comp(self._reference.Composition)

    def get_text_color(self):
        """ Gets the Tool's text color.

        :rtype: dict
        :return: The Tool's current text color.
        """
        return self._reference.TextColor

    def set_text_color(self, color):
        """ Sets the Tool's text color.

        Color should be assigned as a dictionary holding the RGB values between 0-1, like:
            {"R": 1, "G": 0, "B": 0}

        Example
            >>> tool.set_text_color({'R':0.5, 'G':0.1, 'B': 0.0})
            >>> tool.set_text_color(None)
        """
        self._reference.TextColor = color

    def get_tile_color(self):
        """ Gets the Tool's tile color.

        :rtype: dict
        :return: The Tool's current tile color.
        """
        return self._reference.TileColor

    def set_tile_color(self, color):
        """ Sets the Tool's tile color.

        Example
            >>> tool.set_tile_color({'R':0.5, 'G':0.1, 'B': 0.0})
            >>> tool.set_tile_color(None)   # reset
        """
        self._reference.TileColor = color

    def get_keyframes(self):
        """ Return a list of keyframe times, in order, for the tool only.

        These are NOT the keyframes on Inputs of this tool!
        Any animation splines or modifiers attached to the tool's inputs are not considered.

        .. note::
            Most Tools will return only the start and end of their valid region.
            Certain types of tools and modifiers such as BezierSplines may return a longer list of keyframes.

        :return: List of int values indicating frames.
        :rtype: list
        """
        keyframes = self._reference.GetKeyFrames()
        if keyframes:
            return keyframes.values()
        else:
            return None

    def __eq__(self, other):
        if isinstance(other, Tool):
            self.name() == other.name()
        return False

    def __hash__(self):
        return hash(self.name())


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


class Input(Link):
    """An Input is any attribute that can be set or connected to by the user
    on the incoming side of a tool.

    .. note::
        These are the input knobs in the Flow view, but also the input values
        inside the Control view for a Tool.

    Because of the way node-graphs work any value that goes into a Tool
    required to process the information should result (in most scenarios) in a
    reproducible output under the same conditions.

    """

    def __current_time(self):
        # optimize over going through PyNodes (??)
        # instead of: time = self.tool().comp().get_current_time()
        return self._reference.GetTool().Composition.CurrentTime

    def get_value(self, time=None):
        """Get the value of this Input at the given time.

        Arguments:
            time (float): The time to set the value at. If None provided the
                current time is used.

        Returns:
            A value directly from the internal input object.

        """
        if time is None:
            time = self.__current_time()

        return self._reference[time]

    def set_value(self, value, time=None):
        """Set the value of the input at the given time.

        Arguments:
            time (float): The time to set the value at. If None provided the
                currentt time is used.

        """

        if time is None:
            time = self.__current_time()

        attrs = self.get_attrs()
        data_type = attrs['INPS_DataType']

        # Setting boolean values doesn't work. So instead set an integer value
        # allow settings checkboxes with True/False
        if isinstance(value, bool):
            value = int(value)

        # Convert float/integer to enum if datatype == "FuID"
        elif isinstance(value, (int, float)) and data_type == "FuID":

            # We must compare it with a float value. We add 1 to interpret
            # as zero based indices. (Zero would be 1.0 in the fusion id
            # dictionary, etc.)
            v = float(value) + 1.0

            enum_keys = ("INPIDT_MultiButtonControl_ID",
                         "INPIDT_ComboControl_ID")
            for enum_key in enum_keys:
                if enum_key in attrs:
                    enum = attrs[enum_key]
                    if v in enum:
                        value = enum[v]
                        break

        # Convert enum string value to its corresponding integer value
        elif (isinstance(value, basestring) and
                data_type != "Text" and
                data_type != "FuID"):

            enum_keys = ("INPST_MultiButtonControl_String",
                         "INPIDT_MultiButtonControl_ID",
                         "INPIDT_ComboControl_ID")
            for enum_key in enum_keys:
                if enum_key in attrs:
                    enum = dict((str(key), value) for value, key in
                                attrs[enum_key].items())
                    if value in enum:
                        value = enum[str(value)] - 1.0
                        break

        self._reference[time] = value

    def connect_to(self, output):
        """Connect an Output as incoming connection to this Input.

        .. note::
            This function behaves similarly to right clicking on a property,
            selecting Connect To, and selecting the property you wish to
            connect the input to. In that respect, if you try to connect
            non-similar data types (a path's value to a polygon's level, for
            instance) it will not connect the values. Such an action will
            yield NO error message.

        Args:
            output (Output): The output that should act as incoming connection.

        Returns:
            None

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
        """Disconnect the Output this Input is connected to, if any."""
        self.connect_to(None)

    def get_connected_output(self):
        """ Returns the output that is connected to a given input.

        Returns:
            Output: The Output this Input is connected to if any, else None.

        """
        other = self._reference.GetConnectedOutput()
        if other:
            return Output(other)

    def get_expression(self):
        """Return the expression string shown in the Input's Expression field.

        Returns:
            str: the simple expression string from a given input if any else
                an empty string is returned.

        """
        return self._reference.GetExpression()

    def set_expression(self, expression):
        """Set the Expression field for the Input to the given string.

        Args:
            expression (str): An expression string.

        """
        self._reference.SetExpression(expression)

    def get_keyframes(self):
        """Return the times at which this Input has keys.

        Returns:
            list: List of int values indicating frames.
        """
        keyframes = self._reference.GetKeyFrames()
        if keyframes:
            return keyframes.values()
        else:
            return None

    def remove_keyframes(self, time=None, index=None):
        """Remove the keyframes on this Input (if any)

        """
        # TODO: Implement Input.remove_keyframes()
        raise NotImplementedError()

    def is_connected(self):
        """Return whether the Input is an incoming connection from an Output

        Returns:
             bool: True if connected, otherwise False

        """
        return bool(self._reference.GetConnectedOutput())

    def data_type(self):
        """Returns the type of Parameter

        For example the (Number, Point, Text, Image) types this Input accepts.

        Returns:
            str: Type of parameter.

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
    """ An Image parameter object.

    For example the Image output from a Tool.
    """
    def width(self):
        """ Return the width in pixels for the current output, this could be for the current proxy resolution.
        :return: Actual horizontal size, in pixels
        """
        return self._reference.Width

    def height(self):
        """ Return the height in pixels for the current output, this could be for the current proxy resolution.
        :return: Actual horizontal size, in pixels
        """
        return self._reference.Height

    def original_width(self):
        """
        :return: Unproxied horizontal size, in pixels.
        """
        return self._reference.OriginalWidth

    def original_height(self):
        """
        :return: Unproxied vertical size, in pixels.
        """
        return self._reference.OriginalHeight

    def depth(self):
        """ Image depth indicator (not in bits)
        :return: Image depth
        """
        return self._reference.Depth

    def x_scale(self):
        """
        :return: Pixel X Aspect
        """
        return self._reference.XScale

    def y_scale(self):
        """
        :return: Pixel Y Aspect
        """
        return self._reference.YScale

    def x_offset(self):
        """
        :return: X Offset, in pixels
        """
        return self._reference.XOffset

    def y_offset(self):
        """
        :return: Y Offset, in pixels
        """
        return self._reference.YOffset

    def field(self):
        """
        :return: Field indicator
        """
        return self._reference.Field

    def proxy_scale(self):
        """
        :return: Image proxy scale multiplier.
        """
        return self._reference.ProxyScale


class TransformMatrix(Parameter):
    pass


class Fusion(PyObject):
    """The Fusion application.

    Contains all functionality to interact with the global Fusion sessions.
    For example this would allow you to retrieve the available compositions
    that are currently open or open a new one.
    """
    # TODO: Implement Fusion methods: http://www.steakunderwater.com/VFXPedia/96.0.243.189/index5522.html?title=Eyeon:Script/Reference/Applications/Fusion/Classes/Fusion

    @staticmethod
    def _default_reference():
        """Fallback for the default reference"""

        # this would be accessible within Fusion as "fusion"
        return getattr(sys.modules["__main__"], "fusion", None)

    def new_comp(self):
        """Creates a new composition and sets it as the currently active one"""
        # TODO: Need fix: During NewComp() Fusion seems to be temporarily unavailable
        self._reference.NewComp()
        comp = self._reference.GetCurrentComp()
        return Comp(comp)

    def get_current_comp(self):
        """Return the currently active comp in this Fusion instance"""
        comp = self._reference.GetCurrentComp()
        return Comp(comp)

    @property
    def build(self):
        """Returns the build number of the current Fusion instance.

        Returns:
            float: Build number

        """
        return self._reference.Build

    @property
    def version(self):
        """Returns the version of the current Fusion instance.

        Returns:
            float: Version number

        """
        return self._reference.Version

    def __repr__(self):
        return '{0}("{1}")'.format(self.__class__.__name__,
                                   str(self._reference))


class Registry(PyObject):
    """ Represents a type of object within Fusion """
    pass

import fusionscript.core


class GLView(fusionscript.core.PyObject):
    """ The view object has methods that deal with general properties of the view,

    like enabling the sub views or switching between the A & B buffers.

    Each ChildFrame (i.e. composition window) has at least a left and a right view, represented by GLView objects.
    To reach one of these, use something like this:

    >>> # .Left will return the left preview object, the GLView object can be reached via .View
    >>> comp:GetPreviewList().Left.View

    Or this:

    >>> comp.CurrentFrame.LeftView
    """
    # TODO: Implement `GLView`
    # Reference: http://www.steakunderwater.com/VFXPedia/96.0.243.189/index74ef.html?title=Eyeon:Script/Reference/Applications/Fusion/Classes/GLView
    def current_viewer(self):
        self.CurrentViewer


class GLViewer(fusionscript.core.PyObject):
    """
    Each buffer can in turn contain a viewer, represented by either GLViewer or GLImageViewer objects.
    Use a view's :GetViewerList() method or .CurrentViewer to reach these objects.

    They provides further methods specific to a single display buffer like showing guides, enabling LUTs or switching
    color channels:

    For example, to switch to A buffer and show the red channel:
    >>> left = comp.CurrentFrame.LeftView
    >>> left.SetBuffer(0) # switch to A buffer
    >>> viewer = left.CurrentViewer
    >>> if viewer is not None:
    >>>    viewer.SetChannel(0) # switch to red channel
    >>>    viewer.Redraw()

    This is a parent class for 2D and 3D viewers. 2D image viewers are instances of the GLImageViewer subclass and have
    additional methods to set and show the DoD, RoI or LUT.

    """
    pass
    # TODO: Implement `GLViewer`
    # Reference: http://www.steakunderwater.com/VFXPedia/96.0.243.189/indexc3e5.html?title=Eyeon:Script/Reference/Applications/Fusion/Classes/GLViewer


class GLImageViewer(GLViewer):
    """ The GLImageViewer is the subclass of GLViewer that is used for 2D views.

    The GLImageViewer has additional methods for the 2D to set and show the DoD, RoI or LUT.
    """
    pass
    # TODO: Implement `GLImageViewer`
    # Reference: http://www.steakunderwater.com/VFXPedia/96.0.243.189/index1cee.html?title=Eyeon:Script/Reference/Applications/Fusion/Classes/GLImageViewer
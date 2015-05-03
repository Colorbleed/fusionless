""" A set of Context managers to provide a simple and safe way to manage Fusion's context.

    Example
        >>> with LockComp():
        >>>     print "Everything in here is done while the composition is locked."

"""


class LockComp(object):
    def __init__(self, undoQueueName="Script CMD"):
        # Lock flow
        comp.Lock()

    def __enter__(self):
        return None

    def __exit__(self, type, value, traceback):
        comp.Unlock()


class UndoChunk(object):
    def __init__(self, undoQueueName="Script CMD"):
        self._name = undoQueueName

    def __enter__(self):
        comp.StartUndo(self._name)

    def __exit__(self, type, value, traceback):
        comp.EndUndo(True)


class LockAndUndoChunk(object):
    def __init__(self, undoQueueName="Script CMD"):
        self._name = undoQueueName

    def __enter__(self):
        comp.Lock()
        comp.StartUndo(self._name)

    def __exit__(self, type, value, traceback):
        comp.EndUndo(True)
        comp.Unlock()

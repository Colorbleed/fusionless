""" A set of Context managers to provide a simple and safe way to manage Fusion's context. """


class LockComp(object):
    def __init__(self, undoQueueName="Script CMD"):
        # Lock flow
        comp.Lock()
        # Start undo event
        comp.StartUndo(undoQueueName)

    def __enter__(self):
        return None

    def __exit__(self, type, value, traceback):
        comp.EndUndo(True)
        comp.Unlock()


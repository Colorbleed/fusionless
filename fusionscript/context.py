""" A set of Context managers to provide a simple and safe way to manage Fusion's context.

    Example
        >>> with lock_comp():
        >>>     print "Everything in here is done while the composition is locked."

"""

import contextlib

@contextlib.contextmanager
def lock_comp(comp):
    comp.lock()
    try:
        yield
    finally:
        comp.unlock()

@contextlib.contextmanager
def undo_chunk(comp, undoQueueName="Script CMD"):
    comp.start_undo(undoQueueName)
    try:
        yield
    finally:
        comp.end_undo()


@contextlib.contextmanager
def lock_and_undo_chunk(comp, undoQueueName="Script CMD"):
    with lock_comp(comp):
        with undo_chunk(comp, undoQueueName):
            yield
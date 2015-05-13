**********
What's New
**********

==================================
Version 0.1.1
==================================

----------------------------------
Additions
----------------------------------
- core: Added extra methods to PyObject and updated its TODO to reflect those still needing to added.
- core: Added `name` parameter to Comp.create_tool() to easily allow direct naming of the tool.
- core: Implemented Comp, Flow, Tool, Input, Output classes

----------------------------------
Changes
----------------------------------
- core: Refactored PyNode to PyObject class
- core: Refactored Attribute to Link class (to be closer to Fusion's internal naming)
- core: Refactored Comp.create_node() to Comp.create_tool()

==================================
Version 0.1.0
==================================

----------------------------------
Additions
----------------------------------
- core: Implemented PyNode base class
- core: Implemented Comp, Flow, Tool, Input, Output classes
- context: Implemented LockComp, UndoChunk and LockAndUndoChunk context managers.
import unittest
import fusionscript as fu


class TestTools(unittest.TestCase):
    def test_rename(self):
        c = fu.Comp()

        tool = c.create_tool("Background")
        original_name = tool.name()

        tool.rename("foobar_macaroni")
        new_name = tool.name()

        tool.clear_name()
        cleared_name = tool.name()

        self.assertNotEqual(original_name, new_name)
        self.assertEqual(new_name, "foobar_macaroni")
        self.assertEqual(cleared_name, original_name)   # not sure if this is 'always expected behaviour' to be equal

        tool.delete()
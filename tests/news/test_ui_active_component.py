import unittest
from bvb_finance.news import UIActiveComponent

class TestUIActiveComponent(unittest.TestCase):
    def test_active_component(self):
        test_component_name = "TEST_COMPONENT"
        UIActiveComponent.register_components(test_component_name, 10)
        updated_values = [None] * 10
        updated_values[8] = 20
        active_component: UIActiveComponent.ActiveComponent =\
              UIActiveComponent.update_components(test_component_name, updated_values)
        self.assertTrue(active_component is not None)
        self.assertEqual(8, active_component.index)


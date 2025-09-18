from pathlib import Path

import unittest

from omf.tools.message_template_manager import get_message_template_manager

class TestMessageTemplateManagerSingleton(unittest.TestCase):
    def test_singleton_behavior(self):
        # Reset singleton
        import omf.tools.message_template_manager as message_template_manager

        message_template_manager._message_template_manager = None
        manager1 = get_message_template_manager()
        self.assertIsNotNone(manager1)
        manager2 = get_message_template_manager()
        self.assertIs(manager1, manager2)

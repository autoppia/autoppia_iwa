import unittest

from autoppia_iwa.src.data_generation.domain.tests_classes import BaseTaskTest, CheckEventTest, CheckPageViewEventTest, FindInHtmlTest, JudgeBaseOnHTML, JudgeBaseOnScreenshot


class TestAssignTests(unittest.TestCase):
    def test_assign_tests_valid_configs(self):
        """
        Test that `assign_tests` correctly instantiates the appropriate test classes
        based on valid configurations.
        """
        test_configs = [
            {"test_type": "frontend", "keywords": ["example"]},
            {"test_type": "frontend", "name": "JudgeBaseOnHTML"},
            {"test_type": "frontend", "name": "JudgeBaseOnScreenshot", "task": "example task"},
            {"test_type": "backend", "page_view_url": "https://example.com"},
            {"test_type": "backend", "event_name": "test_event"},
        ]

        assigned_tests = BaseTaskTest.assign_tests(test_configs)

        # Assert that the correct number of tests is assigned
        self.assertEqual(len(assigned_tests), 5, "Incorrect number of tests assigned")

        # Assert each test is the correct class type
        self.assertIsInstance(assigned_tests[0], FindInHtmlTest, "Test 1 is not FindInHtmlTest")
        self.assertIsInstance(assigned_tests[1], JudgeBaseOnHTML, "Test 2 is not JudgeBaseOnHTML")
        self.assertIsInstance(assigned_tests[2], JudgeBaseOnScreenshot, "Test 3 is not JudgeBaseOnScreenshot")
        self.assertIsInstance(assigned_tests[3], CheckPageViewEventTest, "Test 4 is not CheckPageViewEventTest")
        self.assertIsInstance(assigned_tests[4], CheckEventTest, "Test 5 is not CheckEventTest")

    def test_assign_tests_invalid_config(self):
        """
        Test that `assign_tests` raises a ValueError for unsupported configurations.
        """
        invalid_config = [{"test_type": "unknown", "name": "InvalidTest"}]

        with self.assertRaises(ValueError, msg="assign_tests did not raise ValueError for invalid config"):
            BaseTaskTest.assign_tests(invalid_config)


if __name__ == "__main__":
    unittest.main()

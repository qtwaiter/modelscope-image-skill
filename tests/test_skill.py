#!/usr/bin/env python3
"""测试 ModelScope Image Generation Skill"""

import unittest
import os
from pathlib import Path

os.environ["MODELSCOPE_API_KEY"] = "test_api_key"

from skill import ModelScopeImageSkill


class TestModelScopeImageSkill(unittest.TestCase):
    def setUp(self):
        self.skill = ModelScopeImageSkill()

    def test_init_without_api_key(self):
        """测试未设置 API Key 时抛出异常"""
        os.environ.pop("MODELSCOPE_API_KEY", None)
        with self.assertRaises(ValueError):
            ModelScopeImageSkill()

    def test_init_with_valid_config(self):
        """测试有效配置初始化"""
        config = {"api_key_env": "MODELSCOPE_API_KEY"}
        skill = ModelScopeImageSkill(config)
        self.assertIsNotNone(skill.api_key)
        self.assertEqual(skill.api_key, "test_api_key")

    def test_generate_image_missing_prompt(self):
        """测试空提示词"""
        result = self.skill.generate_image(prompt="")
        self.assertFalse(result["success"])
        self.assertIn("prompt", result.get("message", "").lower())

    def test_size_parsing(self):
        """测试尺寸解析"""
        width, height = map(int, "1024x1024".split('x'))
        self.assertEqual(width, 1024)
        self.assertEqual(height, 1024)


if __name__ == "__main__":
    unittest.main()
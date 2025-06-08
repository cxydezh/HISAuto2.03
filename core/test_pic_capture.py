"""
图像采集模块的测试文件
"""

import os
import tempfile
import unittest
from core.pic_capture import PicCapture

class TestPicCapture(unittest.TestCase):
    def setUp(self):
        """测试前的准备工作"""
        # 创建临时目录用于保存测试图像
        self.temp_dir = tempfile.mkdtemp()
        self.pic_capture = PicCapture(self.temp_dir)
        
    def test_capture_and_save(self):
        """测试图像捕获和保存功能"""
        # 捕获屏幕
        self.pic_capture.capture_screen()
        
        # 模拟用户选择区域
        self.pic_capture.start_x = 100
        self.pic_capture.start_y = 100
        self.pic_capture.end_x = 200
        self.pic_capture.end_y = 200
        
        # 保存图像
        success = self.pic_capture.save_image("test_image")
        self.assertTrue(success)
        
        # 验证图像文件是否存在
        image_path = os.path.join(self.temp_dir, "test_image.png")
        self.assertTrue(os.path.exists(image_path))
        
    def test_duplicate_filename(self):
        """测试重复文件名处理"""
        # 创建第一个图像
        self.pic_capture.start_x = 100
        self.pic_capture.start_y = 100
        self.pic_capture.end_x = 200
        self.pic_capture.end_y = 200
        self.pic_capture.save_image("test_image")
        
        # 尝试使用相同的文件名保存
        success = self.pic_capture.save_image("test_image")
        self.assertFalse(success)
        
    def test_get_coordinates(self):
        """测试获取坐标功能"""
        # 设置坐标
        self.pic_capture.start_x = 100
        self.pic_capture.start_y = 100
        self.pic_capture.end_x = 200
        self.pic_capture.end_y = 200
        
        # 获取坐标
        coords = self.pic_capture.get_image_coordinates()
        self.assertEqual(coords, (100, 100, 200, 200))
        
    def tearDown(self):
        """测试后的清理工作"""
        # 删除临时目录及其内容
        import shutil
        shutil.rmtree(self.temp_dir)

if __name__ == '__main__':
    unittest.main() 
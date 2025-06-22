import unittest
from unittest.mock import patch, MagicMock
import types
import utils.action_recorder_fixed as arf
from mouse._mouse_event import ButtonEvent

class DummyEvent:
    def __init__(self, button='left', event_type='down', time=0):
        self.button = button
        self.event_type = event_type
        self.time = time

class DummyMainWindow:
    def __init__(self):
        self.window = MagicMock()

class TestActionRecorderFixed(unittest.TestCase):
    def setUp(self):
        self.home_tab = MagicMock()
        self.home_tab.action_group_id = 1
        self.main_window = DummyMainWindow()
        self.recorder = arf.ActionRecorder(self.home_tab, main_window=self.main_window)
        self.recorder._get_session = MagicMock(return_value=MagicMock())
        self.recorder._monitor_end_key = MagicMock()
        self.recorder.recording = True
        # 只放事件字典
        self.recorder.recorded_events = [
            {'type': 'mouse', 'action_code': 1, 'x': 100, 'y': 200, 'mouse_size': 1, 'time_diff': 0, 'timestamp': None},
            {'type': 'mouse', 'action_code': 2, 'x': 101, 'y': 201, 'mouse_size': 1, 'time_diff': 0, 'timestamp': None},
        ]
        self.recorder.last_event_time = 0
        self.recorder.icon_window = MagicMock()
        self.recorder.session = MagicMock()
        self.recorder.session.rollback = MagicMock()
        arf.tk_safe_queue.queue.clear()

    @patch('utils.action_recorder_fixed.mouse.hook')
    @patch('utils.action_recorder_fixed.keyboard.on_press')
    @patch('utils.action_recorder_fixed.keyboard.on_release')
    @patch('utils.action_recorder_fixed.mouse.get_position', return_value=(100, 200))
    def test_mouse_event_handler(self, mock_get_pos, mock_k_release, mock_k_press, mock_hook):
        self.recorder.record_mode = "全部"
        self.recorder._monitor_end_key = MagicMock()
        self.recorder._get_session = MagicMock(return_value=MagicMock())
        self.recorder.session = MagicMock()
        # 执行
        self.recorder._start_event_recording('Esc')
        # 测试_mouse_event_handler分发
        event_down = ButtonEvent(event_type='down', button='left', time=0)
        event_up = ButtonEvent(event_type='up', button='left', time=0)
        self.recorder._mouse_event_handler(event_down)
        self.recorder._mouse_event_handler(event_up)
        print('DEBUG recorded_events:', self.recorder.recorded_events)
        # 检查事件被记录
        self.assertTrue(len(self.recorder.recorded_events) >= 2)
        for e in self.recorder.recorded_events:
            self.assertIn('type', e)
            self.assertIn('action_code', e)
            self.assertIn('x', e)
            self.assertIn('y', e)

    @patch('tkinter.messagebox.showinfo')
    def test_stop_recording_messagebox_async(self, mock_showinfo):
        self.recorder.stop_recording()
        # 队列应有弹窗操作
        found = False
        for func in list(arf.tk_safe_queue.queue):
            if hasattr(func, '__call__'):
                func()
                found = True
        self.assertTrue(found)
        mock_showinfo.assert_called_with("录制完成", f"录制已完成，共记录 {len(self.recorder.recorded_events)} 个事件", parent=self.main_window.window)

    def test_stop_recording_deiconify_async(self):
        # mock deiconify
        self.main_window.window.deiconify = MagicMock()
        self.recorder.stop_recording()
        # 执行队列
        for func in list(arf.tk_safe_queue.queue):
            if hasattr(func, '__call__'):
                func()
        self.main_window.window.deiconify.assert_called_once()

if __name__ == '__main__':
    unittest.main() 
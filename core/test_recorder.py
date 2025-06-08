import unittest
from unittest.mock import Mock, patch

from pytest import Session
from core.recorder import ActionRecorder
from models.actions import ActionMouse, ActionKeyboard, ActionPrintscreen, ActionAI

class TestActionRecorder(unittest.TestCase):
    def setUp(self):
        self.recorder = ActionRecorder()
        self.recorder.session = Mock(spec=Session)
        self.recorder.current_action_list = []
        self.action_list_id = 1

    @patch('core.recorder.ActionMouse')
    def test_save_mouse_action(self, mock_action_mouse):
        self.recorder.current_action_list = [{
            "type": "mouse",
            "data": {
                "mouse_action": "click",
                "x": 100,
                "y": 200,
                "time_diff": 0.5
            }
        }]

        result = self.recorder.save_to_database(self.action_list_id)
        
        self.assertTrue(result)
        mock_action_mouse.assert_called_once_with(
            mouse_action="click",
            x=100,
            y=200,
            time_diff=0.5,
            action_list_id=self.action_list_id
        )
        self.recorder.session.add.assert_called_once()
        self.recorder.session.commit.assert_called_once()

    @patch('core.recorder.ActionKeyboard')
    def test_save_keyboard_action(self, mock_action_keyboard):
        self.recorder.current_action_list = [{
            "type": "keyboard",
            "data": {
                "keyboard_type": "press",
                "keyboard_value": "a",
                "time_diff": 0.3
            }
        }]

        result = self.recorder.save_to_database(self.action_list_id)
        
        self.assertTrue(result)
        mock_action_keyboard.assert_called_once_with(
            keyboard_type="press",
            keyboard_value="a",
            time_diff=0.3,
            action_list_id=self.action_list_id
        )
        self.recorder.session.add.assert_called_once()
        self.recorder.session.commit.assert_called_once()

    @patch('core.recorder.ActionPrintscreen')
    def test_save_printscreen_action(self, mock_action_printscreen):
        self.recorder.current_action_list = [{
            "type": "printscreen",
            "data": {
                "lux": 10,
                "luy": 20,
                "rdx": 30,
                "rdy": 40,
                "pic_name": "test.png",
                "match_picture": True,
                "match_text": False,
                "time_diff": 0.7
            }
        }]

        result = self.recorder.save_to_database(self.action_list_id)
        
        self.assertTrue(result)
        mock_action_printscreen.assert_called_once_with(
            lux=10,
            luy=20,
            rdx=30,
            rdy=40,
            pic_name="test.png",
            match_picture=True,
            match_text=False,
            time_diff=0.7,
            action_list_id=self.action_list_id
        )
        self.recorder.session.add.assert_called_once()
        self.recorder.session.commit.assert_called_once()

    @patch('core.recorder.ActionAI')
    def test_save_ai_action(self, mock_action_ai):
        self.recorder.current_action_list = [{
            "type": "ai",
            "data": {
                "train_group": "group1",
                "train_name": "model1",
                "long_text": "test text",
                "illustration": "illustration text",
                "time_diff": 1.2
            }
        }]

        result = self.recorder.save_to_database(self.action_list_id)
        
        self.assertTrue(result)
        mock_action_ai.assert_called_once_with(
            train_group="group1",
            train_name="model1",
            long_text="test text",
            illustration="illustration text",
            time_diff=1.2,
            action_list_id=self.action_list_id
        )
        self.recorder.session.add.assert_called_once()
        self.recorder.session.commit.assert_called_once()

    def test_database_commit_failure(self):
        self.recorder.current_action_list = [{
            "type": "mouse",
            "data": {
                "mouse_action": "click",
                "x": 100,
                "y": 200,
                "time_diff": 0.5
            }
        }]
        
        self.recorder.session.commit.side_effect = Exception("Database error")
        
        result = self.recorder.save_to_database(self.action_list_id)
        
        self.assertFalse(result)
        self.recorder.session.rollback.assert_called_once()
        self.recorder.session.commit.assert_called_once()

if __name__ == '__main__':
    unittest.main()
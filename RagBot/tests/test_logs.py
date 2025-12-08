import unittest
from unittest.mock import patch, MagicMock
import logging
from datetime import datetime

# Import the functions to be tested
from src.logs import get_logger, non_generative_agent_logger, simple_logger, logger_no_session_id

class TestLogs(unittest.TestCase):

    @patch('src.logs.logging.FileHandler')
    @patch('src.logs.JsonFormatter')
    def test_get_logger_creation(self, mock_json_formatter, mock_file_handler):
        """Test that get_logger creates and configures a new logger correctly."""
        # Reset handlers for a clean test
        logging.getLogger("HamBot").handlers = []

        mock_handler_instance = MagicMock()
        mock_file_handler.return_value = mock_handler_instance
        mock_formatter_instance = MagicMock()
        mock_json_formatter.return_value = mock_formatter_instance

        logger = get_logger()

        self.assertEqual(logger.name, "HamBot")
        self.assertEqual(logger.level, logging.INFO)
        self.assertFalse(logger.propagate)
        mock_file_handler.assert_called_with("/var/log/HamBot.log", encoding="utf8")
        mock_handler_instance.setFormatter.assert_called_with(mock_formatter_instance)
        self.assertIn(mock_handler_instance, logger.handlers)

    def test_get_logger_existing(self):
        """Test that get_logger returns the existing logger if already configured."""
        # Reset handlers to ensure a clean state before the test
        existing_logger = logging.getLogger("HamBot")
        existing_logger.handlers = []

        # First call to create the logger
        with patch('src.logs.logging.FileHandler'), patch('src.logs.JsonFormatter'):
            logger1 = get_logger()

        # Second call should return the same instance without re-configuring
        with patch('src.logs.logging.FileHandler') as mock_file_handler:
            logger2 = get_logger()
            self.assertIs(logger1, logger2)
            mock_file_handler.assert_not_called() # Should not create a new handler

    @patch('src.logs.get_logger')
    def test_non_generative_agent_logger(self, mock_get_logger):
        """Test the non_generative_agent_logger function."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        session_id = "session123"
        tenant_name = "tenant_test"
        user_code = "user001"
        agent = "test_agent"
        message = "Test agent message"
        input_dict = {"input": "test"}
        output_dict = {"output": "result"}
        elapsed_time = 1.23

        non_generative_agent_logger(session_id, tenant_name, user_code, agent, message, input_dict, output_dict, elapsed_time)

        mock_logger.info.assert_called_once()
        args, kwargs = mock_logger.info.call_args
        self.assertEqual(args[0], message)
        extra = kwargs['extra']
        self.assertEqual(extra['session_id'], session_id)
        self.assertEqual(extra['tenant_name'], tenant_name)
        self.assertEqual(extra['user_code'], user_code)
        self.assertEqual(extra['agent'], agent)
        self.assertEqual(extra['input'], input_dict)
        self.assertEqual(extra['return'], output_dict)
        self.assertAlmostEqual(extra['elapsed_time_in_seconds'], elapsed_time)
        self.assertTrue('logtime' in extra)

    @patch('src.logs.get_logger')
    def test_simple_logger(self, mock_get_logger):
        """Test the simple_logger function."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        message = "Simple test message"
        session_id = "session456"

        simple_logger(message, session_id)

        mock_logger.log.assert_called_once()
        args, kwargs = mock_logger.log.call_args
        self.assertEqual(args[0], logging.INFO)
        self.assertEqual(args[1], message)
        extra = kwargs['extra']
        self.assertEqual(extra['session_id'], session_id)
        self.assertTrue('logtime' in extra)

    @patch('src.logs.get_logger')
    def test_logger_no_session_id(self, mock_get_logger):
        """Test the logger_no_session_id function."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        message = "Message without session ID"

        logger_no_session_id(message, log_level=logging.WARNING)

        mock_logger.log.assert_called_once()
        args, kwargs = mock_logger.log.call_args
        self.assertEqual(args[0], logging.WARNING)
        self.assertEqual(args[1], message)
        extra = kwargs['extra']
        self.assertNotIn('session_id', extra)
        self.assertTrue('logtime' in extra)

if __name__ == '__main__':
    unittest.main()

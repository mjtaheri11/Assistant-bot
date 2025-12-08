import unittest
from unittest.mock import patch, AsyncMock
import uuid
import os

from src.orm import Postgres

class TestPostgres(unittest.TestCase):

    def setUp(self):
        """Set up a clean instance of the Postgres class for each test."""
        # Reset the singleton for isolation
        Postgres._instance = None
        self.postgres = Postgres()

    @patch.dict(os.environ, {
        "POSTGRES_DB": "test_db",
        "POSTGRES_ADDR": "localhost",
        "POSTGRES_USER": "test_user",
        "POSTGRES_PASSWORD": "test_password",
        "POSTGRES_PORT": "5432",
    })
    @patch('src.orm.asyncpg.connect', new_callable=AsyncMock)
    async def test_execute_query(self, mock_connect):
        """Test the internal _execute_query method."""
        mock_connection = AsyncMock()
        mock_connect.return_value = mock_connection
        mock_connection.fetchrow.return_value = "fetchrow_result"
        mock_connection.fetch.return_value = "fetch_result"

        # Test fetchrow
        result = await self.postgres._execute_query("SELECT 1", is_insert=True)
        self.assertEqual(result, "fetchrow_result")

        # Test fetch
        result = await self.postgres._execute_query("SELECT ALL", fetch_results=True)
        self.assertEqual(result, "fetch_result")

        # Test execute
        result = await self.postgres._execute_query("INSERT", fetch_results=False, insert_values=("value",))
        self.assertTrue(result)
        mock_connection.execute.assert_called_with("INSERT", "value")

    @patch('src.orm.Postgres._execute_query', new_callable=AsyncMock)
    async def test_create_database(self, mock_execute_query):
        """Test the create_database function."""
        mock_db_id = uuid.uuid4()
        mock_execute_query.return_value = (mock_db_id,)

        # Test with both names
        result = await self.postgres.create_database(company_name="TestCorp", assistant_name="Tester")
        self.assertEqual(result, {"database_id": str(mock_db_id)})
        mock_execute_query.assert_called_with(
            "INSERT INTO public.databases (company_name, assistant_name) VALUES ($1, $2) RETURNING database_id;",
            insert_values=("TestCorp", "Tester"),
            is_insert=True,
            fetch_results=True
        )

        # Test with no names
        await self.postgres.create_database()
        mock_execute_query.assert_called_with(
            "INSERT INTO public.databases DEFAULT VALUES RETURNING database_id;",
            insert_values=None,
            is_insert=True,
            fetch_results=True
        )

    @patch('src.orm.Postgres._execute_query', new_callable=AsyncMock)
    async def test_create_session(self, mock_execute_query):
        """Test the create_session function."""
        mock_session_id = uuid.uuid4()
        mock_execute_query.return_value = (mock_session_id,)

        result = await self.postgres.create_session(database_id="db1", tenant_name="tenant1", user_code="user1")
        self.assertEqual(result, {"session_id": str(mock_session_id)})
        mock_execute_query.assert_called_with(
            "INSERT INTO public.session (database_id, tenant_name, user_code) VALUES ($1, $2, $3) RETURNING session_id;",
            insert_values=("db1", "tenant1", "user1"),
            is_insert=True,
            fetch_results=True
        )

    @patch('src.orm.Postgres._execute_query', new_callable=AsyncMock)
    async def test_get_history(self, mock_execute_query):
        """Test the get_history function."""
        mock_history = [
            ("q1", "p1", "r1", "m1", True, "mod1", 1.1, True, "temp1", "{}"),
            ("q2", "p2", "r2", "m2", False, "mod2", 2.2, False, "temp2", "{}"),
        ]
        mock_execute_query.return_value = mock_history

        history = await self.postgres.get_history("session1", 1, 10, with_paraphrase=True)
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]['query'], 'q1')
        self.assertIn('paraphrased_query', history[0])

        history_no_paraphrase = await self.postgres.get_history("session1", 1, 10, with_paraphrase=False)
        self.assertNotIn('paraphrased_query', history_no_paraphrase[0])

    @patch('src.orm.Postgres._execute_query', new_callable=AsyncMock)
    async def test_insert_chat_row(self, mock_execute_query):
        """Test inserting a new chat row."""
        mock_message_id = uuid.uuid4()
        mock_execute_query.return_value = (mock_message_id,)

        result = await self.postgres.insert_chat_row("session1", "user_query")
        self.assertEqual(result, str(mock_message_id))
        mock_execute_query.assert_called_with(
            "INSERT INTO messages (session_id, user_query) VALUES ($1, $2) RETURNING message_id;",
            is_insert=True,
            insert_values=("session1", "user_query"),
            fetch_results=True
        )

    @patch('src.orm.Postgres._execute_query', new_callable=AsyncMock)
    async def test_update_last_chat_row(self, mock_execute_query):
        """Test updating the last chat row."""
        mock_message_id = uuid.uuid4()
        mock_execute_query.return_value = (mock_message_id,)

        result = await self.postgres.update_last_chat_row(
            "session1", "paraphrased", "response", True, 1.23
        )
        self.assertEqual(result, str(mock_message_id))
        self.assertEqual(mock_execute_query.call_args[1]['insert_values'][0], "paraphrased")

    @patch('src.orm.Postgres._execute_query', new_callable=AsyncMock)
    async def test_set_feedback(self, mock_execute_query):
        """Test setting feedback for a message."""
        mock_execute_query.return_value = (uuid.uuid4(),)

        result = await self.postgres.set_feedback("message1", "positive")
        self.assertTrue(result)
        mock_execute_query.assert_called_with(
            """
            UPDATE messages
            SET feedback = $1
            WHERE message_id = $2 AND feedback IS NULL
            RETURNING message_id;
        """,
            fetch_results=True,
            insert_values=("positive", "message1"),
        )

if __name__ == '__main__':
    unittest.main()

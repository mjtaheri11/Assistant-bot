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

    @patch('src.orm.Postgres._execute_query', new_callable=AsyncMock)
    async def test_exist_session(self, mock_execute_query):
        """Test checking if a session exists."""
        mock_execute_query.return_value = [("some_session_id",)]
        result = await self.postgres.exist_session("some_session_id")
        self.assertTrue(result)

        mock_execute_query.return_value = []
        result = await self.postgres.exist_session("non_existent_session")
        self.assertFalse(result)

    @patch('src.orm.Postgres._execute_query', new_callable=AsyncMock)
    async def test_get_message_fields(self, mock_execute_query):
        """Test retrieving message fields."""
        mock_execute_query.return_value = [("user_q", "paraphrased_q", "bot_r")]
        result = await self.postgres.get_message_fields("session1", "message1")
        self.assertEqual(result, ("user_q", "paraphrased_q", "bot_r"))

    @patch('src.orm.Postgres._execute_query', new_callable=AsyncMock)
    async def test_validate_session(self, mock_execute_query):
        """Test session validation."""
        mock_execute_query.return_value = [(1,)]
        result = await self.postgres.validate_session("session1")
        self.assertTrue(result)

    @patch('src.orm.Postgres._execute_query', new_callable=AsyncMock)
    async def test_find_database_id(self, mock_execute_query):
        """Test finding a database ID from a session ID."""
        mock_db_id = uuid.uuid4()
        mock_execute_query.return_value = (mock_db_id,)
        result = await self.postgres.find_database_id("session1")
        self.assertEqual(result, {"database_id": str(mock_db_id)})

    @patch('src.orm.Postgres._execute_query', new_callable=AsyncMock)
    async def test_find_company_assistant_names(self, mock_execute_query):
        """Test finding company and assistant names."""
        mock_execute_query.return_value = ("TestCorp", "Tester")
        result = await self.postgres.find_company_assistant_names("db1")
        self.assertEqual(result, {"company_name": "TestCorp", "assistant_name": "Tester"})

    @patch('src.orm.Postgres._execute_query', new_callable=AsyncMock)
    async def test_extract_response_type(self, mock_execute_query):
        """Test extracting the response type."""
        mock_execute_query.return_value = [("verbose",)]
        result = await self.postgres.extract_response_type("session1")
        self.assertEqual(result, {"response_type": "verbose"})

    @patch('src.orm.Postgres._execute_query', new_callable=AsyncMock)
    async def test_remove_previous_response(self, mock_execute_query):
        """Test removing a previous response."""
        result = await self.postgres.remove_previous_response("message1")
        self.assertTrue(result)
        mock_execute_query.assert_called_with(
            "UPDATE messages SET bot_response = NULL WHERE message_id = $1;",
            is_insert=True,
            insert_values=("message1",),
            fetch_results=False
        )

    @patch('src.orm.Postgres._execute_query', new_callable=AsyncMock)
    async def test_get_latest_databases(self, mock_execute_query):
        """Test getting the latest databases."""
        mock_db_id = uuid.uuid4()
        mock_execute_query.return_value = [(mock_db_id, "TestCorp", "Tester")]
        result = await self.postgres.get_latest_databases()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["database_id"], str(mock_db_id))

    @patch('src.orm.Postgres._execute_query', new_callable=AsyncMock)
    async def test_get_latest_sessions(self, mock_execute_query):
        """Test getting the latest sessions."""
        mock_session_id = uuid.uuid4()
        mock_execute_query.return_value = [(mock_session_id, "paraphrased_q", "TestCorp", "Tester", "sometime")]
        result = await self.postgres.get_latest_sessions()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["session_id"], str(mock_session_id))

    @patch('src.orm.Postgres._execute_query', new_callable=AsyncMock)
    async def test_update_on_click_chat_row(self, mock_execute_query):
        """Test updating a chat row on click."""
        result = await self.postgres.update_on_click_chat_row("message1", "new_response", 1.23)
        self.assertTrue(result)
        mock_execute_query.assert_called_with(
            "UPDATE message SET bot_response = $1, elapsed_time = $2, do_suggest = $4, is_sql = $5 WHERE message_id = $3;",
            is_insert=True,
            insert_values=("new_response", 1.23, "message1", False, False),
            fetch_results=False
        )

    @patch('src.orm.Postgres._execute_query', new_callable=AsyncMock)
    async def test_update_selected_module(self, mock_execute_query):
        """Test updating the selected module."""
        result = await self.postgres.update_selected_module("message1", "new_module")
        self.assertTrue(result)
        mock_execute_query.assert_called_with(
            "UPDATE message SET selected_module = $1 WHERE message_id = $2;",
            is_insert=True,
            insert_values=("new_module", "message1"),
            fetch_results=False
        )

    @patch('src.orm.Postgres._execute_query', new_callable=AsyncMock)
    async def test_get_user_code_tenant_name(self, mock_execute_query):
        """Test getting user code and tenant name."""
        mock_execute_query.return_value = [("user1", "tenant1")]
        result = await self.postgres.get_user_code_tenant_name("session1")
        self.assertEqual(result, {"user_code": "user1", "tenant_name": "tenant1"})

    @patch('src.orm.Postgres._execute_query', new_callable=AsyncMock)
    async def test_insert_message_choices(self, mock_execute_query):
        """Test inserting message choices."""
        mock_execute_query.return_value = (uuid.uuid4(),)
        result = await self.postgres.insert_message_choices("message1", "choice1", "choice2")
        self.assertTrue(result)
        self.assertEqual(mock_execute_query.call_count, 2)

    @patch('src.orm.Postgres._execute_query', new_callable=AsyncMock)
    async def test_get_message_choices(self, mock_execute_query):
        """Test getting message choices."""
        mock_execute_query.return_value = [("choice1",), ("choice2",)]
        result = await self.postgres.get_message_choices("message1")
        self.assertEqual(result, ["choice1", "choice2"])

    @patch('src.orm.Postgres._execute_query', new_callable=AsyncMock)
    async def test_delete_database(self, mock_execute_query):
        """Test deleting a database."""
        result = await self.postgres.delete_database("db1")
        self.assertTrue(result)
        mock_execute_query.assert_called_with(
            "delete from public.databases where database_id = $1;",
            fetch_results=True,
            insert_values=("db1",)
        )

    @patch('src.orm.Postgres._execute_query', new_callable=AsyncMock)
    async def test_create_database_assistant_only(self, mock_execute_query):
        """Test create_database with only assistant_name."""
        mock_db_id = uuid.uuid4()
        mock_execute_query.return_value = (mock_db_id,)

        result = await self.postgres.create_database(assistant_name="Tester")
        self.assertEqual(result, {"database_id": str(mock_db_id)})
        mock_execute_query.assert_called_with(
            "INSERT INTO public.databases (assistant_name) VALUES ($1) RETURNING database_id;",
            insert_values=("Tester",),
            is_insert=True,
            fetch_results=True
        )

    @patch('src.orm.Postgres._execute_query', new_callable=AsyncMock)
    async def test_create_session_defaults(self, mock_execute_query):
        """Test create_session with default values."""
        mock_session_id = uuid.uuid4()
        mock_execute_query.return_value = (mock_session_id,)

        result = await self.postgres.create_session()
        self.assertEqual(result, {"session_id": str(mock_session_id)})
        mock_execute_query.assert_called_with(
            "INSERT INTO public.session DEFAULT VALUES RETURNING session_id;",
            insert_values=None,
            is_insert=True,
            fetch_results=True
        )

    @patch('src.orm.Postgres._execute_query', new_callable=AsyncMock)
    async def test_find_database_id_none(self, mock_execute_query):
        """Test find_database_id when it returns None."""
        mock_execute_query.return_value = (None,)
        result = await self.postgres.find_database_id("session1")
        self.assertEqual(result, {"database_id": None})

    @patch('src.orm.Postgres._execute_query', new_callable=AsyncMock)
    async def test_get_user_code_tenant_name_none(self, mock_execute_query):
        """Test get_user_code_tenant_name with None values."""
        mock_execute_query.return_value = [(None, None)]
        result = await self.postgres.get_user_code_tenant_name("session1")
        self.assertEqual(result, {"user_code": "", "tenant_name": ""})

        mock_execute_query.return_value = [] # Empty result
        result = await self.postgres.get_user_code_tenant_name("session1")
        self.assertEqual(result, {"user_code": "", "tenant_name": ""})

    @patch('src.orm.Postgres._execute_query', new_callable=AsyncMock)
    async def test_insert_chat_row_full(self, mock_execute_query):
        """Test insert_chat_row with all optional parameters."""
        mock_message_id = uuid.uuid4()
        mock_execute_query.return_value = (mock_message_id,)

        result = await self.postgres.insert_chat_row(
            session_id="s1",
            user_query="q1",
            paraphrased_query="pq1",
            bot_response="br1",
            response_type="detailed",
            elapsed_time=1.5,
            selected_module="mod1",
            response_template="tpl1",
            parameters='{"k": "v"}'
        )
        self.assertEqual(result, str(mock_message_id))
        
        # Verify the query construction
        args, kwargs = mock_execute_query.call_args
        query = args[0]
        self.assertIn("paraphrased_query", query)
        self.assertIn("bot_response", query)
        self.assertIn("elapsed_time", query)
        self.assertIn("selected_module", query)
        self.assertIn("response_type", query)
        self.assertIn("response_template", query)
        self.assertIn("parameters", query)
        
        values = kwargs['insert_values']
        self.assertEqual(len(values), 9) # 2 required + 7 optional

    @patch('src.orm.asyncpg.connect', new_callable=AsyncMock)
    async def test_execute_query_exception(self, mock_connect):
        """Test _execute_query handling exceptions."""
        mock_connect.side_effect = Exception("Connection failed")
        
        with self.assertRaises(Exception) as context:
            await self.postgres._execute_query("SELECT 1")

        self.assertTrue("Connection failed" in str(context.exception))

    def test_singleton_pattern(self):
        """Test that the class behaves as a Singleton (returns same instance)."""
        instance1 = Postgres()
        instance2 = Postgres()
        self.assertIs(instance1, instance2)
        # Verify initialization happened once
        self.assertEqual(instance1.database, "postgres")

    @patch('src.orm.Postgres._execute_query', new_callable=AsyncMock)
    async def test_create_database_company_only(self, mock_execute_query):
        """
        Covers the branch: if company_name is not None (and assistant is None).
        """
        mock_db_id = uuid.uuid4()
        mock_execute_query.return_value = (mock_db_id,)

        # Test with Company Name only
        result = await self.postgres.create_database(company_name="OnlyCorp")

        self.assertEqual(result, {"database_id": str(mock_db_id)})

        # Verify the generated SQL uses $1 for company_name
        args, kwargs = mock_execute_query.call_args
        sql_used = args[0]
        self.assertIn("company_name", sql_used)
        self.assertNotIn("assistant_name", sql_used)
        self.assertEqual(kwargs['insert_values'], ("OnlyCorp",))

    @patch('src.orm.Postgres._execute_query', new_callable=AsyncMock)
    async def test_create_session_dynamic_placeholders(self, mock_execute_query):
        """
        Covers the logic where placeholder_counter increments correctly
        when earlier arguments are missing (e.g., no database_id, but has tenant_name).
        """
        mock_session_id = uuid.uuid4()
        mock_execute_query.return_value = (mock_session_id,)

        # Pass only the SECOND argument (tenant_name)
        # Logic expectation: tenant_name should be $1, not $2
        result = await self.postgres.create_session(tenant_name="TenantOnly")

        self.assertEqual(result, {"session_id": str(mock_session_id)})

        args, kwargs = mock_execute_query.call_args
        sql_used = args[0]

        # Verify SQL construction
        self.assertIn("(tenant_name)", sql_used)
        self.assertIn("VALUES ($1)", sql_used)  # Should be $1 because it's the first actual value
        self.assertEqual(kwargs['insert_values'], ("TenantOnly",))

    @patch('src.orm.Postgres._execute_query', new_callable=AsyncMock)
    async def test_extract_response_type_empty(self, mock_execute_query):
        """Covers the case where DB returns None/Empty for response_type."""
        # Return empty list (no rows found)
        mock_execute_query.return_value = []

        result = await self.postgres.extract_response_type("session1")

        # Should default to "concise" per the conditional expression in the code
        self.assertEqual(result, {"response_type": "concise"})

    @patch('src.orm.Postgres._execute_query', new_callable=AsyncMock)
    async def test_get_message_fields_empty(self, mock_execute_query):
        """Covers the case where DB returns no message fields."""
        mock_execute_query.return_value = []

        result = await self.postgres.get_message_fields("session1", "msg1")

        # Expect empty list (lines 136-137)
        self.assertEqual(result, [])

    @patch('src.orm.Postgres._execute_query', new_callable=AsyncMock)
    async def test_validate_session_failure(self, mock_execute_query):
        """Covers the Exception block in validate_session."""
        mock_execute_query.side_effect = Exception("DB Error")

        with self.assertRaises(Exception):
            await self.postgres.validate_session("session1")

    @patch('src.orm.Postgres._execute_query', new_callable=AsyncMock)
    async def test_insert_chat_row_partial(self, mock_execute_query):
        """
        Test inserting a chat row with mixed optional parameters.
        Ensures the loop for values/columns works when some are None.
        """
        mock_execute_query.return_value = (uuid.uuid4(),)

        # user_query is required. We add ONE optional (response_type).
        # paraphased_query, bot_response etc are None.
        await self.postgres.insert_chat_row(
            "sess1", "query", response_type="detailed"
        )

        args, kwargs = mock_execute_query.call_args
        sql = args[0]

        # Check that 'paraphrased_query' is NOT in the columns
        self.assertNotIn("paraphrased_query", sql)
        # Check that 'response_type' IS in the columns
        self.assertIn("response_type", sql)

if __name__ == '__main__':
    unittest.main()

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch, call
from src.orm import Postgres


@pytest.fixture
def reset_singleton():
    """Reset the singleton instance before and after each test."""
    Postgres.reset_instance()
    yield
    Postgres.reset_instance()


@pytest.fixture
def mock_env_vars():
    """Mock environment variables."""
    with patch.dict('os.environ', {
        'POSTGRES_DB': 'test_db',
        'POSTGRES_ADDR': 'localhost',
        'POSTGRES_USER': 'test_user',
        'POSTGRES_PASSWORD': 'test_pass',
        'POSTGRES_PORT': '5432'
    }):
        yield


@pytest.fixture
def mock_connection():
    """Create a mock database connection."""
    connection = AsyncMock()
    connection.is_closed.return_value = False

    # Mock the transaction context manager properly
    transaction_mock = MagicMock()
    transaction_mock.__aenter__ = AsyncMock(return_value=None)
    transaction_mock.__aexit__ = AsyncMock(return_value=None)

    # --- FIX APPLIED HERE ---
    # We replace the .transaction attribute with a MagicMock.
    # If we left it as an AsyncMock (the default for methods on an AsyncMock object),
    # calling it would return a coroutine, which causes the "TypeError: 'coroutine' object..."
    # when used in an 'async with' statement.
    connection.transaction = MagicMock(return_value=transaction_mock)

    return connection


class TestPostgresSingleton:
    """Test singleton pattern behavior."""

    def test_singleton_instance(self, reset_singleton, mock_env_vars):
        """Test that only one instance is created."""
        pg1 = Postgres()
        pg2 = Postgres()
        assert pg1 is pg2

    def test_reset_instance(self, reset_singleton, mock_env_vars):
        """Test that reset_instance clears the singleton."""
        pg1 = Postgres()
        Postgres.reset_instance()
        pg2 = Postgres()
        assert pg1 is not pg2

    def test_initialization(self, reset_singleton, mock_env_vars):
        """Test that initialization sets correct attributes."""
        pg = Postgres()
        assert pg.database == 'test_db'
        assert pg.connection_address == 'localhost'


class TestExecuteQuery:
    """Test the _execute_query method."""

    @pytest.mark.asyncio
    async def test_execute_query_fetch_multiple(self, reset_singleton, mock_env_vars, mock_connection):
        """Test fetching multiple rows."""
        mock_connection.fetch.return_value = [('row1',), ('row2',)]

        with patch('asyncpg.connect', new_callable=AsyncMock, return_value=mock_connection):
            pg = Postgres()
            result = await pg._execute_query("SELECT * FROM test", fetch_results=True)

            assert result == [('row1',), ('row2',)]
            mock_connection.fetch.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_query_fetch_one(self, reset_singleton, mock_env_vars, mock_connection):
        """Test fetching a single row (is_insert=True)."""
        mock_connection.fetchrow.return_value = {'id': 1}

        with patch('asyncpg.connect', new_callable=AsyncMock, return_value=mock_connection):
            pg = Postgres()
            result = await pg._execute_query(
                "INSERT INTO test VALUES ($1)",
                is_insert=True,
                insert_values=('value',),
                fetch_results=True
            )

            assert result == {'id': 1}
            mock_connection.fetchrow.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_query_no_fetch(self, reset_singleton, mock_env_vars, mock_connection):
        """Test executing without fetching results."""
        with patch('asyncpg.connect', new_callable=AsyncMock, return_value=mock_connection):
            pg = Postgres()
            result = await pg._execute_query(
                "UPDATE test SET value = $1",
                insert_values=('new_value',),
                fetch_results=False
            )

            assert result is True
            mock_connection.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_query_connection_closed(self, reset_singleton, mock_env_vars, mock_connection):
        """Test that connection is closed even if already closed."""
        mock_connection.is_closed.return_value = True
        mock_connection.fetch.return_value = []

        with patch('asyncpg.connect', new_callable=AsyncMock, return_value=mock_connection):
            pg = Postgres()
            await pg._execute_query("SELECT * FROM test", fetch_results=True)

            # Should not call close if already closed
            mock_connection.close.assert_not_called()

    @pytest.mark.asyncio
    async def test_execute_query_exception(self, reset_singleton, mock_env_vars, mock_connection):
        """Test exception handling in _execute_query."""
        mock_connection.fetch.side_effect = Exception("Database error")

        with patch('asyncpg.connect', new_callable=AsyncMock, return_value=mock_connection):
            pg = Postgres()

            with pytest.raises(Exception) as exc_info:
                await pg._execute_query("SELECT * FROM test", fetch_results=True)

            assert "Database error" in str(exc_info.value)


class TestSessionMethods:
    """Test session-related methods."""

    @pytest.mark.asyncio
    async def test_exist_session_true(self, reset_singleton, mock_env_vars, mock_connection):
        """Test exist_session returns True when session exists."""
        mock_connection.fetch.return_value = [('session123',)]

        with patch('asyncpg.connect', new_callable=AsyncMock, return_value=mock_connection):
            pg = Postgres()
            result = await pg.exist_session('session123')

            assert result is True

    @pytest.mark.asyncio
    async def test_exist_session_false(self, reset_singleton, mock_env_vars, mock_connection):
        """Test exist_session returns False when session doesn't exist."""
        mock_connection.fetch.return_value = []

        with patch('asyncpg.connect', new_callable=AsyncMock, return_value=mock_connection):
            pg = Postgres()
            result = await pg.exist_session('session999')

            assert result is False

    @pytest.mark.asyncio
    async def test_validate_session_valid(self, reset_singleton, mock_env_vars, mock_connection):
        """Test validate_session with valid session."""
        mock_connection.fetch.return_value = [(1,)]

        with patch('asyncpg.connect', new_callable=AsyncMock, return_value=mock_connection):
            pg = Postgres()
            result = await pg.validate_session('session123')

            assert result is True

    @pytest.mark.asyncio
    async def test_validate_session_invalid(self, reset_singleton, mock_env_vars, mock_connection):
        """Test validate_session with invalid session."""
        mock_connection.fetch.return_value = []

        with patch('asyncpg.connect', new_callable=AsyncMock, return_value=mock_connection):
            pg = Postgres()
            result = await pg.validate_session('session999')

            assert result is False

    @pytest.mark.asyncio
    async def test_validate_session_exception(self, reset_singleton, mock_env_vars, mock_connection):
        """Test validate_session handles exceptions."""
        mock_connection.fetch.side_effect = Exception("DB Error")

        with patch('asyncpg.connect', new_callable=AsyncMock, return_value=mock_connection):
            pg = Postgres()

            with pytest.raises(Exception):
                await pg.validate_session('session123')

    @pytest.mark.asyncio
    async def test_create_session_with_all_params(self, reset_singleton, mock_env_vars, mock_connection):
        """Test create_session with all parameters."""
        mock_connection.fetchrow.return_value = ('new_session_id',)

        with patch('asyncpg.connect', new_callable=AsyncMock, return_value=mock_connection):
            pg = Postgres()
            result = await pg.create_session(
                database_id='db123',
                tenant_name='tenant1',
                user_code='user1'
            )

            assert result == {'session_id': 'new_session_id'}

    @pytest.mark.asyncio
    async def test_create_session_default_values(self, reset_singleton, mock_env_vars, mock_connection):
        """Test create_session with default values."""
        mock_connection.fetchrow.return_value = ('new_session_id',)

        with patch('asyncpg.connect', new_callable=AsyncMock, return_value=mock_connection):
            pg = Postgres()
            result = await pg.create_session()

            assert result == {'session_id': 'new_session_id'}

    @pytest.mark.asyncio
    async def test_create_session_partial_params(self, reset_singleton, mock_env_vars, mock_connection):
        """Test create_session with some parameters."""
        mock_connection.fetchrow.return_value = ('new_session_id',)

        with patch('asyncpg.connect', new_callable=AsyncMock, return_value=mock_connection):
            pg = Postgres()
            result = await pg.create_session(database_id='db123', tenant_name='tenant1')

            assert result == {'session_id': 'new_session_id'}


class TestDatabaseMethods:
    """Test database-related methods."""

    @pytest.mark.asyncio
    async def test_create_database_with_both_params(self, reset_singleton, mock_env_vars, mock_connection):
        """Test create_database with company and assistant names."""
        mock_connection.fetchrow.return_value = ('db123',)

        with patch('asyncpg.connect', new_callable=AsyncMock, return_value=mock_connection):
            pg = Postgres()
            result = await pg.create_database(company_name='CompanyA', assistant_name='AssistantB')

            assert result == {'database_id': 'db123'}

    @pytest.mark.asyncio
    async def test_create_database_company_only(self, reset_singleton, mock_env_vars, mock_connection):
        """Test create_database with only company name."""
        mock_connection.fetchrow.return_value = ('db123',)

        with patch('asyncpg.connect', new_callable=AsyncMock, return_value=mock_connection):
            pg = Postgres()
            result = await pg.create_database(company_name='CompanyA')

            assert result == {'database_id': 'db123'}

    @pytest.mark.asyncio
    async def test_create_database_assistant_only(self, reset_singleton, mock_env_vars, mock_connection):
        """Test create_database with only assistant name."""
        mock_connection.fetchrow.return_value = ('db123',)

        with patch('asyncpg.connect', new_callable=AsyncMock, return_value=mock_connection):
            pg = Postgres()
            result = await pg.create_database(assistant_name='AssistantB')

            assert result == {'database_id': 'db123'}

    @pytest.mark.asyncio
    async def test_create_database_default_values(self, reset_singleton, mock_env_vars, mock_connection):
        """Test create_database with default values."""
        mock_connection.fetchrow.return_value = ('db123',)

        with patch('asyncpg.connect', new_callable=AsyncMock, return_value=mock_connection):
            pg = Postgres()
            result = await pg.create_database()

            assert result == {'database_id': 'db123'}

    @pytest.mark.asyncio
    async def test_find_database_id(self, reset_singleton, mock_env_vars, mock_connection):
        """Test find_database_id."""
        mock_connection.fetchrow.return_value = ('db123',)

        with patch('asyncpg.connect', new_callable=AsyncMock, return_value=mock_connection):
            pg = Postgres()
            result = await pg.find_database_id('session123')

            assert result == {'database_id': 'db123'}

    @pytest.mark.asyncio
    async def test_find_database_id_none(self, reset_singleton, mock_env_vars, mock_connection):
        """Test find_database_id when database_id is None."""
        mock_connection.fetchrow.return_value = (None,)

        with patch('asyncpg.connect', new_callable=AsyncMock, return_value=mock_connection):
            pg = Postgres()
            result = await pg.find_database_id('session123')

            assert result == {'database_id': None}

    @pytest.mark.asyncio
    async def test_find_company_assistant_names(self, reset_singleton, mock_env_vars, mock_connection):
        """Test find_company_assistant_names."""
        mock_connection.fetchrow.return_value = ('CompanyA', 'AssistantB')

        with patch('asyncpg.connect', new_callable=AsyncMock, return_value=mock_connection):
            pg = Postgres()
            result = await pg.find_company_assistant_names('db123')

            assert result == {'company_name': 'CompanyA', 'assistant_name': 'AssistantB'}

    @pytest.mark.asyncio
    async def test_delete_database(self, reset_singleton, mock_env_vars, mock_connection):
        """Test delete_database."""
        mock_connection.fetch.return_value = []

        with patch('asyncpg.connect', new_callable=AsyncMock, return_value=mock_connection):
            pg = Postgres()
            result = await pg.delete_database('db123')

            assert result is True

    @pytest.mark.asyncio
    async def test_get_latest_databases(self, reset_singleton, mock_env_vars, mock_connection):
        """Test get_latest_databases."""
        mock_connection.fetch.return_value = [
            ('db1', 'Company1', 'Assistant1'),
            ('db2', 'Company2', 'Assistant2')
        ]

        with patch('asyncpg.connect', new_callable=AsyncMock, return_value=mock_connection):
            pg = Postgres()
            result = await pg.get_latest_databases(num_databases=2)

            assert len(result) == 2
            assert result[0] == {'database_id': 'db1', 'company_name': 'Company1', 'assistant_name': 'Assistant1'}
            assert result[1] == {'database_id': 'db2', 'company_name': 'Company2', 'assistant_name': 'Assistant2'}


class TestMessageMethods:
    """Test message-related methods."""

    @pytest.mark.asyncio
    async def test_get_message_fields(self, reset_singleton, mock_env_vars, mock_connection):
        """Test get_message_fields."""
        mock_connection.fetch.return_value = [('user query', 'paraphrased', 'bot response')]

        with patch('asyncpg.connect', new_callable=AsyncMock, return_value=mock_connection):
            pg = Postgres()
            result = await pg.get_message_fields('session123', 'msg123')

            assert result ==  ('user query', 'paraphrased', 'bot response')

    @pytest.mark.asyncio
    async def test_get_message_fields_empty(self, reset_singleton, mock_env_vars, mock_connection):
        """Test get_message_fields with no results."""
        mock_connection.fetch.return_value = []

        with patch('asyncpg.connect', new_callable=AsyncMock, return_value=mock_connection):
            pg = Postgres()
            result = await pg.get_message_fields('session123', 'msg999')

            assert result == []

    @pytest.mark.asyncio
    async def test_insert_chat_row_minimal(self, reset_singleton, mock_env_vars, mock_connection):
        """Test insert_chat_row with minimal parameters."""
        mock_connection.fetchrow.return_value = ('msg123',)

        with patch('asyncpg.connect', new_callable=AsyncMock, return_value=mock_connection):
            pg = Postgres()
            result = await pg.insert_chat_row('session123', 'user query')

            assert result == 'msg123'

    @pytest.mark.asyncio
    async def test_insert_chat_row_full(self, reset_singleton, mock_env_vars, mock_connection):
        """Test insert_chat_row with all parameters."""
        mock_connection.fetchrow.return_value = ('msg123',)

        with patch('asyncpg.connect', new_callable=AsyncMock, return_value=mock_connection):
            pg = Postgres()
            result = await pg.insert_chat_row(
                session_id='session123',
                user_query='user query',
                paraphrased_query='paraphrased',
                bot_response='response',
                response_type='detailed',
                elapsed_time=1.5,
                selected_module='module1',
                response_template='template1',
                parameters='{"key": "value"}'
            )

            assert result == 'msg123'

    @pytest.mark.asyncio
    async def test_update_last_chat_row(self, reset_singleton, mock_env_vars, mock_connection):
        """Test update_last_chat_row."""
        mock_connection.fetchrow.return_value = ('msg123',)

        with patch('asyncpg.connect', new_callable=AsyncMock, return_value=mock_connection):
            pg = Postgres()
            result = await pg.update_last_chat_row(
                session_id='session123',
                paraphrased_query='paraphrased',
                bot_response='response',
                is_sql=True,
                elapsed_time=2.5,
                do_suggest=True,
                selected_module='module1',
                response_template='template1',
                parameters='{"key": "value"}'
            )

            assert result == 'msg123'

    @pytest.mark.asyncio
    async def test_update_on_click_chat_row(self, reset_singleton, mock_env_vars, mock_connection):
        """Test update_on_click_chat_row."""
        mock_connection.execute.return_value = None

        with patch('asyncpg.connect', new_callable=AsyncMock, return_value=mock_connection):
            pg = Postgres()
            result = await pg.update_on_click_chat_row(
                message_id='msg123',
                bot_response='response',
                elapsed_time=1.0,
                do_suggest=True,
                is_sql=False
            )

            assert result is True

    @pytest.mark.asyncio
    async def test_update_selected_module(self, reset_singleton, mock_env_vars, mock_connection):
        """Test update_selected_module."""
        mock_connection.execute.return_value = None

        with patch('asyncpg.connect', new_callable=AsyncMock, return_value=mock_connection):
            pg = Postgres()
            result = await pg.update_selected_module('msg123', 'module2')

            assert result is True

    @pytest.mark.asyncio
    async def test_remove_previous_response(self, reset_singleton, mock_env_vars, mock_connection):
        """Test remove_previous_response."""
        mock_connection.execute.return_value = None

        with patch('asyncpg.connect', new_callable=AsyncMock, return_value=mock_connection):
            pg = Postgres()
            result = await pg.remove_previous_response('msg123')

            assert result is True


class TestHistoryMethods:
    """Test history-related methods."""

    @pytest.mark.asyncio
    async def test_get_history_with_paraphrase(self, reset_singleton, mock_env_vars, mock_connection):
        """Test get_history with paraphrase."""
        mock_connection.fetch.return_value = [
            ('query1', 'paraphrased1', 'response1', 'msg1', True, 'module1', 1.5, True, 'template1', '{}'),
            ('query2', 'paraphrased2', 'response2', 'msg2', False, 'module2', 2.0, False, 'template2', '{}')
        ]

        with patch('asyncpg.connect', new_callable=AsyncMock, return_value=mock_connection):
            pg = Postgres()
            result = await pg.get_history('session123', page_index=1, page_size=10, with_paraphrase=True)

            assert len(result) == 2
            assert result[0]['paraphrased_query'] == 'paraphrased2'
            assert result[0]['query'] == 'query2'

    @pytest.mark.asyncio
    async def test_get_history_without_paraphrase(self, reset_singleton, mock_env_vars, mock_connection):
        """Test get_history without paraphrase."""
        mock_connection.fetch.return_value = [
            ('query1', 'paraphrased1', 'response1', 'msg1', True, 'module1', 1.5, True, 'template1', '{}')
        ]

        with patch('asyncpg.connect', new_callable=AsyncMock, return_value=mock_connection):
            pg = Postgres()
            result = await pg.get_history('session123', page_index=1, page_size=10, with_paraphrase=False)

            assert len(result) == 1
            assert 'paraphrased_query' not in result[0]
            assert result[0]['query'] == 'query1'

    @pytest.mark.asyncio
    async def test_get_history_pagination(self, reset_singleton, mock_env_vars, mock_connection):
        """Test get_history with pagination."""
        mock_connection.fetch.return_value = []

        with patch('asyncpg.connect', new_callable=AsyncMock, return_value=mock_connection):
            pg = Postgres()
            result = await pg.get_history('session123', page_index=2, page_size=5)

            # Verify offset calculation (page_index - 1) * page_size = (2-1)*5 = 5
            assert result == []

    @pytest.mark.asyncio
    async def test_get_latest_sessions(self, reset_singleton, mock_env_vars, mock_connection):
        """Test get_latest_sessions."""
        mock_connection.fetch.return_value = [
            ('session1', 'query1', 'Company1', 'Assistant1', '2024-01-01'),
            ('session2', 'query2', 'Company2', 'Assistant2', '2024-01-02')
        ]

        with patch('asyncpg.connect', new_callable=AsyncMock, return_value=mock_connection):
            pg = Postgres()
            result = await pg.get_latest_sessions(num_sessions=2, offset=0, recent_limit=1000)

            assert len(result) == 2
            assert result[0]['session_id'] == 'session1'
            assert result[0]['paraphrased_query'] == 'query1'
            assert result[0]['company_name'] == 'Company1'


class TestResponseTypeMethods:
    """Test response type methods."""

    @pytest.mark.asyncio
    async def test_extract_response_type_exists(self, reset_singleton, mock_env_vars, mock_connection):
        """Test extract_response_type when response type exists."""
        mock_connection.fetch.return_value = [('detailed',)]

        with patch('asyncpg.connect', new_callable=AsyncMock, return_value=mock_connection):
            pg = Postgres()
            result = await pg.extract_response_type('session123')

            assert result == {'response_type': 'detailed'}

    @pytest.mark.asyncio
    async def test_extract_response_type_default(self, reset_singleton, mock_env_vars, mock_connection):
        """Test extract_response_type returns default when not found."""
        mock_connection.fetch.return_value = []

        with patch('asyncpg.connect', new_callable=AsyncMock, return_value=mock_connection):
            pg = Postgres()
            result = await pg.extract_response_type('session123')

            assert result == {'response_type': 'concise'}


class TestFeedbackMethods:
    """Test feedback-related methods."""

    @pytest.mark.asyncio
    async def test_set_feedback_success(self, reset_singleton, mock_env_vars, mock_connection):
        """Test set_feedback successful update."""
        mock_connection.fetch.return_value = [('msg123',)]

        with patch('asyncpg.connect', new_callable=AsyncMock, return_value=mock_connection):
            pg = Postgres()
            result = await pg.set_feedback('msg123', 'positive')

            assert result is True

    @pytest.mark.asyncio
    async def test_set_feedback_no_update(self, reset_singleton, mock_env_vars, mock_connection):
        """Test set_feedback when no update occurs."""
        mock_connection.fetch.return_value = []

        with patch('asyncpg.connect', new_callable=AsyncMock, return_value=mock_connection):
            pg = Postgres()
            result = await pg.set_feedback('msg123', 'negative')

            assert result is False


class TestUserMethods:
    """Test user-related methods."""

    @pytest.mark.asyncio
    async def test_get_user_code_tenant_name_both_exist(self, reset_singleton, mock_env_vars, mock_connection):
        """Test get_user_code_tenant_name when both exist."""
        mock_connection.fetch.return_value = [('user123', 'tenant123')]

        with patch('asyncpg.connect', new_callable=AsyncMock, return_value=mock_connection):
            pg = Postgres()
            result = await pg.get_user_code_tenant_name('session123')

            assert result == {'user_code': 'user123', 'tenant_name': 'tenant123'}

    @pytest.mark.asyncio
    async def test_get_user_code_tenant_name_none_values(self, reset_singleton, mock_env_vars, mock_connection):
        """Test get_user_code_tenant_name when values are None."""
        mock_connection.fetch.return_value = [(None, None)]

        with patch('asyncpg.connect', new_callable=AsyncMock, return_value=mock_connection):
            pg = Postgres()
            result = await pg.get_user_code_tenant_name('session123')

            assert result == {'user_code': '', 'tenant_name': ''}

    @pytest.mark.asyncio
    async def test_get_user_code_tenant_name_partial_none(self, reset_singleton, mock_env_vars, mock_connection):
        """Test get_user_code_tenant_name when one value is None."""
        mock_connection.fetch.return_value = [('user123', None)]

        with patch('asyncpg.connect', new_callable=AsyncMock, return_value=mock_connection):
            pg = Postgres()
            result = await pg.get_user_code_tenant_name('session123')

            assert result == {'user_code': 'user123', 'tenant_name': ''}


class TestMessageChoicesMethods:
    """Test message choices methods."""

    @pytest.mark.asyncio
    async def test_insert_message_choices_single(self, reset_singleton, mock_env_vars, mock_connection):
        """Test insert_message_choices with single choice."""
        mock_connection.fetch.return_value = [('choice1',)]

        with patch('asyncpg.connect', new_callable=AsyncMock, return_value=mock_connection):
            pg = Postgres()
            result = await pg.insert_message_choices('msg123', 'option1')

            assert result is True

    @pytest.mark.asyncio
    async def test_insert_message_choices_multiple(self, reset_singleton, mock_env_vars, mock_connection):
        """Test insert_message_choices with multiple choices."""
        mock_connection.fetch.return_value = [('choice1',)]

        with patch('asyncpg.connect', new_callable=AsyncMock, return_value=mock_connection):
            pg = Postgres()
            result = await pg.insert_message_choices('msg123', 'option1', 'option2', 'option3')

            assert result is True

    @pytest.mark.asyncio
    async def test_get_message_choices(self, reset_singleton, mock_env_vars, mock_connection):
        """Test get_message_choices."""
        mock_connection.fetch.return_value = [
            ('choice1',),
            ('choice2',),
            ('choice3',)
        ]

        with patch('asyncpg.connect', new_callable=AsyncMock, return_value=mock_connection):
            pg = Postgres()
            result = await pg.get_message_choices('msg123')

            assert result == ['choice1', 'choice2', 'choice3']

    @pytest.mark.asyncio
    async def test_get_message_choices_empty(self, reset_singleton, mock_env_vars, mock_connection):
        """Test get_message_choices with no choices."""
        mock_connection.fetch.return_value = []

        with patch('asyncpg.connect', new_callable=AsyncMock, return_value=mock_connection):
            pg = Postgres()
            result = await pg.get_message_choices('msg123')

            assert result == []


class TestEdgeCases:
    """Test edge cases and error scenarios."""

    @pytest.mark.asyncio
    async def test_connection_error_handling(self, reset_singleton, mock_env_vars):
        """Test handling of connection errors."""
        with patch('asyncpg.connect', new_callable=AsyncMock, side_effect=Exception("Connection failed")):
            pg = Postgres()

            with pytest.raises(Exception) as exc_info:
                await pg.exist_session('session123')

            assert "Connection failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_insert_values_with_empty_tuple(self, reset_singleton, mock_env_vars, mock_connection):
        """Test query execution with empty values tuple."""
        mock_connection.fetch.return_value = []

        with patch('asyncpg.connect', new_callable=AsyncMock, return_value=mock_connection):
            pg = Postgres()
            result = await pg._execute_query(
                "SELECT * FROM test",
                fetch_results=True,
                insert_values=()
            )

            assert result == []

    @pytest.mark.asyncio
    async def test_multiple_connections_singleton(self, reset_singleton, mock_env_vars):
        """Test that multiple async operations use the same singleton."""
        pg1 = Postgres()
        pg2 = Postgres()

        # Both should be the same instance
        assert pg1 is pg2

        # Should only initialize once
        assert pg1.database == 'test_db'
        assert pg2.database == 'test_db'


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=src.orm", "--cov-report=html", "--cov-report=term"])
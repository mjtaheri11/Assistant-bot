import unittest
import sys
import os
import json
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime, timedelta

# ==========================================
# 1. PATH SETUP & DEPENDENCY MOCKING
# ==========================================

# Calculate paths to ensure imports work from both 'root' and 'tests/' directories
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))

# Add project root to sys.path so we can import 'src' as a package
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Create Mocks for internal dependencies (modules inside src/)
# We must inject these into sys.modules BEFORE importing logic.
# This satisfies the "from .prompts import ..." relative imports inside logic.py
mock_prompts = MagicMock()
mock_retriever = MagicMock()
mock_config = MagicMock()
mock_cache = MagicMock()
mock_utils = MagicMock()
mock_bo = MagicMock()
mock_bo_v2 = MagicMock()
mock_router = MagicMock()

# Configure specific mock values for config to avoid KeyErrors during import/runtime
mock_config.config = {
    "cache": {"alpha_threshold": 0.8},
    "modules": {"proposable_modules": ["انبار", "فروش", "دفتر کل"]},
    "router_model": {
        "alpha_threshold": 0.6,
        "beta_threshold": 0.4,
        "embedding_model": "fake-model",
        "address": "fake-address",
        "model_name": "fake-name"
    },
    "database": {
        "collection_name": "test_collection",
        "company_name": "TestCorp",
        "assistant_name": "TestBot",
        "response_type": "normal",
        "use_cache": True
    }
}


# Mock the langfuse decorator to prevent errors
def mock_observe():
    def decorator(func):
        return func

    return decorator


mock_langfuse = MagicMock()
mock_langfuse.observe = mock_observe

# Inject mocks into sys.modules using the 'src.' namespace
# This is crucial because logic.py uses relative imports (from .x import y)
sys.modules['src.prompts'] = mock_prompts
sys.modules['src.retriever'] = mock_retriever
sys.modules['src.config'] = mock_config
sys.modules['src.cache'] = mock_cache
sys.modules['src.utils'] = mock_utils
sys.modules['src.business_objects'] = mock_bo
sys.modules['src.business_objects_v2'] = mock_bo_v2
sys.modules['src.semantic_router'] = mock_router
sys.modules['langfuse'] = mock_langfuse

# Also mock heavy external libraries that might not be installed in the test env
sys.modules['torch'] = MagicMock()
sys.modules['numpy'] = MagicMock()
sys.modules['sqlglot'] = MagicMock()
sys.modules['sqlglot.exp'] = MagicMock()  # Ensure submodules work
# We allow sqlglot.parse to be mocked specifically in tests, but basic import must exist

# ==========================================
# 2. IMPORT MODULE UNDER TEST
# ==========================================
# Now it is safe to import logic. We import it via 'src.logic'
# so relative imports resolve correctly.
from src import logic


class TestLogicModule(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        """Runs before every test method."""
        # Reset utility side effects
        mock_utils.json_cleaning.side_effect = lambda x: x
        mock_utils.json_cleaning_1.side_effect = lambda x: x

        # Setup standard LLM client mocks
        self.mock_clients = {
            "oss": MagicMock(),
            "gpt": MagicMock()
        }
        self.mock_clients["oss"].chat.completions.create = AsyncMock()
        self.mock_clients["gpt"].chat.completions.create = AsyncMock()

    # --- Utility Function Tests ---

    def test_extract_tables_robust(self):
        # We need to mock sqlglot.parse since we mocked the library
        with patch('src.logic.sqlglot.parse') as mock_parse:
            # Create a mock statement chain simulating a table find
            mock_statement = MagicMock()

            # Simulate a CTE
            mock_cte = MagicMock()
            mock_cte.alias = "cte_table"

            # Simulate a real table
            mock_table = MagicMock()
            mock_table.name = "real_table"
            mock_table.catalog = None
            mock_table.db = None

            # Setup the behavior of find_all
            def find_all_side_effect(exp_type):
                # logic.py imports sqlglot.exp.CTE / Table.
                # Since we mocked sqlglot, we need to check against the mocked types
                if exp_type == logic.sqlglot.exp.CTE:
                    return [mock_cte]
                if exp_type == logic.sqlglot.exp.Table:
                    return [mock_table]
                return []

            mock_statement.find_all.side_effect = find_all_side_effect
            mock_parse.return_value = [mock_statement]

            result = logic.extract_tables_robust("SELECT * FROM ...")

            self.assertIn("real_table", result["tables"])
            self.assertIn("cte_table", result["ctes"])

    @patch('src.logic.datetime')
    def test_calculate_date_context(self, mock_dt):
        # Fix date to 2024-03-25 (Post-Nowruz 1403)
        fixed_date = datetime(2024, 3, 25, 10, 30)
        mock_dt.now.return_value = fixed_date
        mock_dt.timedelta = timedelta  # Restore real timedelta

        context = logic.calculate_date_context()

        self.assertEqual(context['today_date'], "2025-12-10")
        self.assertEqual(context['current_hour'], "17")
        self.assertEqual(context['persian_year'], "1404")

    def test_subselect_yaml(self):
        data = {
            "table1": {"key1": "val1", "key2": "val2"},
            "table2": {"keyA": "valA"}
        }
        selections = {
            "table1": ["key1"],
            "table2": None
        }

        result_dict = logic.subselect_yaml(data, selections, output_format="dict")
        self.assertEqual(result_dict["table1"], {"key1": "val1"})
        self.assertNotIn("key2", result_dict["table1"])
        self.assertEqual(result_dict["table2"], {"keyA": "valA"})

    def test_hash_string(self):
        result = logic.hash_string("test")
        self.assertEqual(result, "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08")

    def test_model_selector(self):
        res_oss = logic.model_selector(True, self.mock_clients)
        self.assertEqual(res_oss["client"], self.mock_clients["oss"])

        res_gpt = logic.model_selector(False, self.mock_clients)
        self.assertEqual(res_gpt["client"], self.mock_clients["gpt"])

    def test_history_serializer(self):
        history = [("Hi", "Hello")]
        result = logic.history_serializer(history)
        self.assertIn("USER: Hi", result)
        self.assertIn("ASSISTANT: Hello", result)

    def test_is_somewhat_uniform(self):
        # Uniform distribution (CV = 0)
        freq = {"a": 10, "b": 10}
        needs_clarif, mean = asyncio.run(logic.is_somewhat_uniform(freq))
        self.assertTrue(needs_clarif)

        # Skewed distribution
        freq = {"a": 100, "b": 1}
        needs_clarif, mean = asyncio.run(logic.is_somewhat_uniform(freq, threshold=0.5))
        self.assertFalse(needs_clarif)

    # --- Async Logic Tests ---

    async def test_get_chat_response(self):
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Response"
        self.mock_clients["oss"].chat.completions.create.return_value = mock_response

        client_model = {"client": self.mock_clients["oss"], "model_name": "test", "extra": {}}
        result = await logic.get_chat_response("prompt", client_model)
        self.assertEqual(result, "Response")

    @patch('src.logic.Cache')
    async def test_get_cache_response(self, MockCacheClass):
        mock_instance = MockCacheClass.return_value
        # Cache Hit
        mock_instance.get_embedding_match = AsyncMock(return_value=[
            {"response": "Cached", "url": "url", "thumb_up": 1}
        ])
        res, url = await logic.get_cache_response("query")
        self.assertEqual(res, "Cached")

        # Cache Miss
        mock_instance.get_embedding_match = AsyncMock(return_value=[])
        res, url = await logic.get_cache_response("query")
        self.assertEqual(res, "")

    @patch('src.logic.Retriever')
    async def test_prepare_final_context_clarification(self, MockRetriever):
        mock_retriever_instance = MockRetriever.return_value
        # Mixed modules -> Clarification needed
        context_data = [
            {"text": "docA", "module": "انبار"},
            {"text": "docB", "module": "فروش"}
        ]
        mock_retriever_instance.retrieve_context = AsyncMock(return_value=(context_data, []))

        do_clarify, modules, docs, emb = await logic.prepare_final_context("query")
        self.assertTrue(do_clarify)
        self.assertIn("انبار", modules)

    async def test_sql_responder(self):
        # Mock module schema constants
        logic.FINANCIAL_BO_MODIFIED = "fin"
        logic.LOGISTICS_SALES_MODIFIED = "log"

        with patch('src.logic.get_chat_response', new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = '{"SQL": "SELECT 1"}'

            response = await logic.sql_responder_(
                self.mock_clients, "query", detected_module="انبار"
            )
            self.assertEqual(response, '{"SQL": "SELECT 1"}')

    @patch('src.logic.SemanticRouterPipeline')
    async def test_determine_final_route(self, MockRouterPipe):
        mock_pipe = MockRouterPipe.return_value
        # Mock prediction: sql is top
        mock_pipe.predict_sentences_input_embedding_and_sentences.return_value = (
            [["sql"]], [("sql", 0.9)], 0.9
        )
        route = await logic._determine_final_route(self.mock_clients, "query", [], use_oss=True)
        self.assertEqual(route, "sql")

    # --- Integration: Chat Responder ---

    @patch('src.logic.get_route_for_utterance', new_callable=AsyncMock)
    @patch('src.logic.prepare_final_context', new_callable=AsyncMock)
    @patch('src.logic.utterance_paraphraser', new_callable=AsyncMock)
    @patch('src.logic.get_cache_response', new_callable=AsyncMock)
    async def test_chat_responder_cache_hit(self, mock_cache_resp, mock_para, mock_prep, mock_route):
        # Simulate cache hit
        mock_cache_resp.return_value = ("Cached Answer", "url")

        res = await logic.chat_responder_(
            self.mock_clients, [], "Hello", use_cache=True
        )

        # Check return signature: (utterance, response, context, do_clarify, modules)
        self.assertEqual(res[1], "Cached Answer")
        mock_para.assert_not_called()

    @patch('src.logic.query_responder', new_callable=AsyncMock)
    @patch('src.logic.get_route_for_utterance', new_callable=AsyncMock)
    @patch('src.logic.prepare_final_context', new_callable=AsyncMock)
    @patch('src.logic.utterance_paraphraser', new_callable=AsyncMock)
    @patch('src.logic.get_cache_response', new_callable=AsyncMock)
    async def test_chat_responder_normal_flow(self, mock_cache, mock_para, mock_prep, mock_route, mock_query):
        # 1. No cache
        mock_cache.return_value = ("", "")
        # 2. Paraphrase
        mock_para.return_value = "Para"
        # 3. Context
        mock_prep.return_value = (False, ["sales"], "Context", [])
        # 4. Route
        mock_route.return_value = "qa"
        # 5. Answer
        mock_query.return_value = "LLM Answer"

        result = await logic.chat_responder_(self.mock_clients, [], "Q", use_cache=True)

        self.assertEqual(result[1], "LLM Answer")
        self.assertEqual(result[2], "Context")
        self.assertFalse(result[3])

    @patch('src.logic.Cache')
    async def test_feedback(self, MockCache):
        mock_instance = MockCache.return_value
        mock_instance.increment_flag = AsyncMock()

        await logic.feedback_("q", "a", "u", "flag")
        mock_instance.increment_flag.assert_called_once()


if __name__ == '__main__':
    unittest.main()
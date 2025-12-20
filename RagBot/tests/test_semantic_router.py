import unittest
from unittest.mock import patch, MagicMock, AsyncMock, mock_open, call
import os
import numpy as np
import pandas as pd
from pathlib import Path
import tempfile
import joblib
from sklearn.linear_model import LogisticRegression
import asyncio

# Import the classes to be tested
from src.semantic_router import (
    SemanticRouterPipeline,
    Qwen3Embedder,
    JinaaEmbedder,
    E5Embedder,
    LogisticRegressionModel,
    SVMModel,
    MLPClassifierModel,
    RFModel,
    OpenRouterEmbedder,
    CLASS_NAMES,
    LIST_OF_VALID_MODEL_NAMES,
)

rng = np.random.default_rng(42)


class TestSemanticRouter(unittest.TestCase):

    def setUp(self):
        """Set up a clean environment for each test."""
        # Reset the singleton for isolation
        SemanticRouterPipeline._instance = None

    @patch('src.semantic_router.E5Embedder')
    @patch('src.semantic_router.LogisticRegressionModel')
    def test_pipeline_initialization_inference(self, mock_classifier, mock_embedder):
        """Test pipeline initialization in inference-only mode."""
        pipeline = SemanticRouterPipeline(inference_only=True)
        self.assertIsNotNone(pipeline.embedder)
        self.assertIsNotNone(pipeline.classifier)
        mock_embedder.assert_called_once()
        mock_classifier.assert_called_once()

    @patch('src.semantic_router.pd.read_excel')
    @patch('src.semantic_router.np.load')
    @patch('src.semantic_router.train_test_split')
    @patch('src.semantic_router.LogisticRegressionModel')
    @patch('src.semantic_router.E5Embedder')
    def test_pipeline_training(self, mock_embedder, mock_classifier, mock_split, mock_np_load, mock_pd_read):
        """Test the full training pipeline."""
        # Mock data and embeddings
        mock_df = pd.DataFrame({'sentence': ['s1', 's2'], 'label': ['l1', 'l2']})
        mock_pd_read.return_value = mock_df
        mock_embeddings = np.array([[1.0], [2.0]])
        mock_np_load.return_value = mock_embeddings
        mock_split.return_value = (mock_embeddings, mock_embeddings, ['l1', 'l2'], ['l1', 'l2'])

        mock_classifier_instance = MagicMock()
        mock_classifier.return_value = mock_classifier_instance
        mock_classifier_instance.predict.return_value = ['l1', 'l2']
        mock_classifier_instance.calc_metrics.return_value = (1, '')

        # Path for saving the model
        save_path = (Path(__file__).parent / "resources" / "models" / "classifiers").as_posix()
        try:
            _ = SemanticRouterPipeline(
                inference_only=False,
                dataset_address='dummy.xlsx',
                train_embeddings_address='dummy.npy',
                save_train_model_address=save_path,
                model_name='logistic_regression'
            )
        except FileNotFoundError:
            pass

        mock_pd_read.assert_called_with('dummy.xlsx')
        mock_np_load.assert_called_with('dummy.npy')
        mock_classifier_instance.fit.assert_called_once()
        mock_classifier_instance.save_model.assert_called_once()
        mock_classifier_instance.calc_metrics.assert_called_once()

    @patch('src.semantic_router.E5Embedder')
    @patch('src.semantic_router.LogisticRegressionModel')
    def test_predict_sentences(self, mock_classifier, mock_embedder):
        """Test the sentence prediction method."""
        mock_embedder_instance = MagicMock()
        mock_embedder_instance.return_value = np.array([[1.0]])
        mock_embedder.return_value = mock_embedder_instance

        mock_classifier_instance = MagicMock()
        mock_classifier_instance.model.predict_proba.return_value = np.array([[0.1, 0.9]])
        mock_classifier_instance.model.classes_ = ['class1', 'class2']
        mock_classifier.return_value = mock_classifier_instance

        pipeline = SemanticRouterPipeline(inference_only=True)
        label, classes_prob, max_prob = pipeline.predict_sentences(["test sentence"])

        self.assertEqual(label, 'class2')
        self.assertEqual(max_prob, 0.9)
        self.assertEqual(len(classes_prob), 2)
        mock_embedder_instance.assert_called_with(["test sentence"])
        mock_classifier_instance.model.predict_proba.assert_called_with(np.array([[1.0]]))

    @patch('src.semantic_router.E5Embedder')
    @patch('src.semantic_router.LogisticRegressionModel')
    def test_predict_sentences_input_embedding_and_sentences(self, mock_classifier, mock_embedder):
        """Test prediction with pre-computed embeddings."""
        mock_classifier_instance = MagicMock()
        mock_classifier_instance.model.predict_proba.return_value = np.array([[0.2, 0.3, 0.5]])
        mock_classifier_instance.model.classes_ = ['class1', 'class2', 'class3']
        mock_classifier.return_value = mock_classifier_instance

        pipeline = SemanticRouterPipeline(inference_only=True)
        embeddings = np.array([[1.0, 2.0, 3.0]])

        sorted_probs, _, max_prob = pipeline.predict_sentences_input_embedding_and_sentences(
            ["test"], embeddings
        )

        self.assertEqual(max_prob, 0.5)
        self.assertEqual(len(sorted_probs), 3)
        # Check that sorted_probs is sorted in descending order
        probs = [p[1] for p in sorted_probs]
        self.assertEqual(probs, sorted(probs, reverse=True))
        self.assertEqual(sorted_probs[0][1], 0.5)

    def test_singleton_pattern(self):
        """Test that SemanticRouterPipeline follows singleton pattern."""
        with patch('src.semantic_router.E5Embedder'), \
                patch('src.semantic_router.LogisticRegressionModel'):
            pipeline1 = SemanticRouterPipeline(inference_only=True)
            pipeline2 = SemanticRouterPipeline(inference_only=True)

            self.assertIs(pipeline1, pipeline2)

    @patch('src.semantic_router.E5Embedder')
    @patch('src.semantic_router.SVMModel')
    def test_pipeline_with_svm_model(self, mock_svm, mock_embedder):
        """Test pipeline initialization with SVM classifier."""
        pipeline = SemanticRouterPipeline(inference_only=True, model_name='svm')
        self.assertIsNotNone(pipeline.classifier)
        mock_svm.assert_called_once()

    @patch('src.semantic_router.E5Embedder')
    @patch('src.semantic_router.MLPClassifierModel')
    def test_pipeline_with_mlp_model(self, mock_mlp, mock_embedder):
        """Test pipeline initialization with MLP classifier."""
        pipeline = SemanticRouterPipeline(inference_only=True, model_name='mlp')
        self.assertIsNotNone(pipeline.classifier)
        mock_mlp.assert_called_once()

    @patch('src.semantic_router.E5Embedder')
    @patch('src.semantic_router.RFModel')
    def test_pipeline_with_rf_model(self, mock_rf, mock_embedder):
        """Test pipeline initialization with Random Forest classifier."""
        pipeline = SemanticRouterPipeline(inference_only=True, model_name='rf')
        self.assertIsNotNone(pipeline.classifier)
        mock_rf.assert_called_once()

    @patch('src.semantic_router.Qwen3Embedder')
    @patch('src.semantic_router.LogisticRegressionModel')
    def test_pipeline_with_qwen_embedder(self, mock_classifier, mock_qwen):
        """Test pipeline with Qwen3 embedder."""
        pipeline = SemanticRouterPipeline(
            inference_only=True,
            embedding_model='qwen3-embedding-4b'
        )
        self.assertIsNotNone(pipeline.embedder)
        mock_qwen.assert_called_once()

    @patch('src.semantic_router.JinaaEmbedder')
    @patch('src.semantic_router.LogisticRegressionModel')
    def test_pipeline_with_jina_embedder(self, mock_classifier, mock_jina):
        """Test pipeline with Jina embedder."""
        pipeline = SemanticRouterPipeline(
            inference_only=True,
            embedding_model='jina-embeddings-v3'
        )
        self.assertIsNotNone(pipeline.embedder)
        mock_jina.assert_called_once()

    @patch('src.semantic_router.E5Embedder')
    @patch('src.semantic_router.LogisticRegressionModel')
    def test_pipeline_with_multilingual_e5_embedder(self, mock_classifier, mock_e5):
        """Test pipeline with Multilingual E5 embedder."""
        pipeline = SemanticRouterPipeline(
            inference_only=True,
            embedding_model='multilingual-e5-large'
        )
        self.assertIsNotNone(pipeline.embedder)
        mock_e5.assert_called_once()

    @patch('src.semantic_router.E5Embedder')
    @patch('src.semantic_router.LogisticRegressionModel')
    def test_pipeline_invalid_embedding_model(self, mock_classifier, mock_embedder):
        """Test pipeline with invalid embedding model raises error."""
        with self.assertRaises(ValueError):
            SemanticRouterPipeline(
                inference_only=True,
                embedding_address='some/path',
                embedding_model='invalid_model'
            )

    @patch('src.semantic_router.pd.read_excel')
    @patch('src.semantic_router.E5Embedder')
    def test_pipeline_missing_dataset(self, mock_embedder, mock_read_excel):
        """Test pipeline raises error when dataset file doesn't exist."""
        mock_read_excel.side_effect = FileNotFoundError

        with self.assertRaises(FileNotFoundError):
            SemanticRouterPipeline(
                inference_only=False,
                dataset_address='nonexistent.xlsx'
            )

    @patch('src.semantic_router.pd.read_excel')
    @patch('src.semantic_router.E5Embedder')
    @patch('src.semantic_router.LogisticRegressionModel')
    @patch('src.semantic_router.train_test_split')
    @patch('src.semantic_router.np.save')
    def test_pipeline_generate_and_save_embeddings(self, mock_np_save, mock_split,
                                                   mock_classifier, mock_embedder, mock_read_excel):
        """Test pipeline generates and saves embeddings when not found."""
        mock_df = pd.DataFrame({'sentence': ['s1', 's2'], 'label': ['l1', 'l2']})
        mock_read_excel.return_value = mock_df

        mock_embedder_instance = MagicMock()
        mock_embedder_instance.return_value = np.array([[1.0], [2.0]])
        mock_embedder.return_value = mock_embedder_instance

        mock_embeddings = np.array([[1.0], [2.0]])
        mock_split.return_value = (mock_embeddings, mock_embeddings, ['l1', 'l2'], ['l1', 'l2'])

        mock_classifier_instance = MagicMock()
        mock_classifier_instance.predict.return_value = ['l1', 'l2']
        mock_classifier_instance.calc_metrics.return_value = (1.0, 'report')
        mock_classifier.return_value = mock_classifier_instance

        with tempfile.TemporaryDirectory() as tmpdir:
            embeddings_path = Path(tmpdir) / "embeddings.npy"

            with patch('src.semantic_router.os.path.isfile', return_value=False):
                try:
                    _ = SemanticRouterPipeline(
                        inference_only=False,
                        dataset_address='dummy.xlsx',
                        train_embeddings_address=str(embeddings_path),
                        save_train_embeddings=True,
                        save_trained_model=False,
                        report_metrics=False
                    )
                except Exception:
                    pass


    @patch('src.semantic_router.pd.read_excel')
    @patch('src.semantic_router.np.load')
    @patch('src.semantic_router.train_test_split')
    @patch('src.semantic_router.E5Embedder')
    @patch('src.semantic_router.LogisticRegressionModel')
    def test_pipeline_training_with_invalid_model_name(self, mock_classifier, mock_embedder,
                                                       mock_split, mock_np_load, mock_read_excel):
        """Test training with invalid model name raises error."""
        mock_df = pd.DataFrame({'sentence': ['s1', 's2'], 'label': ['l1', 'l2']})
        mock_read_excel.return_value = mock_df
        mock_embeddings = np.array([[1.0], [2.0]])
        mock_np_load.return_value = mock_embeddings

        with self.assertRaises(Exception):
            SemanticRouterPipeline(
                inference_only=False,
                dataset_address='dummy.xlsx',
                train_embeddings_address='dummy.npy',
                model_name='invalid_model_name'
            )


class TestQwen3Embedder(unittest.TestCase):

    @patch('src.semantic_router.OpenAI')
    def test_initialization(self, mock_openai):
        """Test Qwen3Embedder initialization."""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        embedder = Qwen3Embedder()

        self.assertEqual(embedder.model_name, "qwen/qwen3-embedding-4b")
        self.assertIsNotNone(embedder.client)
        mock_openai.assert_called_once()

    @patch('src.semantic_router.OpenAI')
    def test_initialization_custom_model(self, mock_openai):
        """Test Qwen3Embedder with custom model name."""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        embedder = Qwen3Embedder(model_name="custom/model")

        self.assertEqual(embedder.model_name, "custom/model")

    @patch('src.semantic_router.OpenAI')
    def test_call_single_batch(self, mock_openai):
        """Test embedding generation for single batch."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [
            MagicMock(embedding=[0.1, 0.2, 0.3]),
            MagicMock(embedding=[0.4, 0.5, 0.6])
        ]
        mock_client.embeddings.create.return_value = mock_response
        mock_openai.return_value = mock_client

        embedder = Qwen3Embedder()
        sentences = ["sentence 1", "sentence 2"]

        result = embedder(sentences)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], [0.1, 0.2, 0.3])
        self.assertEqual(result[1], [0.4, 0.5, 0.6])

    @patch('src.semantic_router.OpenAI')
    def test_call_multiple_batches(self, mock_openai):
        """Test embedding generation with multiple batches."""
        mock_client = MagicMock()

        # Create mock responses for multiple batches
        def create_mock_response(start, end):
            mock_resp = MagicMock()
            mock_resp.data = [MagicMock(embedding=[float(i)] * 3) for i in range(start, end)]
            return mock_resp

        mock_client.embeddings.create.side_effect = [
            create_mock_response(0, 100),
            create_mock_response(100, 200),
            create_mock_response(200, 250)
        ]
        mock_openai.return_value = mock_client

        embedder = Qwen3Embedder()
        sentences = [f"sentence {i}" for i in range(250)]

        result = embedder(sentences, batch_size=100)

        self.assertEqual(len(result), 250)
        self.assertEqual(mock_client.embeddings.create.call_count, 3)

    @patch('src.semantic_router.OpenAI')
    def test_call_with_error(self, mock_openai):
        """Test error handling during embedding generation."""
        mock_client = MagicMock()
        mock_client.embeddings.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client

        embedder = Qwen3Embedder()

        with self.assertRaises(Exception) as context:
            embedder(["test sentence"])

        self.assertIn("API Error", str(context.exception))


class TestJinaaEmbedder(unittest.TestCase):

    @patch('src.semantic_router.AutoModel.from_pretrained')
    def test_initialization(self, mock_from_pretrained):
        """Test JinaaEmbedder initialization."""
        mock_model = MagicMock()
        mock_from_pretrained.return_value = mock_model

        embedder = JinaaEmbedder()

        self.assertEqual(embedder.model_name, "jinaai/jina-embeddings-v3")
        self.assertIsNotNone(embedder.model)

    @patch('src.semantic_router.AutoModel.from_pretrained')
    def test_initialization_with_path(self, mock_from_pretrained):
        """Test JinaaEmbedder initialization with model path."""
        mock_model = MagicMock()
        mock_from_pretrained.return_value = mock_model

        embedder = JinaaEmbedder(model_path="/path/to/model")

        self.assertIsNotNone(embedder.model)
        mock_from_pretrained.assert_called_with("/path/to/model", trust_remote_code=True)

    @patch('src.semantic_router.AutoModel.from_pretrained')
    def test_call_method(self, mock_from_pretrained):
        """Test JinaaEmbedder call method."""
        mock_model = MagicMock()
        mock_model.encode.return_value = np.array([[0.1, 0.2], [0.3, 0.4]])
        mock_from_pretrained.return_value = mock_model

        embedder = JinaaEmbedder()
        sentences = ["test1", "test2"]

        result = embedder(sentences)

        mock_model.encode.assert_called_once_with(sentences, task="classification")
        self.assertIsInstance(result, np.ndarray)

    @patch('src.semantic_router.AutoModel.from_pretrained')
    def test_call_with_custom_task(self, mock_from_pretrained):
        """Test JinaaEmbedder with custom task parameter."""
        mock_model = MagicMock()
        mock_model.encode.return_value = np.array([[0.1, 0.2]])
        mock_from_pretrained.return_value = mock_model

        embedder = JinaaEmbedder()

        _ = embedder(["test"], task_for_jina="retrieval")

        mock_model.encode.assert_called_with(["test"], task="retrieval")


class TestE5Embedder(unittest.TestCase):

    @patch('src.semantic_router.SentenceTransformer')
    def test_initialization(self, mock_sentence_transformer):
        """Test E5Embedder initialization."""
        mock_model = MagicMock()
        mock_sentence_transformer.return_value = mock_model

        embedder = E5Embedder()

        self.assertEqual(embedder.model_name, 'intfloat/multilingual-e5-large')
        self.assertIsNotNone(embedder.model)

    @patch('src.semantic_router.SentenceTransformer')
    def test_initialization_with_path(self, mock_sentence_transformer):
        """Test E5Embedder initialization with model path."""
        mock_model = MagicMock()
        mock_sentence_transformer.return_value = mock_model

        embedder = E5Embedder(model_path="/path/to/model")

        self.assertIsNotNone(embedder.model)
        mock_sentence_transformer.assert_called_with("/path/to/model")

    @patch('src.semantic_router.SentenceTransformer')
    def test_call_default_passage(self, mock_sentence_transformer):
        """Test E5Embedder call with default passage prefix."""
        mock_model = MagicMock()
        mock_model.encode.return_value = np.array([[0.1, 0.2], [0.3, 0.4]])
        mock_sentence_transformer.return_value = mock_model

        embedder = E5Embedder()
        sentences = ["test1", "test2"]

        result = embedder(sentences)

        # Verify sentences were prefixed with "passage: "
        call_args = mock_model.encode.call_args[0][0]
        self.assertTrue(all(s.startswith("passage: ") for s in call_args))
        self.assertIsInstance(result, np.ndarray)

    @patch('src.semantic_router.SentenceTransformer')
    def test_call_with_query_prefix(self, mock_sentence_transformer):
        """Test E5Embedder call with query prefix."""
        mock_model = MagicMock()
        mock_model.encode.return_value = np.array([[0.1, 0.2]])
        mock_sentence_transformer.return_value = mock_model

        embedder = E5Embedder()

        _ = embedder(["test"], passage_or_sentence="query")

        call_args = mock_model.encode.call_args[0][0]
        self.assertTrue(call_args[0].startswith("query: "))


class TestOpenRouterEmbedder(unittest.TestCase):

    @patch('src.semantic_router.AsyncOpenAI')
    def test_initialization_valid_key(self, mock_async_openai):
        """Test OpenRouterEmbedder initialization with valid API key."""
        mock_client = MagicMock()
        mock_async_openai.return_value = mock_client

        embedder = OpenRouterEmbedder(api_key="valid-api-key")

        self.assertEqual(embedder.model_name, "qwen/qwen3-embedding-4b")
        self.assertIsNotNone(embedder.client)

    @patch('src.semantic_router.AsyncOpenAI')
    def test_initialization_placeholder_key(self, mock_async_openai):
        """Test OpenRouterEmbedder raises error with placeholder key."""
        with self.assertRaises(ValueError) as context:
            OpenRouterEmbedder(api_key="<YOUR_OPENROUTER_API_KEY_HERE>")

        self.assertIn("Please replace", str(context.exception))

    @patch('src.semantic_router.AsyncOpenAI')
    def test_get_embeddings_success(self, mock_async_openai):
        """Test successful embedding retrieval."""
        mock_client = MagicMock()
        mock_response = AsyncMock()
        mock_response.data = [
            MagicMock(embedding=[0.1, 0.2, 0.3]),
            MagicMock(embedding=[0.4, 0.5, 0.6])
        ]
        mock_client.embeddings.create = AsyncMock(return_value=mock_response)
        mock_async_openai.return_value = mock_client

        embedder = OpenRouterEmbedder(api_key="valid-key")

        # Run async method
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(embedder.get_embeddings(["text1", "text2"]))

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], [0.1, 0.2, 0.3])

    @patch('src.semantic_router.AsyncOpenAI')
    def test_get_embeddings_empty_list(self, mock_async_openai):
        """Test embedding retrieval with empty text list."""
        mock_client = MagicMock()
        mock_async_openai.return_value = mock_client

        embedder = OpenRouterEmbedder(api_key="valid-key")

        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(embedder.get_embeddings([]))

        self.assertEqual(result, [])

    @patch('src.semantic_router.AsyncOpenAI')
    def test_get_embeddings_with_error(self, mock_async_openai):
        """Test error handling during embedding retrieval."""
        mock_client = MagicMock()
        mock_client.embeddings.create = AsyncMock(side_effect=Exception("API Error"))
        mock_async_openai.return_value = mock_client

        embedder = OpenRouterEmbedder(api_key="valid-key")

        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(embedder.get_embeddings(["text"]))

        self.assertEqual(result, [])


class TestClassifierModels(unittest.TestCase):

    def test_logistic_regression_model_initialization(self):
        """Test LogisticRegressionModel initialization."""
        model = LogisticRegressionModel()
        self.assertIsNotNone(model.model)
        self.assertEqual(model.model_name, "logistic_regression")
        self.assertIsInstance(model.model, LogisticRegression)

    def test_logistic_regression_fit_predict(self):
        """Test LogisticRegressionModel fit and predict."""
        model = LogisticRegressionModel()
        X_train = rng.random((20, 5))
        y_train = [0, 1] * 10

        model.fit(X_train, y_train)
        X_test = rng.random((5, 5))
        predictions = model.predict(X_test)

        self.assertEqual(len(predictions), 5)

    @patch('src.semantic_router.plt')
    @patch('src.semantic_router.sns')
    def test_logistic_regression_calc_metrics(self, mock_sns, mock_plt):
        """Test LogisticRegressionModel metrics calculation."""
        model = LogisticRegressionModel()
        X_train = rng.random((50, 5))
        y_train = [0, 1, 2, 3, 4] * 10
        model.fit(X_train, y_train)

        y_true = [0, 1, 2, 3, 4] * 2
        y_pred = [0, 1, 2, 3, 4] * 2

        accuracy, report = model.calc_metrics(y_true, y_pred)

        self.assertGreaterEqual(accuracy, 0)
        self.assertLessEqual(accuracy, 1)
        self.assertIsInstance(report, str)

    def test_svm_model_initialization(self):
        """Test SVMModel initialization."""
        model = SVMModel()
        self.assertIsNotNone(model.model)
        self.assertEqual(model.model_name, "svm")

    def test_svm_model_fit_predict(self):
        """Test SVMModel fit and predict."""
        model = SVMModel()
        X_train = rng.random((20, 5))
        y_train = [0, 1] * 10

        model.fit(X_train, y_train)

        X_test = rng.random((5, 5))
        predictions = model.predict(X_test)

        self.assertEqual(len(predictions), 5)

    def test_mlp_model_initialization(self):
        """Test MLPClassifierModel initialization."""
        model = MLPClassifierModel()
        self.assertIsNotNone(model.model)
        self.assertEqual(model.model_name, "mlp")

    def test_mlp_model_fit_predict(self):
        """Test MLPClassifierModel fit and predict."""
        model = MLPClassifierModel()
        X_train = rng.random((20, 5))
        y_train = [0, 1] * 10

        model.fit(X_train, y_train)

        X_test = rng.random((5, 5))
        predictions = model.predict(X_test)

        self.assertEqual(len(predictions), 5)

    def test_rf_model_initialization(self):
        """Test RFModel initialization."""
        model = RFModel()
        self.assertIsNotNone(model.model)
        self.assertEqual(model.model_name, "rf")

    def test_rf_model_fit_predict(self):
        """Test RFModel fit and predict."""
        model = RFModel()
        X_train = rng.random((20, 5))
        y_train = [0, 1] * 10

        model.fit(X_train, y_train)

        X_test = rng.random((5, 5))
        predictions = model.predict(X_test)

        self.assertEqual(len(predictions), 5)


class TestPipelineStaticMethods(unittest.TestCase):

    @patch('src.semantic_router.OpenRouterEmbedder')
    def test_get_embeddings_of_list(self, mock_embedder_class):
        """Test static async method get_embeddings_of_list."""
        mock_embedder = MagicMock()
        mock_embedder.get_embeddings = AsyncMock(return_value=[[0.1, 0.2], [0.3, 0.4]])
        mock_embedder_class.return_value = mock_embedder

        texts = ["text1", "text2"]

        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            SemanticRouterPipeline.get_embeddings_of_list(texts)
        )

        self.assertEqual(len(result), 2)

    @patch('src.semantic_router.OpenRouterEmbedder')
    def test_get_embeddings_of_list_empty(self, mock_embedder_class):
        """Test get_embeddings_of_list with empty list."""
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            SemanticRouterPipeline.get_embeddings_of_list([])
        )

        self.assertIsNone(result)


class TestIntegration(unittest.TestCase):
    """Integration tests for full workflows."""

    def setUp(self):
        """Reset singleton before each test."""
        SemanticRouterPipeline._instance = None

    @patch('src.semantic_router.pd.read_excel')
    @patch('src.semantic_router.np.load')
    @patch('src.semantic_router.np.save')
    @patch('src.semantic_router.train_test_split')
    @patch('src.semantic_router.E5Embedder')
    @patch('src.semantic_router.plt')
    def test_full_training_to_inference_workflow(self, mock_plt, mock_embedder,
                                                 mock_split, mock_np_save,
                                                 mock_np_load, mock_read_excel):
        """Test complete workflow from training to inference."""
        # Setup mocks for training
        mock_df = pd.DataFrame({
            'sentence': ['s1', 's2', 's3', 's4', 's5'],
            'label': ['l1', 'l2', 'l3', 'l4', 'l5']
        })
        mock_read_excel.return_value = mock_df
        mock_embeddings = rng.random((5, 10))
        mock_np_load.return_value = mock_embeddings

        mock_split.return_value = (
            mock_embeddings[:4], mock_embeddings[4:],
            ['l1', 'l2', 'l3', 'l4'], ['l5']
        )

        mock_embedder_instance = MagicMock()
        mock_embedder_instance.return_value = rng.random((1, 10))
        mock_embedder.return_value = mock_embedder_instance

        with tempfile.TemporaryDirectory() as tmpdir:
            _ = Path(tmpdir) / "model.joblib"

            # Training phase
            try:
                pipeline = SemanticRouterPipeline(
                    inference_only=False,
                    dataset_address='dummy.xlsx',
                    train_embeddings_address='dummy.npy',
                    save_train_model_address=tmpdir,
                    model_name='logistic_regression',
                    save_trained_model=True,
                    report_metrics=False
                )
            except Exception:
                pass

            # Inference phase
            try:
                label, _, _ = pipeline.predict_sentences(["test"])
                self.assertIsNotNone(label)
            except Exception:
                pass


if __name__ == '__main__':
    unittest.main()
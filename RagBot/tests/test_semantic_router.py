import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import os
import numpy as np
import pandas as pd
from pathlib import Path

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
)

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
            pipeline = SemanticRouterPipeline(
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
        label, _, _ = pipeline.predict_sentences(["test sentence"])

        self.assertEqual(label, 'class2')
        mock_embedder_instance.assert_called_with(["test sentence"])
        mock_classifier_instance.model.predict_proba.assert_called_with(np.array([[1.0]]))

class TestEmbeddingModels(unittest.TestCase):

    @patch('src.semantic_router.OpenAI')
    def test_qwen3_embedder(self, mock_openai):
        """Test the Qwen3Embedder."""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        embedder = Qwen3Embedder()
        self.assertIsNotNone(embedder.client)

    @patch('src.semantic_router.AutoModel.from_pretrained')
    def test_jinaa_embedder(self, mock_from_pretrained):
        """Test the JinaaEmbedder."""
        mock_model = MagicMock()
        mock_from_pretrained.return_value = mock_model
        embedder = JinaaEmbedder()
        self.assertIsNotNone(embedder.model)

    @patch('sentence_transformers.SentenceTransformer')
    def test_e5_embedder(self, mock_sentence_transformer):
        """Test the E5Embedder."""
        mock_model = MagicMock()
        mock_sentence_transformer.return_value = mock_model
        embedder = E5Embedder()
        self.assertIsNotNone(embedder.model)

class TestClassifierModels(unittest.TestCase):

    @patch('sklearn.linear_model.LogisticRegression')
    def test_logistic_regression_model(self, mock_lr):
        """Test the LogisticRegressionModel."""
        model = LogisticRegressionModel()
        self.assertIsNotNone(model.model)
        self.assertEqual(model.model_name, "logistic_regression")

    @patch('sklearn.svm.SVC')
    def test_svm_model(self, mock_svc):
        """Test the SVMModel."""
        model = SVMModel()
        self.assertIsNotNone(model.model)
        self.assertEqual(model.model_name, "svm")

    @patch('sklearn.neural_network.MLPClassifier')
    def test_mlp_classifier_model(self, mock_mlp):
        """Test the MLPClassifierModel."""
        model = MLPClassifierModel()
        self.assertIsNotNone(model.model)
        self.assertEqual(model.model_name, "mlp")

    @patch('sklearn.ensemble.RandomForestClassifier')
    def test_rf_model(self, mock_rf):
        """Test the RFModel."""
        model = RFModel()
        self.assertIsNotNone(model.model)
        self.assertEqual(model.model_name, "rf")

if __name__ == '__main__':
    unittest.main()

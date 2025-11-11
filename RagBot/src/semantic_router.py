from packaging.utils import InvalidName
from transformers import AutoTokenizer, AutoModel
from sentence_transformers import SentenceTransformer
import pandas as pd
import os
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import numpy as np
from .config import config 
from abc import ABC, abstractmethod
from pathlib import Path
from time import time
import logging

import matplotlib.pyplot as plt
import joblib
import seaborn as sns

from src.retriever import ModelManager

# Your task is to create a prompt to classify the input user query into the provided classes. The provided classes are at least two of the following types. Consider that this input prompt is targeted to classify for "همکاران سیستم" company, an Iranian company that focuses on creating softwares related to ERP systems. Users' questions should be about whether a question is in the system's manuals, or they want to  

# ["qa", "sql", "illegal", "irrelevant", "chitchat"]

# 1. Configure the logger
# This is the most basic setup. You do this once at the start of your application.
logging.basicConfig(
    level=logging.INFO,  # Set the lowest level of message to be recorded
    filename='app.log',   # Name of the file to save logs to
    filemode='w',         # 'w' for overwrite, 'a' for append
    format='%(asctime)s - %(levelname)s - %(message)s', # The format of the log message
    encoding="utf-8"
)
logger = logging.getLogger(__name__)
CLASS_NAMES = ['chitchat', 'illegal', 'irrelevant', 'sql', 'qa']
LIST_OF_VALID_MODEL_NAMES = ["logistic_regression", "svm", "mlp", "rf"]


# Add this adapter class after the imports section

class HuggingFaceEmbeddingAdapter:
    """Adapter to make ModelManager's HuggingFaceEmbeddings compatible with the existing interface"""
    def __init__(self, hf_embeddings):
        self.model = hf_embeddings
        self.model_name = "huggingface_embeddings_from_modelmanager"
        logger.info(f"Using HuggingFaceEmbeddings from ModelManager")
    
    def __call__(self, sentences, *args, **kwargs):
        """
        Makes HuggingFaceEmbeddings compatible with E5Embedder interface.
        Uses embed_documents for batch processing.
        """
        if not isinstance(sentences, list):
            sentences = [sentences]
        
        # Use embed_documents for batch processing
        embeddings = self.model.embed_documents(sentences)
        return np.array(embeddings)


class EmbeddingLoader(ABC):
    def __init__(self):
        self.__set_model_name__("embedding_name")

    @abstractmethod
    def __set_model_name__(self, model_name):
        self.model_name = model_name

    @abstractmethod
    def __load_model__(self, model_name=None, model_path=None):
        pass

    @abstractmethod
    def __call__(self, *args, **kwargs):
        pass


class JinaaEmbedder(EmbeddingLoader):
    def __init__(self, model_name="jinaai/jina-embeddings-v3", model_path=None):
        super().__init__()
        self.__set_model_name__(model_name)
        self.__load_model__(model_name=model_name, model_path=model_path)

    @abstractmethod
    def __set_model_name__(self, model_name):
        self.model_name = model_name

    def __load_model__(self, model_name="jinaai/jina-embeddings-v3", model_path=None):
        if model_path is None:
            self.model = AutoModel.from_pretrained(model_name, trust_remote_code=True)
        else:
            self.model = AutoModel.from_pretrained(model_path, trust_remote_code=True)

        logger.info(f"loaded {self.model_name} successfully!")

    def __call__(self, sentences, *args, **kwargs):
        return self.model.encode(sentences, task=kwargs.get("task_for_jina", "classification"))

class E5Embedder(EmbeddingLoader):
    def __init__(self, model_name='intfloat/multilingual-e5-large', model_path=None):
        super().__init__()
        self.__set_model_name__(model_name)
        self.__load_model__(model_name=model_name, model_path=model_path)

    def __set_model_name__(self, model_name):
        self.model_name = model_name

    def __load_model__(self, model_name='intfloat/multilingual-e5-large', model_path=None):
        if model_path is None:
            self.model = SentenceTransformer(model_name)
        else:
            self.model = SentenceTransformer(model_path)
        logger.info(f"loaded {self.model_name} successfully!")

    def __call__(self, sentences, *args, **kwargs):
        passage_or_sentence = kwargs.get("passage_or_sentence", "passage")
        sentences = [passage_or_sentence + ": " + w for w in sentences]
        embeddings = self.model.encode(sentences, normalize_embeddings=True)
        return embeddings

    @staticmethod
    def __average_pool__(last_hidden_states, attention_mask):
        last_hidden = last_hidden_states.masked_fill(~attention_mask[..., None].bool(), 0.0)
        return last_hidden.sum(dim=1) / attention_mask.sum(dim=1)[..., None]


class ClassifierModel(ABC):
    def __init__(self, address=None):
        self.__set_model_name__()
        self.__load_model__(address)

    @abstractmethod
    def __set_model_name__(self):
        self.model_name = "model_name"

    def __load_model__(self, address=None):
        if address is None:
            self.model = LogisticRegression()
        else:
            self.model = joblib.load(address)

    def save_model(self, address):
        # with open(address, "wb") as f:
        #     pickle.dump(self.model, f)
        joblib.dump(self.model, address)

    def fit(self, X_train, y_train):
        self.model.fit(X_train, y_train)

    def predict(self, X_test):
        return self.model.predict(X_test)

    def calc_metrics(self, y_true, y_pred):
        accuracy = accuracy_score(y_true, y_pred)
        report = classification_report(y_true, y_pred, target_names=CLASS_NAMES)
        cm = confusion_matrix(y_true, y_pred)
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                    xticklabels=CLASS_NAMES, yticklabels=CLASS_NAMES)
        plt.savefig(f"confusion_matrix_{self.model_name}.png")
        return accuracy, report


class LogisticRegressionModel(ClassifierModel):
    def __init__(self, address=None):
        super().__init__(address)

    def __set_model_name__(self):
        self.model_name = "logistic_regression"

    def __load_model__(self, address=None):
        if address is None:
            self.model = LogisticRegression()
        else:
            self.model = joblib.load(address)

class SVMModel(ClassifierModel):
    def __init__(self, address=None):
        super().__init__(address)

    def __set_model_name__(self):
        self.model_name = "svm"

    def __load_model__(self, address=None):
        if address is None:
            self.model = SVC(kernel='rbf', C=1.0, probability=True)
        else:
            self.model = joblib.load(address)

class MLPClassifierModel(ClassifierModel):
    def __init__(self, address=None):
        super().__init__(address)

    def __set_model_name__(self):
        self.model_name = "mlp"

    def __load_model__(self, address=None):
        if address is None:
            self.model = MLPClassifier(
                            hidden_layer_sizes=(100,),
                            activation='relu',
                            max_iter=500,
                            random_state=42
                        )
        else:
            self.model = joblib.load(address)

class RFModel(ClassifierModel):
    def __init__(self, address=None):
        super().__init__(address)

    def __set_model_name__(self):
        self.model_name = "rf"

    def __load_model__(self, address=None):
        if address is None:
            self.model = RandomForestClassifier(
                            n_estimators=100,
                            max_depth=3,
                            random_state=42
                        )
        else:
            self.model = joblib.load(address)


class SemanticRouterPipeline:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._initialize(**kwargs)
        return cls._instance

    def _initialize(self, inference_only=False, embedding_address=None, classifier_address=None, use_model_manager=True, **kwargs):
        self.__load_embedding_model(embedding_address, use_model_manager)
        self.__load_classifier_model(classifier_address, **kwargs)
        if not inference_only:
            self.__load__train_data__(**kwargs)
            self.__train_model__(**kwargs)

    def __load_embedding_model(self, address, use_model_manager=False):
        if use_model_manager:
            # Use the embedding model from ModelManager singleton
            model_manager = ModelManager()
            self.embedder = HuggingFaceEmbeddingAdapter(model_manager.embedding_model)
        elif address is not None and os.path.exists(address):
            self.embedder = E5Embedder(model_path=address)
        else:
            self.embedder = E5Embedder()

    def __load_classifier_model(self, classifier_address, **kwargs):
        if kwargs.get("model_name") is None or kwargs.get("model_name") == "logistic_regression":
            self.classifier = LogisticRegressionModel(classifier_address)
        elif kwargs.get("model_name") == "svm":
            self.classifier = SVMModel(classifier_address)
        elif kwargs.get("model_name") == "mlp":
            self.classifier = MLPClassifierModel(classifier_address)
        elif kwargs.get("model_name") == "rf":
            self.classifier = RFModel(classifier_address)
        else:
            NotImplementedError(f"unknown model name: {kwargs['model_name']}")

    def __load__train_data__(self, **kwargs):
        dataset_address = kwargs.get("dataset_address",
                                     (Path(__file__).parent / "resources" / "generated_questions" / "output.xlsx").as_posix())
        if dataset_address is None:
            logger.error("dataset_address is required")
            raise FileNotFoundError
        elif not os.path.exists(dataset_address):
            logger.error("dataset_address file doesn't exist")
            raise FileNotFoundError
        data = pd.read_excel(dataset_address)
        self.X = list(data["sentence"])
        self.y = list(data["label"])

    def __train_model__(self, **kwargs):
        model_name = kwargs.get("model_name", "logistic_regression")
        embeddings = self.__load_train_data_embeddings__(**kwargs)
        if model_name not in LIST_OF_VALID_MODEL_NAMES:
            logger.error("model_name should be one of {}".format(LIST_OF_VALID_MODEL_NAMES))
            raise InvalidName
        if model_name == "logistic_regression":
            self.classifier = LogisticRegressionModel(address=None)
        elif model_name == "svm":
            self.classifier = SVMModel(address=None)
        X_train, X_test, y_train, y_test = train_test_split(embeddings, self.y,
                                                            test_size=kwargs.get("test_size", 0.2), random_state=42)
        self.classifier.fit(X_train, y_train)
        if kwargs.get("save_trained_model", True):
            self.classifier.save_model(address=(Path(__file__).parent / "resources" / "models" / "classifiers" / (model_name + ".joblib")).as_posix())
        y_pred = self.classifier.predict(X_test)
        report_metrics = kwargs.get("report_metrics", True)
        if report_metrics:
            accuracy, report = self.classifier.calc_metrics(y_test, y_pred)
            logger.info(f"Accuracy of the model: {self.classifier.model_name} is: {accuracy}")
            logger.info(f"Report of the model: {self.classifier.model_name} is: {report}")
            with open((Path(__file__).parent / "resources" / "models" / "classifiers" /  f"report_of_{model_name}.txt").as_posix(),
                       "w", encoding="utf-8") as file:
                file.write(report)

    def __load_train_data_embeddings__(self, **kwargs):
        train_embeddings_address = kwargs.get("train_embeddings_address",
                                   (Path(__file__).parent / "resources" / "vectors" / "embeddings.npy").as_posix())
        if os.path.isfile(train_embeddings_address):
            embeddings = np.load(train_embeddings_address)
            logger.info(f"Loaded embeddings from {train_embeddings_address}")
        else:
            logger.info(f"No embeddings found in {train_embeddings_address}, providing embeddings for training data!")
            embeddings = self.embedder(self.X, passage_or_sentence= "passage")
            logger.info(f"Predictions done!")
            save_train_embeddings = kwargs.get("save_train_embeddings", True)
            if save_train_embeddings:
                logger.info(f"Saving embeddings to {train_embeddings_address}")
                np.save(train_embeddings_address, embeddings)
                logger.info(f"Saving embeddings to {train_embeddings_address} is done!")
        return embeddings

    def predict_sentences(self, sentences):
        t0 = time()
        label = self.classifier.predict(self.embedder(sentences))
        prob = self.classifier.model.predict_proba(self.embedder(sentences))
        classes = self.classifier.model.classes_
        classes_prob = list(zip(classes, prob[0]))
        t1 = time()
        logger.info(f"Prediction done in {t1 - t0} seconds")
        logger.info(f"The sentence: {sentences[0]} is classified as: {label}")
        return label, classes_prob, max(prob[0])

# if __name__ == '__main__':
#     # embedding_address = r"C:\Users\SoroushA\.cache\huggingface\hub\models--intfloat--multilingual-e5-large"
#     classifier_address = r"E:\semantic_router\resources\models\classifiers\svm.joblib"
#     semantic_router_object = SemanticRouterPipeline(inference_only=False, embedding_address=None,
#                                                     classifier_address=None,
#                                                     model_name="svm")
#     # semantic_router_object = SemanticRouterPipeline(inference_only=True, embedding_address=None,
#     #                                                 classifier_address=classifier_address,
#     #                                                 model_name="logistic_regression")
#     # semantic_router_object = SemanticRouterPipeline(inference_only=True, embedding_address=embedding_address,
#     #                                                 classifier_address=classifier_address,
#     #                                                 model_name="svm")
#     new_sentence = "برای ساخت سند حسابداری چه کنم؟"

#     semantic_router_object.predict_sentences([new_sentence])
#     # list[str] => ["qa", "sql", "illegal", "irrelevant", "chitchat"]



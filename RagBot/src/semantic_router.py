import logging
import os
from abc import ABC, abstractmethod
from pathlib import Path
from time import time
from typing import List
import asyncio

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from openai import AsyncOpenAI
from packaging.utils import InvalidName
from sentence_transformers import SentenceTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from transformers import AutoModel
from openai import OpenAI
from tqdm import tqdm

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

YOUR_SITE_URL = "<YOUR_SITE_URL>"
YOUR_SITE_NAME = "<YOUR_SITE_NAME>"
MODEL_NAME = "qwen/qwen3-embedding-4b"
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "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")


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


class Qwen3Embedder(EmbeddingLoader):
    def __init__(self, model_name="qwen/qwen3-embedding-4b", model_path=None):
        super().__init__()
        self.__set_model_name__(model_name)
        self.__load_model__(model_name=model_name, model_path=model_path)

    def __set_model_name__(self, model_name):
        self.model_name = model_name

    def __load_model__(self, model_name="qwen/qwen3-embedding-4b", model_path=None):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY,
        )

        logger.info(f"client set {self.model_name} successfully!")

    # def __call__(self, sentences, *args, **kwargs):
    #     embedding = self.client.embeddings.create(
    #         model="qwen/qwen3-embedding-4b",
    #         # input="Your text string goes here",
    #         input= sentences, # batch embeddings also supported!
    #         encoding_format="float"
    #     )
    #     embeddings = [w.embedding for w in embedding.data]
    #     return embeddings

    def __call__(self, sentences, batch_size=100, *args, **kwargs):
        """
        Generates embeddings in batches to avoid API payload limits.
        """
        all_embeddings = []
        total_sentences = len(sentences)

        logger.info(f"Starting embedding process for {total_sentences} sentences in batches of {batch_size}...")

        # Loop through the sentences in steps of 'batch_size'
        for i in tqdm(range(0, total_sentences, batch_size)):
            # Create the slice for the current batch
            batch = sentences[i: i + batch_size]

            try:
                embedding_response = self.client.embeddings.create(
                    model="qwen/qwen3-embedding-4b",
                    input=batch,
                    encoding_format="float"
                )

                # Extract embeddings from response
                batch_embeddings = [w.embedding for w in embedding_response.data]

                # Add to our main list
                all_embeddings.extend(batch_embeddings)

                logger.info(f"Processed batch {i} to {i + len(batch)} (Total: {len(all_embeddings)})")

                # Optional: specific sleep to avoid hitting Rate Limits (429 Errors)
                # time.sleep(0.2)

            except Exception as e:
                logger.error(f"Error processing batch starting at index {i}: {e}")
                raise e  # Stop execution if a batch fails, to avoid data misalignment

        return all_embeddings

class JinaaEmbedder(EmbeddingLoader):
    def __init__(self, model_name="jinaai/jina-embeddings-v3", model_path=None):
        super().__init__()
        self.__set_model_name__(model_name)
        self.__load_model__(model_name=model_name, model_path=model_path)

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
                            # alpha=0.001,
                            activation='relu',
                            max_iter=2000,
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


class OpenRouterEmbedder:
    """
    A class to asynchronously fetch embeddings from OpenRouter.
    """

    def __init__(
            self,
            api_key: str,
            model_name: str = MODEL_NAME,
            site_url: str = YOUR_SITE_URL,
            site_name: str = YOUR_SITE_NAME
    ):
        """
        Initializes the embedder with API key and optional parameters.
        """
        if api_key == "<YOUR_OPENROUTER_API_KEY_HERE>":
            raise ValueError(
                "Error: Please replace '<YOUR_OPENROUTER_API_KEY_HERE>' with your actual OpenRouter API key or set the environment variable.")

        print(f"Initializing AsyncOpenAI client for OpenRouter...")
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        self.model_name = model_name
        self.custom_headers = {
            "HTTP-Referer": site_url,
            "X-Title": site_name,
        }

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Asynchronously fetches embeddings for a list of texts.
        """
        if not texts:
            print("No texts provided to embed.")
            return []

        print(f"Requesting embeddings for {len(texts)} texts using model: {self.model_name}...")

        try:
            embedding_response = await self.client.embeddings.create(
                extra_headers=self.custom_headers,
                model=self.model_name,
                input=texts,  # Pass the list of texts directly
                encoding_format="float"
            )

            print("Successfully received embedding response.")

            # Extract the embedding data
            embeddings = [item.embedding for item in embedding_response.data]
            return embeddings

        except Exception as e:
            print(f"An error occurred while fetching embeddings: {e}")
            return []
        finally:
            # Modern clients often manage connections automatically.
            # Add await self.client.close() if your version requires it.
            pass


class SemanticRouterPipeline:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            # cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance = super().__new__(cls)
            cls._instance._initialize(**kwargs)
        return cls._instance

    def _initialize(self, inference_only=False, embedding_address=None, classifier_address=None, **kwargs):
        self.__load_embedding_model(embedding_address, model=kwargs.get("embedding_model"))
        self.__load_classifier_model(classifier_address, **kwargs)
        if not inference_only:
            self.__load__train_data__(**kwargs)
            self.__train_model__(**kwargs)

    @staticmethod
    async def get_embeddings_of_list(texts_to_embed: List[str]):
        """
        get_embeddings_of_list asynchronous function to run the embedding request.

        :param texts_to_embed: A list of text strings to embed.
        """
        if not texts_to_embed:
            print("No texts provided to embed. Exiting.")
            return

        print("Starting asynchronous embedding process...")

        try:
            # Create an instance of the embedder
            embedder = OpenRouterEmbedder(api_key=OPENROUTER_API_KEY)

            # Get embeddings using the class method
            embeddings = await embedder.get_embeddings(texts_to_embed)

            if embeddings:
                print(f"\nSuccessfully retrieved {len(embeddings)} embeddings.")

                # Print info about each embedding
                for i, (text, emb) in enumerate(zip(texts_to_embed, embeddings)):
                    print("\n---")
                    print(f"Text {i + 1}: \"{text}\"")
                    # Print the first 5 dimensions and the total length
                    print(f"Embedding (first 5 dims): {emb[:5]}...")
                    print(f"Total dimensions: {len(emb)}")
                    print("---")
                return embeddings
            else:
                print("\nFailed to retrieve embeddings.")

        except ValueError as e:
            print(e)  # Print the API key error from the constructor
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def __load_embedding_model(self, address, model=None):
        if (address is not None and os.path.exists(address)) or model is not None:
            if model == "multilingual-e5-large":
                self.embedder = E5Embedder(model_path=address)
            elif model == "jina-embeddings-v3":
                self.embedder = JinaaEmbedder(model_path=address)
            elif model == "qwen3-embedding-4b":
                self.embedder = Qwen3Embedder(model_path=address)
            else:
                raise ValueError()
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
        elif kwargs.get("model_name") == "mlp":
            self.classifier = MLPClassifierModel(address=None)
        elif kwargs.get("model_name") == "rf":
            self.classifier = RFModel(address=None)
        X_train, X_test, y_train, y_test = train_test_split(embeddings, self.y,
                                                            test_size=kwargs.get("test_size", 0.2), random_state=42)
        self.classifier.fit(X_train, y_train)
        save_train_model_address = kwargs.get("save_train_model_address", (Path(__file__).parent / "resources" / "models" / "classifiers").as_posix())
        if kwargs.get("save_trained_model", True):
            self.classifier.save_model(address=(Path(save_train_model_address) / (model_name + ".joblib")).as_posix())
        y_pred = self.classifier.predict(X_test)
        report_metrics = kwargs.get("report_metrics", True)
        if report_metrics:
            accuracy, report = self.classifier.calc_metrics(y_test, y_pred)
            logger.info(f"Accuracy of the model: {self.classifier.model_name} is: {accuracy}")
            logger.info(f"Report of the model: {self.classifier.model_name} is: {report}")
            with open((Path(save_train_model_address) /  f"report_of_{model_name}.txt").as_posix(),
                       "w", encoding="utf-8") as file:
                file.write(report)

    def __load_train_data_embeddings__(self, **kwargs):
        train_embeddings_address = kwargs.get("train_embeddings_address",
                                   (Path(__file__).parent / "resources" / "vectors_v2" / "embeddings.npy").as_posix())
        if os.path.isfile(train_embeddings_address):
            embeddings = np.load(train_embeddings_address)
            logger.info(f"Loaded embeddings from {train_embeddings_address}")
        else:
            logger.info(f"No embeddings found in {train_embeddings_address}, providing embeddings for training data!")
            # embeddings = asyncio.run(self.get_embeddings_of_list(self.X[:10]))
            # embeddings = self.get_embeddings_of_list(self.X[:10])
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
        X = self.embedder(sentences)
        t2 = time()
        print("embedder time: %s" %(t2 - t0))
        prob = self.classifier.model.predict_proba(X)
        t3 = time()
        print("predict_proba_time: %s" % (t3 - t2))
        classes = self.classifier.model.classes_
        label = classes[np.argmax(prob[0])]
        # label = self.classifier.predict(X)
        classes_prob = list(zip(classes, prob[0]))
        t1 = time()
        logger.info(f"Prediction done in {t1 - t0} seconds")
        logger.info(f"The sentence: {sentences[0]} is classified as: {label}")
        return label, classes_prob, max(prob[0])

    def predict_sentences_input_embedding_and_sentences(self, sentences, sentences_vectors):
        t0 = time()
        # label = self.classifier.predict(sentences_vectors)
        prob = self.classifier.model.predict_proba(sentences_vectors)
        classes = self.classifier.model.classes_
        classes_prob = list(zip(classes, prob[0]))
        label = classes[np.argmax(prob[0])]
        t1 = time()
        logger.info(f"Prediction done in {t1 - t0} seconds")
        logger.info(f"The sentence: {sentences[0]} is classified as: {label}")
        return label, classes_prob, max(prob[0])

if __name__ == '__main__':
    dataset_address = (Path(__file__).parent / "resources" / "generated_questions" / "output.xlsx").as_posix()
    embedding_address = r"E:\workspace-semantic-router\da-semantic-router\models--intfloat--multilingual-e5-large"
    # classifier_address = r"E:\semantic_router\resources\models\classifiers_v2\mlp.joblib"
    semantic_router_object = SemanticRouterPipeline(inference_only=False,
                                                    train_embeddings_address=(Path(__file__).parent / "resources" / "vectors_qwen3_embedding_4b" / "embeddings.npy").as_posix(),
                                                    embedding_address=embedding_address,
                                                    classifier_address=None,
                                                    model_name="mlp",
                                                    # model_name="logistic_regression",
                                                    embedding_model="qwen3-embedding-4b",
                                                    save_train_model_address=(Path(__file__).parent / "resources" / "models" / "classifiers_qwen3_embedding_4b").as_posix())
    # total_time = 0
    # for i in range(10):
    #     t0 = time()
        # semantic_router_object = SemanticRouterPipeline(inference_only=False, embedding_address=embedding_address,
        #                                                 classifier_address=classifier_address,
        #                                                 model_name="mlp",
        #                                                 dataset_address=dataset_address)
        # semantic_router_object = SemanticRouterPipeline(inference_only=True, embedding_address=None,
        #                                                 classifier_address=classifier_address,
        #                                                 model_name="logistic_regression")
        # semantic_router_object = SemanticRouterPipeline(inference_only=False, embedding_address=embedding_address,
        #                                                 classifier_address=classifier_address,
        #                                                 model_name="mlp")
        # t1 = time()
        # print("init time: ", t1 - t0)
        # new_sentence = "برای ساخت سند حسابداری چه کنم؟"
        # semantic_router_object.predict_sentences([new_sentence])
        # t2 = time()
        # print("predict time: ", t2 - t1)

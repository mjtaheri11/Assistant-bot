# data_loader.py
import pandas as pd
from typing import List, Dict

def load_evaluation_data(file_path: str) -> List:
    """
    Loads evaluation data from a CSV file into a list of dictionaries.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        List: A list where each dictionary represents a row from the CSV.
    """
    try:
        df = pd.read_csv(file_path)
        # Ensure required columns exist
        required_columns = ['input', 'expected_output']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"CSV file must contain the following columns: {required_columns}")
        
        # Convert DataFrame to a list of dictionaries
        return df.to_dict('records')
    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
        return
    except Exception as e:
        print(f"An error occurred while reading the CSV file: {e}")
        return
    
# custom_model.py
import httpx
from deepeval.models.base_model import DeepEvalBaseLLM
from typing import Optional

class CustomLLM(DeepEvalBaseLLM):
    """
    A custom wrapper for any OpenAI-compatible LLM API.
    This class allows DeepEval to use a custom model as the 'judge' for its metrics.
    """
    def __init__(self, model: str, base_url: str, api_key: Optional[str] = None):
        if not base_url:
            raise ValueError("base_url must be provided for CustomLLM")
        self.model = model
        self.base_url = base_url
        self.api_key = api_key
        # Ensure the base URL ends with a slash
        if not self.base_url.endswith('/'):
            self.base_url += '/'

    def load_model(self):
        # This method is required by the DeepEvalBaseLLM interface.
        # It can be used to load a model into memory, but for API-based models,
        # we simply return the model name.
        return self.model

    def generate(self, prompt: str) -> str:
        """
        Synchronously generate a response from the custom LLM.
        """
        headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False
        }

        try:
            with httpx.Client() as client:
                response = client.post(
                    f"{self.base_url}chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=60.0
                )
                response.raise_for_status()
                return response.json()["choices"]["message"]["content"]
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
            return f"Error: Failed to get response from model. Status: {e.response.status_code}"
        except Exception as e:
            print(f"An unexpected error occurred during API call: {e}")
            return "Error: An unexpected error occurred."

    async def a_generate(self, prompt: str) -> str:
        """
        Asynchronously generate a response from the custom LLM.
        """
        headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=60.0
                )
                response.raise_for_status()
                return response.json()["choices"]["message"]["content"]
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
            return f"Error: Failed to get response from model. Status: {e.response.status_code}"
        except Exception as e:
            print(f"An unexpected error occurred during API call: {e}")
            return "Error: An unexpected error occurred."

    def get_model_name(self) -> str:
        """
        Returns the model name.
        """
        return self.model
    
    
# metrics_suite.py
from deepeval.metrics import (
    FaithfulnessMetric,
    AnswerRelevancyMetric,
    ContextualRecallMetric,
    ContextualPrecisionMetric,
    ContextualRelevancyMetric
)

def get_rag_evaluation_suite(custom_llm: CustomLLM):
    """
    Initializes and returns a list of configured RAG evaluation metrics.
    
    Args:
        custom_llm (CustomLLM): The custom LLM instance to be used as the judge.
        
    Returns:
        list: A list of DeepEval metric instances.
    """
    # Generator-focused metrics
    faithfulness_metric = FaithfulnessMetric(
        threshold=0.7,
        model=custom_llm,
        include_reason=True  # Provides a qualitative reason for the score
    )
    
    answer_relevancy_metric = AnswerRelevancyMetric(
        threshold=0.7,
        model=custom_llm,
        include_reason=True
    )
    
    # Retriever-focused metrics
    contextual_recall_metric = ContextualRecallMetric(
        threshold=0.7,
        model=custom_llm,
        include_reason=True
    )
    
    contextual_precision_metric = ContextualPrecisionMetric(
        threshold=0.7,
        model=custom_llm,
        include_reason=True
    )
    
    contextual_relevancy_metric = ContextualRelevancyMetric(
        threshold=0.7,
        model=custom_llm,
        include_reason=True
    )
    
    return [
        faithfulness_metric,
        answer_relevancy_metric,
        contextual_recall_metric,
        contextual_precision_metric,
        contextual_relevancy_metric
    ]
    
# run_evaluation.py
import os
import asyncio
from dotenv import load_dotenv
from typing import List, Dict, Tuple

from deepeval import evaluate
from deepeval.test_case import LLMTestCase

# A placeholder for the actual RAG chatbot application
def run_rag_chatbot(query: str) -> Tuple[str, List[str]]:
    """
    Simulates a call to the RAG chatbot.
    In a real application, this would invoke the RAG chain and return
    the generated answer and the retrieved context documents.
    """
    print(f"INFO: Querying RAG chatbot with: '{query}'")
    # Dummy response for demonstration
    if "France" in query:
        actual_output = "Paris is the capital and most populous city of France."
        retrieval_context = ""
    elif "Mockingbird" in query:
        actual_output = "Harper Lee is the author of the novel 'To Kill a Mockingbird'."
        retrieval_context = ""
    else:
        actual_output = "I'm sorry, I don't have information on that topic."
        retrieval_context = ["General knowledge document."]
        
    print(f"INFO: RAG chatbot returned output and context.")
    return actual_output, retrieval_context

async def main():
    """
    Main function to orchestrate the RAG evaluation pipeline.
    """
    # 1. Setup: Load environment variables and initialize the custom model
    load_dotenv()
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_API_BASE")
    model_name = os.getenv("LLM_MODEL_NAME")

    if not base_url or not model_name:
        print("Error: CUSTOM_LLM_BASE_URL and CUSTOM_LLM_MODEL_NAME must be set in.env file.")
        return

    print("--- Initializing Custom LLM for Evaluation Judge ---")
    custom_llm_judge = CustomLLM(model=model_name, base_url=base_url, api_key=api_key)
    print(f"Judge Model: {custom_llm_judge.get_model_name()} at {custom_llm_judge.base_url}")
    import pdb
    pdb.set_trace()

    # 2. Data Loading: Load the evaluation dataset from the local CSV
    print("\n--- Loading Evaluation Dataset ---")
    dataset_path = "evaluation_dataset.csv"
    evaluation_data = load_evaluation_data(dataset_path)
    if not evaluation_data:
        print("Evaluation cannot proceed without data.")
        return
    print(f"Loaded {len(evaluation_data)} test case(s) from {dataset_path}")

    # 3. Test Case Generation: Create LLMTestCase objects dynamically
    print("\n--- Generating Test Cases from RAG Chatbot ---")
    test_cases: List = [""]
    for item in evaluation_data:
        # Get fresh output from the RAG application for each input
        actual_output, retrieval_context = run_rag_chatbot(item['input'])
        
        test_case = LLMTestCase(
            input=item['input'],
            actual_output=actual_output,
            expected_output=item['expected_output'],
            retrieval_context=retrieval_context
        )
        test_cases.append(test_case)
    print(f"Successfully generated {len(test_cases)} LLMTestCase objects.")

    # 4. Metric Suite Initialization
    print("\n--- Initializing RAG Evaluation Metric Suite ---")
    metrics = get_rag_evaluation_suite(custom_llm_judge)
    print(f"Initialized {len(metrics)} metrics for evaluation.")

    # 5. Execution: Run the evaluation
    print("\n--- Starting DeepEval Evaluation ---")
    # The evaluate function will run all metrics on all test cases.
    # It handles asynchronous execution internally for performance.
    results = evaluate(test_cases=test_cases, metrics=metrics)
    print("--- Evaluation Complete ---")

    # 6. Reporting: Display the results
    print("\n--- Evaluation Results ---")
    # The 'results' object is a list of TestResult objects.
    for test_result in results:
        print(f"\n===== Test Case Input: {test_result.input} =====")
        print(f"  Overall Status: {'PASSED' if test_result.success else 'FAILED'}")
        for metric_result in test_result.metrics:
            print(f"  - Metric: {metric_result.metric}")
            print(f"    Score: {metric_result.score:.4f}")
            print(f"    Status: {'PASSED' if metric_result.success else 'FAILED'} (Threshold: {metric_result.threshold})")
            if metric_result.reason:
                print(f"    Reason: {metric_result.reason.strip()}")

if __name__ == "__main__":
    asyncio.run(main())
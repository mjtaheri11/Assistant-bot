# data_loader.py
import pandas as pd
from typing import List, Dict


BASE_URL = "http://0.0.0.0:8689" # "http://172.27.0.6:8686" #



# result_exporter.py
import json
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
import os

class ResultExporter:
    """
    Handles exporting evaluation results to various file formats.
    """
    
    def __init__(self, output_dir: str = "./evaluation_results"):
        """
        Initialize the ResultExporter.
        
        Args:
            output_dir: Directory to save results
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.timestamp_readable = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def extract_metric_data(self, metric_result) -> Dict[str, Any]:
        """
        Extract metric data from various possible attribute names.
        """
        return {
            'metric_name': getattr(metric_result, 'metric', getattr(metric_result, 'name', 'Unknown')),
            'score': getattr(metric_result, 'score', None),
            'success': getattr(metric_result, 'success', False),
            'threshold': getattr(metric_result, 'threshold', None),
            'reason': getattr(metric_result, 'reason', '').strip()
        }
    
    def prepare_results_data(self, test_cases: List, test_results: List) -> List[Dict]:
        """
        Prepare evaluation results for export.
        
        Args:
            test_cases: List of LLMTestCase objects
            test_results: List of test results from DeepEval
            
        Returns:
            List of dictionaries containing structured results
        """
        results_data = []
        
        for i, (test_case, test_result) in enumerate(zip(test_cases, test_results)):
            base_result = {
                'test_case_id': i + 1,
                'input': test_case.input,
                'expected_output': test_case.expected_output,
                'actual_output': test_case.actual_output,
                'overall_success': test_result.success if hasattr(test_result, 'success') else False,
                'retrieval_context': '\n---\n'.join(test_case.retrieval_context) if test_case.retrieval_context else ''
            }
            
            # Extract metrics data
            metrics_attr = None
            if hasattr(test_result, 'metrics_data'):
                metrics_attr = test_result.metrics_data
            elif hasattr(test_result, 'metrics'):
                metrics_attr = test_result.metrics
            elif hasattr(test_result, 'metric_results'):
                metrics_attr = test_result.metric_results
            
            if metrics_attr:
                for metric_data in metrics_attr:
                    metric_info = self.extract_metric_data(metric_data)
                    # Add each metric as columns
                    metric_name = metric_info['metric_name'].replace(' ', '_').lower()
                    base_result[f'{metric_name}_score'] = metric_info['score']
                    base_result[f'{metric_name}_success'] = metric_info['success']
                    base_result[f'{metric_name}_threshold'] = metric_info['threshold']
                    base_result[f'{metric_name}_reason'] = metric_info['reason']
            
            results_data.append(base_result)
        
        return results_data
    
    def export_to_csv(self, results_data: List[Dict], filename_suffix: str = "") -> str:
        """
        Export results to CSV file.
        
        Args:
            results_data: List of result dictionaries
            filename_suffix: Optional suffix for filename
            
        Returns:
            Path to the created CSV file
        """
        filename = f"evaluation_results_{self.timestamp}{filename_suffix}.csv"
        filepath = os.path.join(self.output_dir, filename)
        
        df = pd.DataFrame(results_data)
        
        # Reorder columns for better readability
        priority_cols = ['test_case_id', 'input', 'expected_output', 'actual_output', 'overall_success']
        other_cols = [col for col in df.columns if col not in priority_cols]
        df = df[priority_cols + other_cols]
        
        df.to_csv(filepath, index=False)
        return filepath
    
    def export_to_json(self, test_cases: List, test_results: List, 
                      evaluation_metadata: Dict = None, filename_suffix: str = "") -> str:
        """
        Export results to JSON file with full detail preservation.
        
        Args:
            test_cases: List of LLMTestCase objects
            test_results: List of test results from DeepEval
            evaluation_metadata: Optional metadata about the evaluation
            filename_suffix: Optional suffix for filename
            
        Returns:
            Path to the created JSON file
        """
        filename = f"evaluation_results_{self.timestamp}{filename_suffix}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        json_data = {
            'evaluation_timestamp': self.timestamp,
            'metadata': evaluation_metadata or {},
            'summary': {
                'total_test_cases': len(test_cases),
                'passed': sum(1 for r in test_results if getattr(r, 'success', False)),
                'failed': sum(1 for r in test_results if not getattr(r, 'success', True))
            },
            'test_results': []
        }
        
        for i, (test_case, test_result) in enumerate(zip(test_cases, test_results)):
            test_data = {
                'test_case_id': i + 1,
                'input': test_case.input,
                'expected_output': test_case.expected_output,
                'actual_output': test_case.actual_output,
                'retrieval_context': test_case.retrieval_context if test_case.retrieval_context else [],
                'overall_success': getattr(test_result, 'success', False),
                'metrics': []
            }
            
            # Extract metrics
            metrics_attr = None
            if hasattr(test_result, 'metrics_data'):
                metrics_attr = test_result.metrics_data
            elif hasattr(test_result, 'metrics'):
                metrics_attr = test_result.metrics
            elif hasattr(test_result, 'metric_results'):
                metrics_attr = test_result.metric_results
            
            if metrics_attr:
                for metric_data in metrics_attr:
                    metric_info = self.extract_metric_data(metric_data)
                    test_data['metrics'].append(metric_info)
            
            json_data['test_results'].append(test_data)
        
        # Calculate aggregate metrics
        if json_data['test_results']:
            json_data['summary']['success_rate'] = (
                json_data['summary']['passed'] / json_data['summary']['total_test_cases']
            )
            
            # Aggregate metric scores
            metric_aggregates = {}
            for result in json_data['test_results']:
                for metric in result['metrics']:
                    name = metric['metric_name']
                    if name not in metric_aggregates:
                        metric_aggregates[name] = {
                            'scores': [],
                            'successes': 0,
                            'total': 0
                        }
                    if metric['score'] is not None:
                        metric_aggregates[name]['scores'].append(metric['score'])
                    metric_aggregates[name]['successes'] += 1 if metric['success'] else 0
                    metric_aggregates[name]['total'] += 1
            
            # Calculate averages
            for metric_name, data in metric_aggregates.items():
                if data['scores']:
                    data['average_score'] = sum(data['scores']) / len(data['scores'])
                    data['success_rate'] = data['successes'] / data['total'] if data['total'] > 0 else 0
                    del data['scores']  # Remove raw scores from summary
            
            json_data['summary']['metric_aggregates'] = metric_aggregates
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def export_to_markdown(self, test_cases: List, test_results: List,
                          evaluation_metadata: Dict = None, filename_suffix: str = "") -> str:
        """
        Export results to a well-formatted Markdown file.
        
        Args:
            test_cases: List of LLMTestCase objects
            test_results: List of test results from DeepEval
            evaluation_metadata: Optional metadata about the evaluation
            filename_suffix: Optional suffix for filename
            
        Returns:
            Path to the created Markdown file
        """
        filename = f"evaluation_report_{self.timestamp}{filename_suffix}.md"
        filepath = os.path.join(self.output_dir, filename)
        
        # Initialize markdown content
        md_lines = []
        
        # Header
        md_lines.append("# RAG System Evaluation Report")
        md_lines.append(f"\n**Generated on:** {self.timestamp_readable}")
        md_lines.append("")
        
        # Table of Contents
        md_lines.append("## Table of Contents")
        md_lines.append("1. [Executive Summary](#executive-summary)")
        md_lines.append("2. [Configuration](#configuration)")
        md_lines.append("3. [Overall Performance](#overall-performance)")
        md_lines.append("4. [Metric Analysis](#metric-analysis)")
        md_lines.append("5. [Detailed Test Results](#detailed-test-results)")
        md_lines.append("6. [Recommendations](#recommendations)")
        md_lines.append("")
        
        # Executive Summary
        md_lines.append("## Executive Summary")
        md_lines.append("")
        
        total_cases = len(test_cases)
        passed_cases = sum(1 for r in test_results if getattr(r, 'success', False))
        failed_cases = total_cases - passed_cases
        success_rate = (passed_cases / total_cases * 100) if total_cases > 0 else 0
        
        md_lines.append(f"This evaluation report summarizes the performance of the RAG system across {total_cases} test case(s).")
        md_lines.append("")
        
        # Quick stats box
        md_lines.append("### Quick Stats")
        md_lines.append("")
        md_lines.append("| Metric | Value |")
        md_lines.append("|--------|-------|")
        md_lines.append(f"| **Total Test Cases** | {total_cases} |")
        md_lines.append(f"| **Passed** | {passed_cases} ✅ |")
        md_lines.append(f"| **Failed** | {failed_cases} ❌ |")
        md_lines.append(f"| **Success Rate** | {success_rate:.1f}% |")
        md_lines.append("")
        
        # Configuration
        md_lines.append("## Configuration")
        md_lines.append("")
        if evaluation_metadata:
            md_lines.append("### Evaluation Settings")
            md_lines.append("")
            md_lines.append("| Parameter | Value |")
            md_lines.append("|-----------|-------|")
            for key, value in evaluation_metadata.items():
                if key != 'metrics_used':
                    if isinstance(value, list):
                        value = ', '.join(str(v) for v in value)
                    md_lines.append(f"| **{key.replace('_', ' ').title()}** | `{value}` |")
            md_lines.append("")
            
            if 'metrics_used' in evaluation_metadata:
                md_lines.append("### Metrics Used")
                md_lines.append("")
                for metric in evaluation_metadata['metrics_used']:
                    md_lines.append(f"- `{metric}`")
                md_lines.append("")
        
        # Overall Performance
        md_lines.append("## Overall Performance")
        md_lines.append("")
        
        # Collect all metrics data
        all_metrics = {}
        for test_result in test_results:
            metrics_attr = None
            if hasattr(test_result, 'metrics_data'):
                metrics_attr = test_result.metrics_data
            elif hasattr(test_result, 'metrics'):
                metrics_attr = test_result.metrics
            elif hasattr(test_result, 'metric_results'):
                metrics_attr = test_result.metric_results
            
            if metrics_attr:
                for metric_data in metrics_attr:
                    metric_info = self.extract_metric_data(metric_data)
                    name = metric_info['metric_name']
                    if name not in all_metrics:
                        all_metrics[name] = {
                            'scores': [],
                            'successes': 0,
                            'total': 0,
                            'threshold': metric_info['threshold']
                        }
                    if metric_info['score'] is not None:
                        all_metrics[name]['scores'].append(metric_info['score'])
                    all_metrics[name]['successes'] += 1 if metric_info['success'] else 0
                    all_metrics[name]['total'] += 1
        
        # Performance by metric table
        if all_metrics:
            md_lines.append("### Performance by Metric")
            md_lines.append("")
            md_lines.append("| Metric | Average Score | Success Rate | Threshold | Status |")
            md_lines.append("|--------|--------------|--------------|-----------|---------|")
            
            for metric_name, data in all_metrics.items():
                avg_score = sum(data['scores']) / len(data['scores']) if data['scores'] else 0
                metric_success_rate = (data['successes'] / data['total'] * 100) if data['total'] > 0 else 0
                threshold = data['threshold'] if data['threshold'] is not None else 'N/A'
                status = "✅ Pass" if metric_success_rate >= 70 else "⚠️ Warning" if metric_success_rate >= 50 else "❌ Fail"
                
                md_lines.append(f"| **{metric_name}** | {avg_score:.3f} | {metric_success_rate:.1f}% | {threshold} | {status} |")
            
            md_lines.append("")
        
        # Metric Analysis
        md_lines.append("## Metric Analysis")
        md_lines.append("")
        
        # Add descriptions for each metric
        metric_descriptions = {
            'FaithfulnessMetric': 'Measures whether the generated answer is faithful to the retrieved context.',
            'AnswerRelevancyMetric': 'Evaluates how relevant the answer is to the user\'s question.',
            'ContextualRecallMetric': 'Assesses whether all relevant information was retrieved.',
            'ContextualPrecisionMetric': 'Measures the precision of retrieved context.',
            'ContextualRelevancyMetric': 'Evaluates the relevancy of retrieved context to the query.'
        }
        
        for metric_name, data in all_metrics.items():
            md_lines.append(f"### {metric_name}")
            md_lines.append("")
            
            # Add description if available
            for key, desc in metric_descriptions.items():
                if key in metric_name:
                    md_lines.append(f"*{desc}*")
                    md_lines.append("")
                    break
            
            avg_score = sum(data['scores']) / len(data['scores']) if data['scores'] else 0
            min_score = min(data['scores']) if data['scores'] else 0
            max_score = max(data['scores']) if data['scores'] else 0
            
            md_lines.append("**Statistics:**")
            md_lines.append(f"- Average Score: `{avg_score:.3f}`")
            md_lines.append(f"- Min Score: `{min_score:.3f}`")
            md_lines.append(f"- Max Score: `{max_score:.3f}`")
            md_lines.append(f"- Pass Rate: `{(data['successes'] / data['total'] * 100) if data['total'] > 0 else 0:.1f}%`")
            md_lines.append("")
        
        # Detailed Test Results
        md_lines.append("## Detailed Test Results")
        md_lines.append("")
        
        for i, (test_case, test_result) in enumerate(zip(test_cases, test_results)):
            md_lines.append(f"### Test Case {i + 1}")
            md_lines.append("")
            
            # Test case status
            status = "✅ **PASSED**" if getattr(test_result, 'success', False) else "❌ **FAILED**"
            md_lines.append(f"**Status:** {status}")
            md_lines.append("")
            
            # Input/Output section
            md_lines.append("#### Query")
            md_lines.append("```")
            md_lines.append(test_case.input)
            md_lines.append("```")
            md_lines.append("")
            
            md_lines.append("#### Expected Output")
            md_lines.append("```")
            md_lines.append(test_case.expected_output)
            md_lines.append("```")
            md_lines.append("")
            
            md_lines.append("#### Actual Output")
            md_lines.append("```")
            md_lines.append(test_case.actual_output)
            md_lines.append("```")
            md_lines.append("")
            
            # Retrieval Context (collapsed by default using details tag)
            if test_case.retrieval_context:
                md_lines.append("<details>")
                md_lines.append("<summary><b>Retrieved Context</b> (click to expand)</summary>")
                md_lines.append("")
                for j, context in enumerate(test_case.retrieval_context, 1):
                    md_lines.append(f"**Context {j}:**")
                    md_lines.append("```")
                    md_lines.append(context[:500] + "..." if len(context) > 500 else context)
                    md_lines.append("```")
                    md_lines.append("")
                md_lines.append("</details>")
                md_lines.append("")
            
            # Metrics results
            md_lines.append("#### Metric Results")
            md_lines.append("")
            md_lines.append("| Metric | Score | Pass/Fail | Reason |")
            md_lines.append("|--------|-------|-----------|---------|")
            
            metrics_attr = None
            if hasattr(test_result, 'metrics_data'):
                metrics_attr = test_result.metrics_data
            elif hasattr(test_result, 'metrics'):
                metrics_attr = test_result.metrics
            elif hasattr(test_result, 'metric_results'):
                metrics_attr = test_result.metric_results
            
            if metrics_attr:
                for metric_data in metrics_attr:
                    metric_info = self.extract_metric_data(metric_data)
                    pass_fail = "✅ Pass" if metric_info['success'] else "❌ Fail"
                    reason = metric_info['reason'][:100] + "..." if len(metric_info['reason']) > 100 else metric_info['reason']
                    score = f"{metric_info['score']:.3f}" if metric_info['score'] is not None else "N/A"
                    
                    md_lines.append(f"| {metric_info['metric_name']} | {score} | {pass_fail} | {reason} |")
            
            md_lines.append("")
            md_lines.append("---")
            md_lines.append("")
        
        # Recommendations
        md_lines.append("## Recommendations")
        md_lines.append("")
        md_lines.append("Based on the evaluation results, here are key areas for improvement:")
        md_lines.append("")
        
        # Generate recommendations based on metric performance
        for metric_name, data in all_metrics.items():
            metric_success_rate = (data['successes'] / data['total'] * 100) if data['total'] > 0 else 0
            if metric_success_rate < 70:
                if 'Faithfulness' in metric_name:
                    md_lines.append("- **Improve Faithfulness**: The system is generating responses that deviate from the retrieved context. Consider:")
                    md_lines.append("  - Strengthening the prompt to emphasize using only information from context")
                    md_lines.append("  - Implementing stricter context-adherence checks")
                elif 'AnswerRelevancy' in metric_name:
                    md_lines.append("- **Enhance Answer Relevancy**: Responses are not fully addressing user queries. Consider:")
                    md_lines.append("  - Improving query understanding")
                    md_lines.append("  - Refining the response generation prompt")
                elif 'ContextualRecall' in metric_name:
                    md_lines.append("- **Boost Retrieval Recall**: Not all relevant information is being retrieved. Consider:")
                    md_lines.append("  - Adjusting retrieval parameters (k, similarity threshold)")
                    md_lines.append("  - Improving document chunking strategy")
                elif 'ContextualPrecision' in metric_name:
                    md_lines.append("- **Improve Retrieval Precision**: Too much irrelevant context is being retrieved. Consider:")
                    md_lines.append("  - Fine-tuning embedding model")
                    md_lines.append("  - Implementing re-ranking strategies")
                elif 'ContextualRelevancy' in metric_name:
                    md_lines.append("- **Enhance Context Relevancy**: Retrieved documents lack relevance. Consider:")
                    md_lines.append("  - Improving query preprocessing")
                    md_lines.append("  - Implementing semantic search enhancements")
                md_lines.append("")
        
        # Footer
        md_lines.append("---")
        md_lines.append("")
        md_lines.append("*This report was automatically generated by the RAG Evaluation Pipeline.*")
        md_lines.append(f"*Report generated on: {self.timestamp_readable}*")
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(md_lines))
        
        return filepath
    
    
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
import json
import re
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
        return self.model

    def _clean_json_response(self, response: str) -> str:
        """
        Clean and extract JSON from the LLM response.
        DeepEval expects pure JSON without any additional text.
        """
        print(f"DEBUG: Raw LLM Output: '{response}'")
        
        # Remove any markdown code block formatting
        response = re.sub(r'```json\s*', '', response)
        response = re.sub(r'```\s*$', '', response)
        
        # Try to extract JSON object from the response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
        else:
            json_str = response.strip()
        
        # Validate that it's proper JSON
        try:
            parsed = json.loads(json_str)
            result = json.dumps(parsed)  # Re-serialize to ensure clean formatting
            print(f"DEBUG: Cleaned JSON Output: '{result}'")
            return result
        except json.JSONDecodeError as e:
            print(f"DEBUG: JSON parsing failed: {e}")
            print(f"DEBUG: Attempted to parse: '{json_str}'")
            # Return a fallback JSON structure
            fallback = {"score": 0.0, "reason": "Failed to parse JSON response"}
            return json.dumps(fallback)

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
            "stream": False,
            "temperature": 1,  # Lower temperature for more consistent JSON output
            "max_completion_tokens": 16384
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    f"{self.base_url}chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=120.0  # Increased timeout for complex evaluations
                )
                response.raise_for_status()
                content_string = response.json()["choices"][0]["message"]["content"]
                
                # Clean and validate JSON response
                return self._clean_json_response(content_string)
                
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
            fallback = {"score": 0.0, "reason": f"HTTP error: {e.response.status_code}"}
            return json.dumps(fallback)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            fallback = {"score": 0.0, "reason": "Unexpected error occurred"}
            return json.dumps(fallback)
        
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
            "stream": False,
            "temperature": 1,  # Lower temperature for more consistent JSON output
            "max_completion_tokens": 16384
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=120.0  # Increased timeout for complex evaluations
                )
                response.raise_for_status()
                content_string = response.json()["choices"][0]["message"]["content"]
                
                # Clean and validate JSON response
                return self._clean_json_response(content_string)
                
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
            fallback = {"score": 0.0, "reason": f"HTTP error: {e.response.status_code}"}
            return json.dumps(fallback)
        except Exception as e:
            print(f"An unexpected error occurred during API call: {e}")
            fallback = {"score": 0.0, "reason": "Unexpected error occurred"}
            return json.dumps(fallback)

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

def get_rag_evaluation_suite(custom_llm):
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
        include_reason=True
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
import requests
import json
import pandas as pd


def session_create(database_id : str = None, api_url: str = BASE_URL):
    """
    Sends a POST request to create a session and returns the session ID if successful.

    :param api_url: The URL for the session creation API endpoint.
    :return: The session ID if successful, None otherwise.
    """
    try:
        create_session_data = {"tenant_name": "admin", "user_code": "admin"}
        if database_id:
            create_session_data = {"database_id": database_id,
                                   "tenant_name": "admin",
                                   "user_code": "admin"
                                   }
        response = requests.post(f"{api_url}/v1/session/create", json=create_session_data)
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response and extract the
            data = response.json()
            session_id = data.get("session_id")
            return session_id
        else:
            # Handle any other status codes
            return None

    except requests.exceptions.RequestException as e:
        # Handle any errors that occur during the request
        return None


def chat_request(
    session_id: str, 
    query: str, 
    on_click: bool, 
    database_id: str = None, 
    answer_type: str = "concise", 
    does_evaluate: bool = False, 
    use_cache: bool = True, 
    api_url: str = BASE_URL,
    sql_mode: bool = True
    ):
    
    # Define the request data
    chat_data = {
        "query": query,
        "session_id": session_id,  # Assume this is generated or fetched from somewhere
        "on_click": on_click,
        "does_evaluate": does_evaluate,
        "response_type": answer_type,
        "use_cache": use_cache,
        "sql_mode": sql_mode
    }
    if database_id:
        chat_data["database_id"] = database_id
        
    headers = {"Session-ID": session_id}
    response = requests.post(
        f"{api_url}/v1/chat", json=chat_data, headers=headers
    )  # , timeout=11

    # Handle the different response status codes
    json_response = response.json()
    if response.status_code == 200:
        return {
            "status": "success",
            "query": json_response["query"],
            "response": json_response["response"],
            "message_id": json_response["message_id"],
            "choices": json_response.get("choices", []),
            "is_sql": json_response.get("is_sql", False),
            "do_suggest": json_response.get("do_suggest", False)
        }
    else:
        return {"status": "error", "query": "", "response": "", "message_id": "", 
                "choices": [], "is_sql": False, "do_suggest": False}


def request_simple_qa(session_id, query, api_url: str = BASE_URL):
    payload = {
        "query": query,
        "session_id": session_id,  # Assume this is generated or fetched from somewhere
    }

    response = requests.get(f"{api_url}/v1/faq", params=payload)
    json_response = response.json()
    if response.status_code == 200:
        return {
            "status": "success",
            "response": json_response["response"]
            }
    else:
        return {"status": "error", "response": ""}


# A placeholder for the actual RAG chatbot application
def run_rag_chatbot(query: str) -> Tuple[str, List[str]]:
    """
    Simulates a call to the RAG chatbot.
    In a real application, this would invoke the RAG chain and return
    the generated answer and the retrieved context documents.
    """
    session_id = session_create()
    chat_response = chat_request(session_id=session_id, query=query, on_click=False)
    retrieved_context = request_simple_qa(session_id=session_id, query=chat_response["query"])
    retrieved_context_lst = retrieved_context["response"].split("\n\n ============= \n\n")
    return chat_response["response"], retrieved_context_lst


async def main():
    """
    Main function to orchestrate the RAG evaluation pipeline.
    """
    # 1. Setup: Load environment variables and initialize the custom model
    load_dotenv()
    api_key = os.getenv("LLM_API_KEY_EVAL")
    base_url = os.getenv("LLM_API_BASE_EVAL")
    model_name = os.getenv("LLM_MODEL_NAME_EVAL")

    if not base_url or not model_name:
        print("Error: CUSTOM_LLM_BASE_URL and CUSTOM_LLM_MODEL_NAME must be set in.env file.")
        return

    print("--- Initializing Custom LLM for Evaluation Judge ---")
    custom_llm_judge = CustomLLM(model=model_name, base_url=base_url, api_key=api_key)
    print(f"Judge Model: {custom_llm_judge.get_model_name()} at {custom_llm_judge.base_url}")

    # 2. Data Loading: Load the evaluation dataset from the local CSV
    print("\n--- Loading Evaluation Dataset ---")
    dataset_path = "/home/user01/mj-workspace/Assistant-bot/RagBot/eval/sample.csv"
    evaluation_data = load_evaluation_data(dataset_path)
    if not evaluation_data:
        print("Evaluation cannot proceed without data.")
        return
    print(f"Loaded {len(evaluation_data)} test case(s) from {dataset_path}")

    # 3. Test Case Generation: Create LLMTestCase objects dynamically
    print("\n--- Generating Test Cases from RAG Chatbot ---")
    test_cases: List[LLMTestCase] = []  # Initialize with empty list, not [""]

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
    evaluation_result = evaluate(test_cases=test_cases, metrics=metrics)
    print("--- Evaluation Complete ---")
    
    # 6. Reporting: Display the results
    print("\n--- Evaluation Results ---")
    
    # Initialize the result exporter
    exporter = ResultExporter(output_dir="./evaluation_results")
    
    try:
        if hasattr(evaluation_result, 'test_results'):
            test_results = evaluation_result.test_results
            print(f"Total Test Cases: {len(test_results)}")
            
            # Calculate success rate
            passed_tests = sum(1 for result in test_results if result.success)
            success_rate = passed_tests / len(test_results) if test_results else 0
            print(f"Overall Success Rate: {success_rate:.2%}")
            
            # Display results (your existing display code)
            for i, (test_case, test_result) in enumerate(zip(test_cases, test_results)):
                print(f"\n===== Test Case {i+1}: {test_case.input} =====")
                print(f"  Expected: {test_case.expected_output}")
                print(f"  Actual: {test_case.actual_output}")
                print(f"  Overall Status: {'PASSED' if test_result.success else 'FAILED'}")
                
                # ... [rest of your metric display code] ...
            
            # Export results to files
            print("\n--- Exporting Results ---")
            
            # Create evaluation metadata
            metadata = {
                'model_name': model_name,
                'base_url': base_url,
                'dataset_path': dataset_path,
                'metrics_used': [type(m).__name__ for m in metrics],
                'total_test_cases': len(test_cases),
                'success_rate': success_rate
            }
            
            # Export to Markdown (human-readable report)
            md_path = exporter.export_to_markdown(
                test_cases=test_cases,
                test_results=test_results,
                evaluation_metadata=metadata
            )
            print(f"✓ Evaluation report exported to Markdown: {md_path}")
            
            # Export to JSON (detailed)
            json_path = exporter.export_to_json(
                test_cases=test_cases,
                test_results=test_results,
                evaluation_metadata=metadata
            )
            print(f"✓ Detailed results exported to JSON: {json_path}")
            
            # Export to CSV (tabular)
            results_data = exporter.prepare_results_data(test_cases, test_results)
            csv_path = exporter.export_to_csv(results_data)
            print(f"✓ Tabular results exported to CSV: {csv_path}")
            
            # Optional: Export a summary CSV with just aggregates
            summary_data = [{
                'timestamp': exporter.timestamp,
                'total_cases': len(test_cases),
                'passed': passed_tests,
                'failed': len(test_cases) - passed_tests,
                'success_rate': success_rate,
                'model': model_name
            }]
            summary_df = pd.DataFrame(summary_data)
            summary_path = os.path.join(exporter.output_dir, f"evaluation_summary_{exporter.timestamp}.csv")
            summary_df.to_csv(summary_path, index=False)
            print(f"✓ Summary exported to CSV: {summary_path}")
            
            print(f"\nAll results saved to: {exporter.output_dir}/")
            
        else:
            print("No test_results attribute found in evaluation result")
            
    except Exception as e:
        print(f"Error processing/exporting results: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
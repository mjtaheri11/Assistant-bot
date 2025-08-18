import os
from typing import List, Dict, Any
from dataclasses import dataclass
from dotenv import load_dotenv
import json

# DeepEval imports
from deepeval import evaluate
from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    ContextualRelevancyMetric,
    HallucinationMetric,
    ToxicityMetric,
    BiasMetric,
    AnswerCorrectnessMetric
)
from deepeval.test_case import LLMTestCase
from deepeval.dataset import EvaluationDataset
from deepeval.synthesizer import Synthesizer

# load environment variables 
load_dotenv()

@dataclass
class RAGTestCase:
    """Custom test case for RAG evaluation"""
    query: str
    expected_output: str
    actual_output: str
    retrieval_context: List[str]
    ground_truth_context: List[str] = None

import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import json
import litellm

# Configure litellm for verbose output (optional)
litellm.set_verbose = True

class CustomModelRAGEvaluator:
    """
    RAG Evaluator with support for custom models and API endpoints
    """
    
    def __init__(
        self, 
        model: str = "gpt-4",
        api_base: Optional[str] = None,
        api_key: Optional[str] = None,
        provider: Optional[str] = "custom",
        threshold: float = 0.7,
        custom_headers: Optional[Dict] = None
    ):
        """
        Initialize evaluator with custom model configuration
        
        Args:
            model: Model name or path
            api_base: Custom API base URL (for OpenAI-compatible endpoints)
            api_key: API key for the service
            provider: Provider name (ollama, together_ai, azure, etc.)
            threshold: Minimum score threshold
            custom_headers: Additional headers for API requests
        """
        self.threshold = threshold
        self.provider = provider
        
        # Configure based on provider
        if provider:
            self.model = self._configure_provider(provider, model, api_base, api_key)
        else:
            self.model = model
            
        # Set custom headers if provided
        if custom_headers:
            litellm.headers = custom_headers
            
        self._initialize_metrics()
    
    def _configure_provider(self, provider: str, model: str, api_base: str, api_key: str) -> str:
        """
        Configure specific provider settings
        Based on [docs.together.ai](https://docs.together.ai/docs/openai-api-compatibility)
        and [docs.praison.ai](https://docs.praison.ai/models/other)
        """
        provider_configs = {
            "ollama": {
                "base": api_base or "http://localhost:11434/v1",
                "key": "NA",
                "model_prefix": "ollama/"
            },
            "lm_studio": {
                "base": api_base or "http://localhost:1234/v1",
                "key": "NA",
                "model_prefix": ""
            },
            "together_ai": {
                "base": api_base or "https://api.together.xyz/v1",
                "key": api_key or os.getenv("TOGETHER_API_KEY"),
                "model_prefix": "together_ai/"
            },
            "mistral": {
                "base": api_base or "https://api.mistral.ai/v1",
                "key": api_key or os.getenv("MISTRAL_API_KEY"),
                "model_prefix": ""
            },
            "fastchat": {
                "base": api_base or "http://localhost:8001/v1",
                "key": "NA",
                "model_prefix": ""
            },
            "azure": {
                "base": api_base,
                "key": api_key or os.getenv("AZURE_API_KEY"),
                "model_prefix": "azure/"
            },
            "anthropic": {
                "base": api_base or "https://api.anthropic.com",
                "key": api_key or os.getenv("ANTHROPIC_API_KEY"),
                "model_prefix": ""
            },
            "custom": {
                "base": os.getenv("LLM_MODEL_NAME"),
                "key": os.getenv("LLM_API_KEY") or "NA",
                "model_prefix": ""
            }
        }
        
        config = provider_configs.get(provider, provider_configs["custom"])
        
        # Return model with appropriate prefix
        if config["model_prefix"] and not model.startswith(config["model_prefix"]):
            return f"{config['model_prefix']}{model}"
        return model
    
    def _initialize_metrics(self):
        """Initialize metrics with the configured model"""
        from deepeval.metrics import (
            AnswerRelevancyMetric,
            FaithfulnessMetric,
            ContextualPrecisionMetric,
            ContextualRecallMetric,
            ContextualRelevancyMetric,
            HallucinationMetric
        )
        
        # All metrics use the same model configuration
        self.answer_relevancy = AnswerRelevancyMetric(
            threshold=self.threshold,
            model=self.model,
            include_reason=True
        )
        
        self.faithfulness = FaithfulnessMetric(
            threshold=self.threshold,
            model=self.model,
            include_reason=True
        )
        
        self.contextual_precision = ContextualPrecisionMetric(
            threshold=self.threshold,
            model=self.model,
            include_reason=True
        )
        
        self.contextual_recall = ContextualRecallMetric(
            threshold=self.threshold,
            model=self.model,
            include_reason=True
        )
        
        self.contextual_relevancy = ContextualRelevancyMetric(
            threshold=self.threshold,
            model=self.model,
            include_reason=True
        )
        
        self.hallucination = HallucinationMetric(
            threshold=self.threshold,
            model=self.model,
            include_reason=True
        )
    
    def test_connection(self) -> bool:
        """
        Test if the model connection is working
        """
        try:
            from deepeval.test_case import LLMTestCase
            
            test_case = LLMTestCase(
                input="Test question",
                actual_output="Test answer",
                retrieval_context=["Test context"]
            )
            
            # Try a simple metric evaluation
            self.answer_relevancy.measure(test_case)
            print(f"✅ Successfully connected to model: {self.model}")
            print(f"   API Base: {os.getenv('OPENAI_API_BASE', 'default')}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to connect to model: {e}")
            return False
    
    def _initialize_metrics(self):
        """Initialize all evaluation metrics"""
        
        # Retrieval Metrics
        self.contextual_precision = ContextualPrecisionMetric(
            threshold=self.threshold,
            model=self.model,
            include_reason=True
        )
        
        self.contextual_recall = ContextualRecallMetric(
            threshold=self.threshold,
            model=self.model,
            include_reason=True
        )
        
        self.contextual_relevancy = ContextualRelevancyMetric(
            threshold=self.threshold,
            model=self.model,
            include_reason=True
        )
        
        # Generation Metrics
        self.answer_relevancy = AnswerRelevancyMetric(
            threshold=self.threshold,
            model=self.model,
            include_reason=True
        )
        
        self.faithfulness = FaithfulnessMetric(
            threshold=self.threshold,
            model=self.model,
            include_reason=True
        )
        
        self.hallucination = HallucinationMetric(
            threshold=self.threshold,
            model=self.model,
            include_reason=True
        )
        
        # End-to-End Metrics
        self.answer_correctness = AnswerCorrectnessMetric(
            threshold=self.threshold,
            model=self.model,
            include_reason=True
        )
        
        # Safety Metrics (optional)
        self.toxicity = ToxicityMetric(
            threshold=0.5,
            model=self.model
        )
        
        self.bias = BiasMetric(
            threshold=0.5,
            model=self.model
        )
    
    def evaluate_retrieval(self, test_cases: List[RAGTestCase]) -> Dict[str, Any]:
        """
        Evaluate the retrieval component of RAG
        
        Args:
            test_cases: List of RAG test cases
            
        Returns:
            Dictionary containing retrieval evaluation results
        """
        print("🔍 Evaluating Retrieval Component...")
        
        retrieval_metrics = [
            self.contextual_precision,
            self.contextual_recall,
            self.contextual_relevancy
        ]
        
        results = {
            "contextual_precision": [],
            "contextual_recall": [],
            "contextual_relevancy": []
        }
        
        for test_case in test_cases:
            llm_test_case = LLMTestCase(
                input=test_case.query,
                actual_output=test_case.actual_output,
                expected_output=test_case.expected_output,
                retrieval_context=test_case.retrieval_context,
                context=test_case.ground_truth_context or test_case.retrieval_context
            )
            
            for metric in retrieval_metrics:
                metric.measure(llm_test_case)
                metric_name = metric.__class__.__name__.replace("Metric", "").lower()
                
                results[metric_name].append({
                    "score": metric.score,
                    "passed": metric.score >= self.threshold,
                    "reason": metric.reason if hasattr(metric, 'reason') else None
                })
        
        return self._aggregate_results(results, "Retrieval")
    
    def evaluate_generation(self, test_cases: List[RAGTestCase]) -> Dict[str, Any]:
        """
        Evaluate the generation component of RAG
        
        Args:
            test_cases: List of RAG test cases
            
        Returns:
            Dictionary containing generation evaluation results
        """
        print("🤖 Evaluating Generation Component...")
        
        generation_metrics = [
            self.answer_relevancy,
            self.faithfulness,
            self.hallucination,
            self.answer_correctness
        ]
        
        results = {
            "answer_relevancy": [],
            "faithfulness": [],
            "hallucination": [],
            "answer_correctness": []
        }
        
        for test_case in test_cases:
            llm_test_case = LLMTestCase(
                input=test_case.query,
                actual_output=test_case.actual_output,
                expected_output=test_case.expected_output,
                retrieval_context=test_case.retrieval_context
            )
            
            for metric in generation_metrics:
                metric.measure(llm_test_case)
                metric_name = metric.__class__.__name__.replace("Metric", "").lower()
                
                results[metric_name].append({
                    "score": metric.score,
                    "passed": metric.score >= self.threshold,
                    "reason": metric.reason if hasattr(metric, 'reason') else None
                })
        
        return self._aggregate_results(results, "Generation")
    
    def evaluate_safety(self, test_cases: List[RAGTestCase]) -> Dict[str, Any]:
        """
        Evaluate safety aspects (toxicity, bias) of the generated responses
        
        Args:
            test_cases: List of RAG test cases
            
        Returns:
            Dictionary containing safety evaluation results
        """
        print("🛡️ Evaluating Safety Metrics...")
        
        safety_metrics = [self.toxicity, self.bias]
        
        results = {
            "toxicity": [],
            "bias": []
        }
        
        for test_case in test_cases:
            llm_test_case = LLMTestCase(
                input=test_case.query,
                actual_output=test_case.actual_output
            )
            
            for metric in safety_metrics:
                metric.measure(llm_test_case)
                metric_name = metric.__class__.__name__.replace("Metric", "").lower()
                
                results[metric_name].append({
                    "score": metric.score,
                    "passed": metric.score <= 0.5,  # Lower is better for safety metrics
                    "details": metric.reason if hasattr(metric, 'reason') else None
                })
        
        return self._aggregate_results(results, "Safety")
    
    def evaluate_rag_triad(self, test_cases: List[RAGTestCase]) -> Dict[str, Any]:
        """
        Evaluate using the RAG Triad approach (Context Relevance, Groundedness, Answer Relevance)
        Based on [deepeval.com](https://www.deepeval.com/guides/guides-rag-triad)
        
        Args:
            test_cases: List of RAG test cases
            
        Returns:
            Dictionary containing RAG Triad evaluation results
        """
        print("🔺 Evaluating RAG Triad...")
        
        triad_results = {
            "context_relevance": [],
            "groundedness": [],
            "answer_relevance": []
        }
        
        for test_case in test_cases:
            llm_test_case = LLMTestCase(
                input=test_case.query,
                actual_output=test_case.actual_output,
                expected_output=test_case.expected_output,
                retrieval_context=test_case.retrieval_context
            )
            
            # Context Relevance
            self.contextual_relevancy.measure(llm_test_case)
            triad_results["context_relevance"].append({
                "score": self.contextual_relevancy.score,
                "passed": self.contextual_relevancy.score >= self.threshold
            })
            
            # Groundedness (using Faithfulness)
            self.faithfulness.measure(llm_test_case)
            triad_results["groundedness"].append({
                "score": self.faithfulness.score,
                "passed": self.faithfulness.score >= self.threshold
            })
            
            # Answer Relevance
            self.answer_relevancy.measure(llm_test_case)
            triad_results["answer_relevance"].append({
                "score": self.answer_relevancy.score,
                "passed": self.answer_relevancy.score >= self.threshold
            })
        
        return self._aggregate_results(triad_results, "RAG Triad")
    
    def full_evaluation(self, test_cases: List[RAGTestCase]) -> Dict[str, Any]:
        """
        Perform comprehensive evaluation of the entire RAG pipeline
        
        Args:
            test_cases: List of RAG test cases
            
        Returns:
            Dictionary containing all evaluation results
        """
        print("📊 Starting Full RAG Evaluation...")
        print(f"Evaluating {len(test_cases)} test cases\n")
        
        results = {
            "retrieval": self.evaluate_retrieval(test_cases),
            "generation": self.evaluate_generation(test_cases),
            "rag_triad": self.evaluate_rag_triad(test_cases),
            "safety": self.evaluate_safety(test_cases),
            "summary": {}
        }
        
        # Calculate overall summary
        all_scores = []
        for component in ["retrieval", "generation", "rag_triad"]:
            all_scores.extend([
                score for metric_scores in results[component]["detailed_scores"].values()
                for score in metric_scores
            ])
        
        results["summary"] = {
            "total_tests": len(test_cases),
            "overall_average_score": sum(all_scores) / len(all_scores) if all_scores else 0,
            "component_averages": {
                "retrieval": results["retrieval"]["average_score"],
                "generation": results["generation"]["average_score"],
                "rag_triad": results["rag_triad"]["average_score"],
                "safety": results["safety"]["average_score"]
            }
        }
        
        return results
    
    def _aggregate_results(self, results: Dict, component_name: str) -> Dict[str, Any]:
        """Aggregate and summarize evaluation results"""
        aggregated = {
            "component": component_name,
            "metrics": {},
            "detailed_scores": {},
            "average_score": 0
        }
        
        all_scores = []
        for metric_name, metric_results in results.items():
            scores = [r["score"] for r in metric_results]
            aggregated["detailed_scores"][metric_name] = scores
            
            if scores:
                avg_score = sum(scores) / len(scores)
                passed_count = sum(1 for r in metric_results if r["passed"])
                
                aggregated["metrics"][metric_name] = {
                    "average_score": avg_score,
                    "pass_rate": passed_count / len(metric_results),
                    "passed": passed_count,
                    "failed": len(metric_results) - passed_count
                }
                all_scores.extend(scores)
        
        if all_scores:
            aggregated["average_score"] = sum(all_scores) / len(all_scores)
        
        return aggregated
    
    def generate_report(self, results: Dict[str, Any], output_file: str = "rag_evaluation_report.json"):
        """
        Generate a detailed evaluation report
        
        Args:
            results: Evaluation results dictionary
            output_file: Path to save the report
        """
        print(f"\n📝 Generating Report...")
        
        # Console output
        print("\n" + "="*60)
        print("RAG EVALUATION REPORT")
        print("="*60)
        
        for component in ["retrieval", "generation", "rag_triad", "safety"]:
            if component in results:
                print(f"\n{component.upper()} METRICS:")
                print("-"*40)
                
                for metric, scores in results[component]["metrics"].items():
                    print(f"  {metric}:")
                    print(f"    Average Score: {scores['average_score']:.3f}")
                    print(f"    Pass Rate: {scores['pass_rate']:.1%}")
                    print(f"    Passed/Failed: {scores['passed']}/{scores['failed']}")
        
        if "summary" in results:
            print(f"\n{'OVERALL SUMMARY':^60}")
            print("="*60)
            print(f"Total Test Cases: {results['summary']['total_tests']}")
            print(f"Overall Average Score: {results['summary']['overall_average_score']:.3f}")
            print("\nComponent Averages:")
            for comp, avg in results['summary']['component_averages'].items():
                print(f"  {comp}: {avg:.3f}")
        
        # Save to file
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n✅ Report saved to {output_file}")


# Example usage function
def create_sample_test_cases() -> List[RAGTestCase]:
    """Create sample test cases for demonstration"""
    return [
        RAGTestCase(
            query="What is the capital of France?",
            expected_output="The capital of France is Paris.",
            actual_output="The capital of France is Paris, which is also the country's largest city.",
            retrieval_context=[
                "Paris is the capital and largest city of France.",
                "France is a country in Western Europe.",
                "The Eiffel Tower is located in Paris."
            ]
        ),
        RAGTestCase(
            query="Explain photosynthesis",
            expected_output="Photosynthesis is the process by which plants convert light energy into chemical energy.",
            actual_output="Photosynthesis is the process where plants use sunlight, water, and carbon dioxide to produce glucose and oxygen.",
            retrieval_context=[
                "Photosynthesis occurs in chloroplasts.",
                "Plants use sunlight to convert CO2 and water into glucose.",
                "Chlorophyll is the green pigment that captures light energy."
            ]
        )
    ]


# Synthesizer for generating test data (optional)
class RAGTestDataGenerator:
    """
    Generate synthetic test data for RAG evaluation
    Based on [llamaindex.ai](https://www.llamaindex.ai/blog/evaluating-rag-with-deepeval-and-llamaindex)
    """
    
    def __init__(self, documents: List[str]):
        """
        Initialize the test data generator
        
        Args:
            documents: List of documents to generate test cases from
        """
        self.synthesizer = Synthesizer(model="gpt-4")
        self.documents = documents
    
    def generate_test_cases(self, num_cases: int = 10) -> List[RAGTestCase]:
        """
        Generate synthetic test cases
        
        Args:
            num_cases: Number of test cases to generate
            
        Returns:
            List of generated test cases
        """
        # Generate using DeepEval's synthesizer
        dataset = self.synthesizer.generate_goldens_from_docs(
            documents=self.documents,
            num_goldens_per_doc=num_cases // len(self.documents)
        )
        
        test_cases = []
        for golden in dataset.goldens:
            test_cases.append(RAGTestCase(
                query=golden.input,
                expected_output=golden.expected_output,
                actual_output="",  # Will be filled by your RAG system
                retrieval_context=golden.context,
                ground_truth_context=golden.context
            ))
        
        return test_cases


# Main execution
if __name__ == "__main__":
    # Initialize evaluator
    evaluator = RAGEvaluator(model="gpt-4", threshold=0.7)
    
    # Create or load your test cases
    test_cases = create_sample_test_cases()
    
    # Run full evaluation
    results = evaluator.full_evaluation(test_cases)
    
    # Generate report
    evaluator.generate_report(results)
    
    # Optional: Generate synthetic test data
    # generator = RAGTestDataGenerator(documents=["your", "documents", "here"])
    # synthetic_cases = generator.generate_test_cases(num_cases=20)
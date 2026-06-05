"""Run evaluation on golden dataset"""
import asyncio
from src.evaluation.offline.ragas_evaluator import RAGASEvaluator
from benchmarks.emerging import EmergingBenchmarkSuite

async def run_evaluation():
    """Run comprehensive evaluation"""
    
    # Load golden dataset
    with open('benchmarks/datasets/golden_dataset.json') as f:
        golden_dataset = json.load(f)
    
    # Run RAGAS
    ragas_eval = RAGASEvaluator()
    ragas_scores = await ragas_eval.evaluate(golden_dataset['queries'])
    
    # Run emerging benchmarks
    benchmark_suite = EmergingBenchmarkSuite()
    emerging_scores = await benchmark_suite.evaluate_comprehensive(
        query=golden_dataset['queries'][0]['query'],
        response="",  # Get from RAG system
        retrieved_docs=[],  # Get from retrieval
        context=""  # Get from processing
    )
    
    print(f"RAGAS Scores: {ragas_scores}")
    print(f"Emerging Benchmarks: {emerging_scores}")

if __name__ == "__main__":
    asyncio.run(run_evaluation())

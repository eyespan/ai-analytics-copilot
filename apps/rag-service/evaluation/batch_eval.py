import json
from retrieval.hybrid import hybrid_search
from evaluation.metrics import recall_at_k, reciprocal_rank


def load_dataset(path="evaluation/dataset.json"):
    with open(path, "r") as f:
        return json.load(f)


def run_batch_eval():
    dataset = load_dataset()

    results_summary = []

    total_recall = 0
    total_rr = 0

    for item in dataset:
        query = item["query"]
        expected = item["expected_repo"]

        results = hybrid_search(query)

        recall = recall_at_k(results, expected)
        rr = reciprocal_rank(results, expected)

        total_recall += recall
        total_rr += rr

        results_summary.append({
            "query": query,
            "expected_repo": expected,
            "recall": recall,
            "reciprocal_rank": rr
        })

    n = len(dataset)

    return {
        "count": n,
        "mean_recall": total_recall / n,
        "mrr": total_rr / n,
        "details": results_summary
    }
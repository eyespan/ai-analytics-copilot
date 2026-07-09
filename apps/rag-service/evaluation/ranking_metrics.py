import math


def ndcg_at_k(results, expected_repos, k=10):
    expected_set = set(expected_repos)

    dcg = 0.0
    for i, r in enumerate(results[:k]):
        if r["repo_name"] in expected_set:
            dcg += 1 / math.log2(i + 2)

    # ideal DCG
    ideal_hits = min(len(expected_set), k)
    idcg = sum(1 / math.log2(i + 2) for i in range(ideal_hits))

    return dcg / idcg if idcg > 0 else 0.0

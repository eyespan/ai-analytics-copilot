def recall_at_k(results, expected_repos, k=10):
    expected_set = set(expected_repos)
    retrieved_set = set(r["repo_name"] for r in results[:k])

    return 1 if len(expected_set & retrieved_set) > 0 else 0


def reciprocal_rank(results, expected_repos):
    expected_set = set(expected_repos)

    best_rank = None

    for idx, result in enumerate(results, start=1):
        if result["repo_name"] in expected_set:
            best_rank = idx
            break

    return 1 / best_rank if best_rank else 0
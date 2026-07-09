import argparse
import json

from evaluation.dataset_loader import load_dataset
from evaluation.runner import EvaluationRunner
from agents.agent_executor import AgentExecutor
from agents.tool_registry import ToolRegistry
from agents.tools import get_time
from agents.tools import search_docs


def build_executor():

    # You plug your real model here
    from your_model_provider import model

    registry = ToolRegistry()

    # register tools (example)
    # from tools.time_tool import get_time
    # from tools.search_tool import search_docs

    registry.register("get_time", get_time)
    registry.register("search_docs", search_docs)

    return AgentExecutor(model=model, tool_registry=registry)


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("command")
    parser.add_argument("dataset")

    args = parser.parse_args()

    if args.command != "run":
        raise ValueError("Only 'run' supported")

    dataset = load_dataset(args.dataset)

    executor = build_executor()
    runner = EvaluationRunner(executor)

    result = runner.run_dataset(dataset)

    print("\n======================")
    print("EVALUATION SUMMARY")
    print("======================")
    print(json.dumps(result["summary"], indent=2))

    # save full report
    with open("evaluation_report.json", "w") as f:
        json.dump(result, f, indent=2)

    print("\nSaved: evaluation_report.json")


if __name__ == "__main__":
    main()

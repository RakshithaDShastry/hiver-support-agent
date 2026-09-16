"""
Reproduces the headline results from SAVED outputs — no API key needed,
runs in seconds. This is the primary reproduction path referenced in the
README's 15-minute promise.

For the (much slower, optional) path that regenerates these outputs by
actually calling the LLM APIs, see scripts/run_full_pipeline.py.

Usage:
    python scripts/compute_metrics.py
"""

import pandas as pd
from sklearn.metrics import accuracy_score, classification_report

GOLDEN_RESULTS_PATH = "data/processed/golden_set_final_results.csv"
BASELINE_RESULTS_PATH = "data/processed/baseline_results.csv"
EVAL_RESULTS_PATH = "data/processed/final_eval_results.csv"


def print_header(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def main():
    print_header("INTENT CLASSIFICATION: LLM vs. baselines")
    golden_df = pd.read_csv(GOLDEN_RESULTS_PATH)
    baseline_results = pd.read_csv(BASELINE_RESULTS_PATH)

    llm_accuracy = accuracy_score(golden_df['intent_label'], golden_df['llm_prediction'])

    print(baseline_results.to_string(index=False))
    print(f"\n{'LLM classifier (few-shot)':<35}{llm_accuracy:.3f}")

    print("\nPer-category breakdown (LLM classifier):")
    print(classification_report(
        golden_df['intent_label'], golden_df['llm_prediction'], zero_division=0
    ))

    print_header("REPLY DRAFTING + ESCALATION: full pipeline eval (n=50)")
    eval_df = pd.read_csv(EVAL_RESULTS_PATH)
    print(f"Mean judge score (1-5, v2 judge — see failure_analysis.md for its known bias): "
          f"{eval_df['judge_score'].mean():.2f}")
    print("\nEscalation decisions:")
    print(eval_df['escalation_decision'].value_counts().to_string())

    print_header("Done")
    print("See reports/report.md, reports/failure_analysis.md, and")
    print("reports/decision_log.md for full analysis and reasoning.")


if __name__ == "__main__":
    main()

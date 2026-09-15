"""
Baseline classifiers for intent classification.

Both baselines are trained/evaluated using only the golden set itself
(no separate training data), since hand-labeled data is scarce:

- Majority class: predicts the single most frequent label. No real
  "training" beyond reading the label distribution.
- TF-IDF + Logistic Regression: evaluated with stratified k-fold
  cross-validation on the golden set, so no example is ever evaluated
  using a model that was trained on it.

These exist purely to give the LLM-based classifier's accuracy a
meaningful point of comparison. A headline number with no baseline
is not evidence of anything.
"""

from collections import Counter

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score, classification_report


def majority_class_baseline(labels):
    """Returns (accuracy, most_common_label) for always predicting the
    single most frequent label in `labels`."""
    counts = Counter(labels)
    majority_label = counts.most_common(1)[0][0]
    predictions = [majority_label] * len(labels)
    accuracy = accuracy_score(labels, predictions)
    return accuracy, majority_label


def tfidf_logreg_cv_baseline(texts, labels, n_splits=5, random_state=42):
    """Runs stratified k-fold CV with a TF-IDF + Logistic Regression
    pipeline, refitting the vectorizer and model fresh in every fold
    (so no fold's vocabulary is contaminated by its own test text).

    Returns:
        overall_accuracy: float
        fold_accuracies: list of per-fold accuracy
        all_predictions: predictions aligned to input order (for error analysis)
        report: sklearn classification_report string, computed over all
                out-of-fold predictions pooled together
    """
    texts = np.array(texts)
    labels = np.array(labels)

    # Guard: stratified k-fold needs every class to have >= n_splits examples.
    class_counts = Counter(labels)
    min_class_count = min(class_counts.values())
    if min_class_count < n_splits:
        raise ValueError(
            f"Smallest class has only {min_class_count} examples, which is "
            f"fewer than n_splits={n_splits}. Either reduce n_splits or "
            f"check for a rare/mislabeled category."
        )

    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)

    all_predictions = np.empty(len(labels), dtype=object)
    fold_accuracies = []

    for fold_idx, (train_idx, test_idx) in enumerate(skf.split(texts, labels)):
        vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            min_df=1,
        )
        X_train = vectorizer.fit_transform(texts[train_idx])
        X_test = vectorizer.transform(texts[test_idx])

        clf = LogisticRegression(max_iter=1000, class_weight="balanced")
        clf.fit(X_train, labels[train_idx])

        preds = clf.predict(X_test)
        all_predictions[test_idx] = preds

        fold_acc = accuracy_score(labels[test_idx], preds)
        fold_accuracies.append(fold_acc)

    overall_accuracy = accuracy_score(labels, all_predictions)
    report = classification_report(labels, all_predictions, zero_division=0)

    return overall_accuracy, fold_accuracies, list(all_predictions), report


if __name__ == "__main__":
    # Smoke test with synthetic data, just to confirm the code runs
    # end-to-end correctly before real golden-set labels exist.
    rng = np.random.default_rng(0)
    fake_intents = [
        "Technical/Product Issue", "Billing & Subscription", "Account & Access",
        "How-to / Informational Question", "Feature/Content Request",
        "General Complaint/Feedback", "Other/Unclear",
    ]
    fake_texts = [
        f"sample support message number {i} about {rng.choice(fake_intents)}"
        for i in range(140)
    ]
    fake_labels = [rng.choice(fake_intents) for _ in range(140)]

    maj_acc, maj_label = majority_class_baseline(fake_labels)
    print(f"[smoke test] Majority baseline accuracy: {maj_acc:.3f} (always predicts '{maj_label}')")

    overall_acc, fold_accs, preds, report = tfidf_logreg_cv_baseline(fake_texts, fake_labels, n_splits=5)
    print(f"[smoke test] TF-IDF+LR overall CV accuracy: {overall_acc:.3f}")
    print(f"[smoke test] Per-fold accuracies: {[round(a, 3) for a in fold_accs]}")
    print("[smoke test] Code ran end-to-end without errors.")

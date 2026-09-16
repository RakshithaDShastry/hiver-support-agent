"""
Data preparation: builds the SpotifyCares-scoped subsets used throughout
the pipeline, from the raw Kaggle "Customer Support on Twitter" dataset.

This is a SUBSAMPLE by design (see decision_log.md) — we scope to one
brand's data, not the full ~3M-row dataset.
"""

import pandas as pd


def load_raw_dataset(csv_path):
    """Loads the raw twcs.csv file downloaded via kagglehub."""
    return pd.read_csv(csv_path)


def build_spotify_subsets(df):
    """
    From the full raw dataset, builds:
      - spotify_replies: every reply sent BY SpotifyCares
      - customer_msgs: every customer message SpotifyCares replied to
      - openers: customer messages that START a conversation
                 (in_response_to_tweet_id is null) — see decision_log.md
                 entry 1 for why we scope to openers only.
      - resolved_pairs: (customer message, real SpotifyCares reply) pairs,
                 filtered to 5+ word customer messages (decision_log.md
                 entry 10) — used as the retrieval grounding corpus.
    """
    spotify_replies = df[df['author_id'] == 'SpotifyCares']

    spotify_ids = set(spotify_replies['in_response_to_tweet_id'].dropna())
    customer_msgs = df[df['tweet_id'].isin(spotify_ids)]

    openers = customer_msgs[customer_msgs['in_response_to_tweet_id'].isna()]

    resolved_pairs = spotify_replies.dropna(subset=['in_response_to_tweet_id']).copy()
    resolved_pairs = resolved_pairs.merge(
        df[['tweet_id', 'text']],
        left_on='in_response_to_tweet_id',
        right_on='tweet_id',
        suffixes=('_reply', '_customer')
    )
    resolved_pairs = resolved_pairs[['text_customer', 'text_reply']].dropna()
    resolved_pairs = resolved_pairs.drop_duplicates(subset=['text_customer'])
    resolved_pairs = resolved_pairs[
        resolved_pairs['text_customer'].str.split().str.len() >= 5
    ].copy()

    return {
        'spotify_replies': spotify_replies,
        'customer_msgs': customer_msgs,
        'openers': openers,
        'resolved_pairs': resolved_pairs,
    }

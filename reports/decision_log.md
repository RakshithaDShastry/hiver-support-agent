# Decision Log

Non-obvious decisions made while building this project, and the reasoning
behind each.

1. **Scoped the agent to conversation-opening messages only** (where
   `in_response_to_tweet_id` is null), not every customer tweet. Manual
   review showed mid-thread replies are frequently uninterpretable without
   prior context (e.g. "IT WAS A MISTAKE", "Nevermind it works again"). This
   also mirrors how a real support agent triggers: on new ticket creation.

2. **Chose SpotifyCares over larger brands** (e.g. AmazonHelp at 170k
   messages) despite having less data. Single-product brands produce a
   tighter, more defensible intent taxonomy in a short timeframe; AmazonHelp
   spans orders/deliveries/refunds/devices, which would fragment the
   taxonomy.

3. **Stopped taxonomy-drafting sampling at 80 hand-reviewed examples**
   (2 batches of 40) rather than continuing indefinitely. Categories had
   stabilized by the second batch; further sampling had diminishing returns
   against the project's time budget.

4. **Split "Content Availability" out from general technical bugs** during
   golden-set labelling, after real examples showed these need different
   resolutions (a licensing/catalog fact to communicate vs. something to
   troubleshoot) even though they can look identical to the customer (e.g.
   greyed-out tracks).

5. **Folded "How-to/Informational Question" into Account & Access** rather
   than keeping it as its own category, since in practice these examples
   were rare and usually overlapped with account/registration questions.

6. **Baselines are trained without a separate labeled training set.**
   Majority-class uses the golden set's own label distribution; TF-IDF +
   Logistic Regression uses 5-fold stratified cross-validation on the golden
   set itself (via `sklearn.Pipeline` + `cross_val_score`, which refits the
   vectorizer fresh per fold, avoiding leakage) rather than a held-out
   split, since a separate large labeled training set doesn't exist and
   wasn't worth hand-labelling given the timeline.

7. **Switched LLM provider from Google Gemini to Groq mid-project.**
   Gemini's `gemini-3.6-flash` free tier turned out to be capped at 20
   requests/day — unusable for a 200-example evaluation. Groq's
   `openai/gpt-oss-120b` free tier (1000 requests/day, no card) was
   sufficient for classification, generation, and judging combined.

8. **Chose few-shot over zero-shot for the intent classifier.** Few-shot
   examples were deliberately drawn from outside the golden set (verified
   by tweet_id exclusion) to avoid evaluating the classifier on data it had
   effectively seen.

9. **Used TF-IDF + cosine similarity for retrieval, not neural embeddings.**
   Simpler, no extra dependencies, fast to iterate on given the timeline.
   Known tradeoff: embeddings would likely retrieve more semantically
   similar examples even without shared vocabulary (e.g. matching "songs
   are grey" with "can't play tracks"); flagged as a "what's next" item
   rather than silently treated as equivalent to a better solution we
   didn't have time to validate.

10. **Filtered the retrieval corpus to messages with 5+ words and added a
    0.25 minimum-similarity floor.** Initial testing showed very short
    historical messages (e.g. "Why???", "Why") produced spuriously high
    similarity scores against unrelated queries, since with so little text
    almost the entire message is the one shared word.

11. **Strip URLs from retrieved historical replies before they enter the
    generation prompt, and explicitly instruct the model never to include a
    link.** Testing surfaced a real failure: the model reused a URL from a
    retrieved historical reply as if it were a valid, generic link for the
    current customer — a fabricated-looking but plausible link is a worse
    failure mode than an admitted lack of information.

12. **Reply generation explicitly tells the model to ignore retrieved
    examples that aren't actually relevant**, rather than trusting the
    retrieval step's top-k blindly, since retrieval quality is known to be
    imperfect (see decision 9/10).

13. **Redesigned the LLM judge after blind human validation revealed it was
    badly miscalibrated** (correlation -0.16 against 20 blind human scores).
    The original judge's prompt stated that invented/unverifiable claims
    should be penalized, but it wasn't actually enforcing that — tone and
    topical relevance dominated its scoring instead. Fixed by forcing an
    explicit "list unverifiable claims first, then score" reasoning step
    with a hard cap, which brought within-1-point agreement from 55% to 80%
    and correlation to +0.63 on the same validation set. This is disclosed
    as a finding, not smoothed over, since it materially changes how
    trustworthy the original headline reply-quality number was.

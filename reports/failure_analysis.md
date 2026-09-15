# Failure Analysis — Intent Classifier

Headline: 80.0% accuracy on the 200-example golden set (vs. 22.5% majority-class,
45.5% TF-IDF+LogisticRegression). Macro-avg F1 is 0.77 — meaningfully below
accuracy, because performance is uneven across categories (see taxonomy.md
and the classification report in `golden_set_final_results.csv`).

## Pattern 1: Tone conflated with category ("General Complaint" over-triggers)
General Complaint precision is only 0.58 despite 0.88 recall — the model
over-predicts this category. Four clear examples where a message names a
specific, fixable technical problem but strong negative tone (profanity,
sarcasm) caused a General Complaint prediction instead of the correct
Playback & Technical Issue label:
- A user asking why a bad recommendation played instead of the artist they
  requested, phrased angrily — predicted General Complaint, true label
  Technical (bad recommendation is a fixable, specific issue).
- A user questioning why an unrelated artist was suggested, sharply worded —
  same pattern.
- A user complaining their music is miscategorized into the wrong genre —
  same pattern.
- A user sarcastically comparing audio quality to YouTube — same pattern
  (audio quality is a concrete technical complaint).

**Implication:** the classifier appears to route on emotional tone rather
than on whether a concrete, actionable problem is present in the message.
This is a prompt-level weakness, not a fundamental data problem — worth an
explicit instruction (e.g. "classify based on the underlying issue described,
not the sender's tone") as a follow-up experiment.

## Pattern 2: Content Availability vs. Technical Issue is ambiguous even to a
human labeller
Content Availability F1 is the weakest specific category (0.70). Two
examples: users reporting specific tracks are "greyed out" and won't play.
Greyed-out tracks on Spotify typically signal regional licensing
unavailability (a Content Availability fact) rather than a bug — but this
requires product/domain knowledge the raw customer message doesn't contain
on its own. From the text alone, "I can't play this song" reads identically
whether the cause is a licensing restriction or an app bug.

**Implication:** this is a structural ambiguity in the taxonomy, not purely
a model weakness — a real production system would need to check the
song/catalog status (e.g. via search/retrieval against a catalog API) to
disambiguate reliably, not just classify from message text.

## Related limitation: golden-set labelling consistency
Two near-identical market-availability questions ("when are you arriving in
India" and "when will it start in India") were labelled inconsistently in
the golden set — one Other/Unclear, one implicitly closer to Content
Availability by the taxonomy's own definition. The model classified both as
Content Availability, which is arguably the more internally consistent
reading. This is disclosed here rather than treated as a pure model error,
since the golden set itself has some labelling noise on this exact boundary.

## Pattern 3: Retrieval-grounded generation reused a stale URL from a past
conversation
Before a fix was applied, the reply generator copied a URL verbatim from a
retrieved historical reply (a real link valid for that past customer's
specific ticket) and presented it to a different customer as if it were a
generic, valid link (e.g. "update your card here: [url]"). This is a worse
failure mode than an honest "no information available," since a fabricated-
looking but plausible link could be mistaken for a real, working one.

**Fix applied:** URLs are stripped from all retrieved historical replies
before they enter the generation prompt, and the prompt explicitly instructs
the model never to include a link, even if one appeared in a retrieved
example. Verified fixed on the example that originally surfaced it.

**Implication:** grounding on real historical text is not risk-free —
specific, time/context-bound details (links, ticket numbers, names) need to
be filtered out of retrieved context before use, not just the prose content
trusted wholesale.

*(2 more failure patterns to be added after the escalation-policy stage is
built and evaluated.)*

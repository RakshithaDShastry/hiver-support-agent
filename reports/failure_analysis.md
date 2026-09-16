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

## Pattern 4: The first LLM-judge design was miscalibrated — it didn't
enforce its own stated criteria
Initial judge scores averaged 4.86/5 across 50 replies — suspiciously high.
Blind human validation on a 20-example subset (scored without seeing judge
output) found: exact match 30%, within-1-point agreement 55%, correlation
**-0.16** (essentially no positive relationship, bordering on inverted).

**Root cause:** every 2+ point disagreement had the same shape — a reply
made a confident, specific, unverifiable claim or promise (e.g. "we're
working on it as we speak", "we'll make sure you won't be charged",
"hoping to add it soon", a confidently-stated but ungrounded technical
explanation), and the judge scored it 5 anyway because it sounded polite
and on-topic. The judge's original prompt explicitly said "invents nothing"
should score low, but the model wasn't actually applying that criterion —
tone and topical relevance dominated its impression instead.

**Fix:** redesigned the judge to explicitly list unverifiable claims/promises
as a separate reasoning step *before* scoring, with a hard rule: any
unverifiable claim caps the score at 2, regardless of tone. Re-scored the
same 20 human-validated examples:
- Exact match: 30% → 45%
- Within-1-point agreement: 55% → 80%
- Correlation: -0.16 → +0.63
- Judge mean: 4.85 → 2.90 (much closer to the 3.55 human mean)

**Implication:** an LLM judge given the right criteria in its prompt does
not automatically apply them — telling it to penalize hallucination is not
the same as it actually doing so. Forcing explicit intermediate reasoning
(list the problem, then score) measurably improved reliability. This also
means the original 4.86 headline "reply quality" number was never
trustworthy and should not be cited on its own.

**Known limitation:** re-validation reused the same 20 examples used to
diagnose the problem, which could inflate agreement somewhat versus a fully
independent set — a fresh validation batch would strengthen this further
(listed under "what's next").

**Further finding (second-order miscalibration):** running the fixed (v2)
judge across the full 50-example eval sample produced a bimodal score
distribution — 32 examples scored exactly 2, 16 scored exactly 5, almost
none in between. Inspection showed the "cap at 2 if any unverifiable claim"
rule was firing on honestly-hedged, appropriately uncertain replies (e.g.
"we can't guarantee when or if a specific artist will be added", "no
confirmed launch date yet") — normal, honest customer-support language, not
false promises. This is a real over-triggering bias, distinct from the
original under-triggering problem.

A v3 judge was built to distinguish genuine false-certainty claims from
honest hedging. It correctly fixed the specific over-triggering cases found
(all 4 re-scored 2 → 5) and still correctly caught the genuine overpromising
cases (account merging, refunds — still scored 2). However, re-validating
v3 against the same 20 human-scored examples used for v2 showed **agreement
regressed**: within-1-point agreement dropped from 80% to 50%, correlation
from +0.63 to -0.09. The additional exceptions written into v3's prompt
appear to have given the model room to also excuse some genuinely bad
replies, not just the mild ones.

**Decision:** v2 was kept as the reported judge (best directly-validated
agreement with human judgment), rather than shipping v3 without adequate
re-validation. This means the reported 3.04/5 mean reply-quality score
likely **undercounts true quality somewhat**, since it inherits v2's known
bias toward over-flagging honestly-hedged replies as false-certainty
promises. This is disclosed here rather than smoothed over, since it
directly affects how the headline reply-quality number should be read.

## Pattern 5: Reply generation still overpromises on high-stakes,
account-specific actions despite explicit instructions not to
Across the full 50-example eval, the clearest *genuine* (not judge-artifact)
failures involve the model promising specific outcomes it cannot actually
guarantee, on account-altering actions:
- A customer with 3 duplicate accounts asked for help — the reply promised
  to "verify ownership... merge them or close the duplicates" and that
  password reset "often gets you back in quickly."
- A student-discount rejection with an incorrect charge — the reply
  promised "I can check the status of your subscription and arrange a
  refund," despite no actual authority to guarantee a refund outcome.
- A simple duplicate-account request — the reply promised to "combine your
  listening history and playlists into a single account," which Spotify's
  actual systems cannot do.

**Implication:** these are exactly the account-specific, action-requiring
cases the escalation policy is supposed to catch — and it did correctly
mark 2 of these 3 as ESCALATE. But the *drafted reply itself* still
contains the overpromise, meaning a human reviewer would need to catch and
rewrite it, not just approve/reject it. A more robust design would prevent
the reply generator from making these promises in the first place (e.g. an
explicit list of actions the bot cannot promise: merging accounts, refunds,
guaranteed outcomes) rather than relying entirely on escalation as the only
safety net.

*(5 of 5 failure patterns documented.)*

# Intent Taxonomy — SpotifyCares Support Agent

**Scope decision:** The agent operates on conversation-*opening* messages only
(customer tweets where `in_response_to_tweet_id` is null). Mid-thread replies
were excluded after manual review showed they're frequently uninterpretable
without prior turns (e.g. "Nevermind it works again", "IT WAS A MISTAKE").
This mirrors how a real support agent actually triggers: on new ticket
creation, not on every message in an existing thread.

**Grounding:** Derived from manual review of 80 real customer messages
(40 correctly-scoped openers + 40 from an earlier mixed sample used to spot
the scoping issue itself), sampled from the 26,068 SpotifyCares conversation
openers in the Kaggle Customer Support on Twitter dataset.

## Categories

**Revision note:** During hand-labelling of the 200-example golden set, one
category was split further based on what the examples actually showed:
"Content Availability" (a specific song/album/market not available) was
separated out from general technical bugs, since these have different
resolutions — a content-availability issue is a licensing/catalog fact
to communicate, not something to troubleshoot. The 7 categories below are
the ones actually used to label the golden set and are the taxonomy of
record for this project.

| Intent | Definition | Borderline example (and why it goes here) |
|---|---|---|
| Playback & Technical Issue | Crashes, playback failures, sync bugs, third-party device integration problems | "Sonos inoperable, still controls volume but no access to stations" — technical, not billing, even though it concerns a paid feature |
| Billing & Subscription | Duplicate/incorrect charges, promo/discount not applying, refund requests, upgrade/downgrade, cancellation not processed | Student discount charged but subscription still shows "free" — billing, even though the root cause may be a technical sync failure |
| Account & Access | Login/password issues, identity verification (e.g. SheerID student status), data/playlist migration between accounts, account security concerns | "You verified me but mixed another person's music with mine" — account/identity issue, not technical, since it's about account-data integrity |
| Content Availability | A specific song/album/artist/market not available on the platform | "Why isn't the whole Heathers soundtrack available" — a catalog fact, not a bug to fix |
| Feature Request | Requests for a feature or functionality that doesn't exist yet | "Add Guilty Pleasures presents: Heartthrobs" |
| General Complaint | Real dissatisfaction that isn't a specific, actionable report | "Discover Weekly totally failed this week" — no concrete bug described, just dissatisfaction |
| Other / Unclear | Genuinely insufficient context to classify: rumors, jokes, references to unstated prior issues, non-requests | "please any news about my issue?" — refers to context we don't have |

Note: "How-to / Informational Question" from the original draft taxonomy was
folded into the closest applicable category during labelling rather than kept
separate, since in practice these were rare and often overlapped with Account
& Access or Content Availability questions.

## Known limitation (to carry into the report's "what's misleading about my
headline number" section)
Even after scoping to openers only, roughly 7-8% of the reviewed sample was
still not a genuine, actionable support request (jokes, rumors, vague venting).
Any accuracy metric should be read alongside this — a classifier that performs
worse specifically on this noisy tail is not necessarily a worse classifier
overall.

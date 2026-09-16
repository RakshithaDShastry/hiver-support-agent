"""
Intent taxonomy and few-shot examples used by the classifier and reply
generator. See reports/taxonomy.md for the full grounding and reasoning
behind each category.
"""

CATEGORIES = [
    'Playback & Technical Issue', 'Billing & Subscription', 'Account & Access',
    'Content Availability', 'Feature Request', 'General Complaint', 'Other / Unclear'
]

TAXONOMY_DEFINITIONS = """
- Playback & Technical Issue: Crashes, playback failures, sync bugs, third-party device integration problems.
- Billing & Subscription: Duplicate/incorrect charges, promo not applying, refunds, upgrade/downgrade, cancellation issues.
- Account & Access: Login/password, identity verification, data/playlist migration, how-to and policy questions.
- Content Availability: A specific song/album/artist/market not available on the platform.
- Feature Request: Wants a feature or functionality that doesn't exist yet.
- General Complaint: Real dissatisfaction with no specific actionable bug named.
- Other / Unclear: Genuinely insufficient context — rumors, jokes, references to unstated prior issues.
"""

# Hand-labelled, deliberately kept SEPARATE from the golden evaluation set
# (verified by tweet_id exclusion at collection time — see decision_log.md
# entry 8) so the classifier is never evaluated on examples it was shown.
FEWSHOT_EXAMPLES = [
    {'text': '@115888 help me all my music is gone 😭', 'label': 'Playback & Technical Issue'},
    {'text': '@115888 where is reputation', 'label': 'Content Availability'},
    {'text': '@SpotifyCares  my old email has been deleted and I was wondering how I can change the email linked with my account', 'label': 'Account & Access'},
    {'text': 'And we’re back to Spotify desktop not working again this last week, worked for 3 days on a new iMac, and then stops searching or showing results. @SpotifyCares', 'label': 'Playback & Technical Issue'},
    {'text': '@SpotifyCares where is Red Velvet’s new Album :( Peek-A-Boo', 'label': 'Content Availability'},
    {'text': '@SpotifyCares Hey! I need to be listening to one song for 30 seconds so it gets one stream counted. Right? I can skip after that?', 'label': 'Account & Access'},
    {'text': 'Is @115888 not available in Taiwan?', 'label': 'Content Availability'},
    {'text': 'Yo, how does a guy register for @115888 ?', 'label': 'Account & Access'},
    {'text': "@115888 @SpotifyCares \n\nDoes streaming still count if it's offline??", 'label': 'Account & Access'},
    {'text': '@115888 hey guys i am having some trouble canceling an account is there any way i could call or email you for help?', 'label': 'Billing & Subscription'},
    {'text': "@spotifycares i have been upgraded to family membership, but didn't ask for it. I have downgraded myself, but how can i get a refund please?", 'label': 'Billing & Subscription'},
    {'text': "Long term @115888 premium user here. Is there any timeline to integrate lyrics in the app? I'd put up with an ad for this feature.", 'label': 'Feature Request'},
    {'text': "@SpotifyCares any reason why Bowie tracks wouldn't be playing at all for the past 48 hours?", 'label': 'Playback & Technical Issue'},
    {'text': 'Hi @115888, I was just wondering why your service has turned into absolute dogshit in the last month?', 'label': 'General Complaint'},
    {'text': '@SpotifyCares please any news about my issue?', 'label': 'Other / Unclear'},
]


def build_fewshot_block(examples=FEWSHOT_EXAMPLES):
    lines = [f"Message: {ex['text']}\nIntent: {ex['label']}" for ex in examples]
    return "\n\n".join(lines)

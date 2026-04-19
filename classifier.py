"""
Scope SEO Keyword Classifier
Processes raw Reddit posts and Google search snippets,
matches against 80+ scope/optic keywords, classifies intent.
"""

SCOPE_KEYWORDS = [
    # Generic
    'scope', 'riflescope', 'optic', 'optics', 'glass',
    # Brands
    'vortex', 'nightforce', 'leupold', 'zeiss', 'swarovski',
    'schmidt', 'bender', 'kahles', 'march', 'tract', 'burris',
    'bushnell', 'steiner', 'meopta', 'primary arms', 'swfa',
    'athlon', 'sig sauer', 'us optics', 'zco', 'holosun',
    'trijicon', 'arken',
    # Models / lines
    'razor', 'atacr', 'mark 5', 'vx3', 'vx-3', 'sx4',
    # Technical
    'moa', 'mrad', 'ffp', 'sfp', 'focal plane', 'reticle',
    'turret', 'parallax', 'eye relief', 'magnification',
    'zero', 'zeroing', 'dope', 'mil',
    'first focal', 'second focal',
    # Intent phrases
    'best scope', 'scope for', 'scope under',
    'scope recommendation', 'scope review', 'scope vs',
    'which scope', 'scope help',
    # Competition
    'prs scope', 'benchrest scope', 'long range scope',
    'hunting scope', 'nrl22', 'precision rifle',
    # Night / thermal
    'night vision', 'thermal scope', 'thermal optic',
]

# Normalise to lowercase once
SCOPE_KEYWORDS_LOWER = [k.lower() for k in SCOPE_KEYWORDS]


def match_keywords(text: str) -> list[str]:
    """Return list of matched keywords found in text."""
    text_lower = text.lower()
    return [kw for kw in SCOPE_KEYWORDS_LOWER if kw in text_lower]


def classify_intent(title: str) -> str:
    """
    Classify SEO intent from post title.

    Returns one of: 'transactional', 'commercial', 'informational', 'navigational'
    """
    t = title.lower()

    if any(x in t for x in [
        'buy', 'purchase', 'deal', 'sale', 'coupon',
        'cheapest', 'price', 'cost', 'where to get',
    ]):
        return 'transactional'

    if any(x in t for x in [
        'best', 'recommend', 'review', 'worth', 'vs',
        'comparison', 'which', 'should i', 'top', 'or', 'between',
    ]):
        return 'commercial'

    if any(x in t for x in [
        'how', 'what is', 'explain', 'difference', 'why',
        'guide', 'tutorial', 'help', 'upgrade', 'budget',
    ]):
        return 'informational'

    # Brand name only → navigational
    if any(x in t for x in [
        'vortex', 'nightforce', 'leupold', 'zeiss', 'swarovski',
        'kahles', 'march', 'arken', 'athlon', 'sig sauer', 'holosun',
    ]):
        return 'navigational'

    return 'informational'


def process_posts(posts: list[dict]) -> list[dict]:
    """
    Filter and enrich raw post dicts.

    Each post dict should have at minimum: title, body (optional).
    Returns only posts that match at least one scope keyword.
    """
    results = []
    for post in posts:
        text = f"{post.get('title', '')} {post.get('body', '')}"
        matched = match_keywords(text)
        if matched:
            post['matched_keywords'] = matched
            post['intent'] = classify_intent(post.get('title', ''))
            post['is_question'] = post.get('title', '').strip().endswith('?')
            results.append(post)
    return results


def build_summary(posts: list[dict]) -> dict:
    """Build keyword_counts, top_keywords, intent_breakdown from processed posts."""
    from collections import Counter

    kw_counter: Counter = Counter()
    intent_counter: Counter = Counter()

    for post in posts:
        for kw in post.get('matched_keywords', []):
            kw_counter[kw] += 1
        intent_counter[post.get('intent', 'informational')] += 1

    return {
        'keyword_counts': dict(kw_counter),
        'top_keywords': kw_counter.most_common(20),
        'intent_breakdown': dict(intent_counter),
        'trending_questions': sorted(
            [p for p in posts if p.get('score', 0) or p.get('num_comments', 0)],
            key=lambda p: (p.get('score', 0) or 0) + (p.get('num_comments', 0) or 0) * 2,
            reverse=True,
        )[:10],
    }


if __name__ == '__main__':
    import json, sys

    if len(sys.argv) < 2:
        print("Usage: python classifier.py input.json")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        raw_posts = json.load(f)

    processed = process_posts(raw_posts if isinstance(raw_posts, list) else raw_posts.get('posts', []))
    summary = build_summary(processed)

    print(f"Matched posts: {len(processed)}")
    print(f"Top keywords: {summary['top_keywords'][:5]}")
    print(f"Intent breakdown: {summary['intent_breakdown']}")

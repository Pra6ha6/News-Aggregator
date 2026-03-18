import nltk
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
import re
from collections import defaultdict, Counter

# Ensure nltk resources are available
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt')
    nltk.download('punkt_tab')

def find_top_topics(articles, n=4):
    """Identifies highly specific N topics using multi-word frequency."""
    if not articles:
        return []
    all_titles = " ".join([(a.get('title', '') or '').lower() for a in articles])
    words = re.findall(r'\b[a-z]{4,}\b', all_titles)
    stopwords = {
        'today', 'news', 'live', 'india', 'world', 'times', 'update', 'latest', 'reported',
        'makes', 'pushes', 'deal', 'ties', 'over', 'with', 'from', 'into', 'after', 'against',
        'says', 'will', 'about', 'more', 'this', 'that', 'been', 'were'
    }
    meaningful_words = [w for w in words if w not in stopwords]
    word_counts = Counter(meaningful_words)
    topics = []
    candidates = [w for w, count in word_counts.most_common(12)]
    for word in candidates:
        if any(word in t for t in topics): continue
        companions = []
        for a in articles:
            t = (a.get('title', '') or '').lower()
            if word in t:
                parts = re.findall(r'\b[a-z]{4,}\b', t)
                companions.extend([p for p in parts if p != word and p not in stopwords])
        if companions:
            pair = Counter(companions).most_common(1)[0][0]
            topics.append(f"{word} {pair}")
        else:
            topics.append(word)
        if len(topics) >= n: break
    return topics

def deduplicate_sources(articles, topic_query=None):
    """Enforces source diversity and filters for topic relevance."""
    seen_sources = set()
    diverse_articles = []
    keywords = set(topic_query.lower().split()) if topic_query else set()
    for a in articles:
        title = (a.get('title', '') or '').lower()
        if keywords and not any(k in title for k in keywords):
            continue
        s_name = a.get('source', {}).get('name', 'Unknown')
        if s_name not in seen_sources:
            diverse_articles.append(a)
            seen_sources.add(s_name)
    return diverse_articles if diverse_articles else articles[:3]

def extract_key_facts(text):
    """Extracts unique proper nouns and entities as key facts."""
    # Light-weight regex entity extraction (Proper nouns, Numbers, $ amounts)
    potential_facts = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b|\$\d+(?:\.\d+)?m?b?|\d{1,3}%\b', text)
    noise = {'The', 'This', 'That', 'News', 'Today', 'Live', 'India', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'}
    unique_facts = sorted(list(set([f for f in potential_facts if f not in noise])), key=len, reverse=True)
    return unique_facts[:5]

def triangulate_cluster(cluster_articles, topic_query=None):
    """Synthesizes a structured Factual Core with separate points and facts."""
    if not cluster_articles:
        return None
    diverse_pool = deduplicate_sources(cluster_articles, topic_query)
    
    # 1. Metatada & Attribution
    contribution_sources = [{"name": a.get('source', {}).get('name', 'Source'), "url": a.get('url', '#')} for a in diverse_pool]
    
    # 2. Extract Data
    descriptions = [art.get("description", "") or "" for art in diverse_pool if art.get("description")]
    titles = [art.get("title", "") for art in diverse_pool if art.get("title")]
    full_text = " ".join(descriptions + titles)
    
    # 3. Summarize into Points
    points = []
    try:
        parser = PlaintextParser.from_string(full_text, Tokenizer("english"))
        summarizer = LexRankSummarizer()
        summary_sentences = summarizer(parser.document, 3)
        points = [str(s).strip() for s in summary_sentences if len(str(s)) > 30]
        # Basic narrative connector logic
        if len(points) > 1: points[1] = "Furthermore, " + points[1]
    except:
        points = titles[:2]

    # 4. Extract Key Facts
    key_facts = extract_key_facts(full_text)
    
    # Check depth
    depth = "Synthesized Core" if len(points) >= 2 else "Headline Digest"
    bias_score = max(5, 100 - (len(set([s['name'] for s in contribution_sources])) * 20))
    
    return {
        "title": titles[0] if titles else "Major Story",
        "points": points,
        "facts": key_facts,
        "bias_score": bias_score,
        "depth": depth,
        "sources": contribution_sources
    }

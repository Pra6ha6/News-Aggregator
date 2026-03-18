import nltk
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from deep_translator import GoogleTranslator
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

def safe_translate(text):
    """Translates text to English if needed."""
    if not text or len(text) < 10: return text, False
    try:
        # Check if contains non-ASCII characters as a proxy for non-English
        if any(ord(char) > 127 for char in text[:100]):
            translated = GoogleTranslator(source='auto', target='en').translate(text)
            return translated, True
    except:
        pass
    return text, False

def extract_key_facts(text):
    potential_facts = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b|\$\d+(?:\.\d+)?m?b?|\d{1,3}%\b', text)
    noise = {'The', 'This', 'That', 'News', 'Today', 'Live', 'India', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'}
    unique_facts = sorted(list(set([f for f in potential_facts if f not in noise])), key=len, reverse=True)
    return unique_facts[:5]

def triangulate_cluster(cluster_articles, topic_query=None):
    if not cluster_articles: return None
    diverse_pool = deduplicate_sources(cluster_articles, topic_query)
    
    contribution_sources = []
    any_translated = False
    
    processed_texts = []
    processed_titles = []
    
    for art in diverse_pool:
        raw_title = art.get('title', '')
        raw_desc = art.get('description', '')
        
        title, t1 = safe_translate(raw_title)
        desc, t2 = safe_translate(raw_desc)
        
        if t1 or t2: any_translated = True
        
        processed_titles.append(title)
        processed_texts.append(desc or title)
        
        contribution_sources.append({
            "name": art.get('source', {}).get('name', 'Source'),
            "url": art.get('url', '#'),
            "translated": t1 or t2
        })
    
    full_text = " ".join(processed_texts)
    
    points = []
    try:
        parser = PlaintextParser.from_string(full_text, Tokenizer("english"))
        summarizer = LexRankSummarizer()
        summary_sentences = summarizer(parser.document, 3)
        points = [str(s).strip() for s in summary_sentences if len(str(s)) > 30]
        if len(points) > 1: points[1] = "Additionally, " + points[1]
    except:
        points = processed_titles[:2]

    key_facts = extract_key_facts(full_text)
    depth = "Universal Digest" if any_translated else "Synthesized Core"
    bias_score = max(5, 100 - (len(set([s['name'] for s in contribution_sources])) * 20))
    
    return {
        "title": processed_titles[0] if processed_titles else "Top Story",
        "points": points,
        "facts": key_facts,
        "bias_score": bias_score,
        "depth": depth,
        "translated": any_translated,
        "sources": contribution_sources
    }

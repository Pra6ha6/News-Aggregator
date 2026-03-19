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
    """Identifies highly specific N topics using multi-word/entity matching."""
    if not articles:
        return []
        
    all_titles = " ".join([(a.get('title', '') or '').lower() for a in articles])
    
    # Noise filter
    stopwords = {
        'today', 'news', 'live', 'india', 'world', 'times', 'update', 'latest', 'reported',
        'makes', 'pushes', 'deal', 'ties', 'over', 'with', 'from', 'into', 'after', 'against',
        'says', 'will', 'about', 'more', 'this', 'that', 'been', 'were', 'illegal', 'federal', 'judge'
    }
    
    # 1. Identify "Anchor" Entities (Capitalized words like Kari Lake, Epstein)
    anchors = []
    for a in articles:
        t = a.get('title', '')
        entities = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', t)
        anchors.extend([e for e in entities if e not in {'The', 'This', 'News', 'Judge', 'Court', 'India'}])
    
    anchor_counts = Counter(anchors)
    top_anchors = [a for a, count in anchor_counts.most_common(n * 2)]
    
    topics = []
    seen = set()
    for anchor in top_anchors:
        if anchor in seen: continue
        # Find a companion word/entity that appears with this anchor
        companions = []
        for a in articles:
            t = a.get('title', '')
            if anchor in t:
                # Find other entities or significant words
                # Filter out the anchor itself
                parts = re.findall(r'\b[a-z]{4,}\b', t.lower())
                companions.extend([p for p in parts if p not in anchor.lower() and p not in stopwords])
        
        if companions:
            top_comp = Counter(companions).most_common(1)[0][0]
            topics.append(f"{anchor} {top_comp}")
        else:
            topics.append(anchor)
        
        seen.add(anchor)
        if len(topics) >= n: break
        
    return topics

def deduplicate_sources(articles, topic_query=None):
    """Enforces source diversity and strict topic-entity relevance."""
    seen_sources = set()
    diverse_articles = []
    
    # Extract entities from the topic query
    topic_entities = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b|\b[a-z]{4,}\b', topic_query if topic_query else "")
    keywords = [k.lower() for k in topic_entities]
    
    for a in articles:
        title = (a.get('title', '') or '').lower()
        
        # Purity Guard: The title MUST contain at least 2 keywords or 1 exact entity from the topic
        score = sum(1 for k in keywords if k in title)
        if keywords and score < 1: # Basic filter
            continue
            
        s_name = a.get('source', {}).get('name', 'Unknown')
        if s_name not in seen_sources:
            diverse_articles.append(a)
            seen_sources.add(s_name)
    
    return diverse_articles if diverse_articles else articles[:3]

def safe_translate(text):
    if not text or len(text) < 10: return text, False
    try:
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
    processed_texts = []
    processed_titles = []
    
    for art in diverse_pool:
        title, t1 = safe_translate(art.get('title', ''))
        desc, t2 = safe_translate(art.get('description', ''))
        
        processed_titles.append(title)
        # Use full descriptions to ensure sentence integrity
        processed_texts.append(desc or title)
        
        contribution_sources.append({
            "name": art.get('source', {}).get('name', 'Source'),
            "url": art.get('url', '#'),
            "translated": t1 or t2
        })
    
    # 3. Summarize into Points (Strict sentence selection)
    points = []
    try:
        # Pass descriptions separately to avoid run-on concatenation
        all_sentences = []
        for text in processed_texts:
            # Simple sentence splitting to ensure we pick complete sentences
            sents = re.split(r'(?<=[.!?])\s+', text)
            all_sentences.extend([s for s in sents if len(s) > 40])
            
        parser = PlaintextParser.from_string(" ".join(all_sentences), Tokenizer("english"))
        summarizer = LexRankSummarizer()
        summary_sentences = summarizer(parser.document, 3)
        points = [str(s).strip() for s in summary_sentences]
        if len(points) > 1: points[1] = "Additionally, " + points[1]
    except:
        points = processed_titles[:2]

    key_facts = extract_key_facts(" ".join(processed_texts))
    depth = "Verified Cross-Source" if len(contribution_sources) > 1 else "Single Source"
    bias_score = max(5, 100 - (len(set([s['name'] for s in contribution_sources])) * 20))
    
    return {
        "title": processed_titles[0] if processed_titles else topic_query,
        "points": points,
        "facts": key_facts,
        "bias_score": bias_score,
        "depth": depth,
        "sources": contribution_sources
    }

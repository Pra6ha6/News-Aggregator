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
    
    # Extended noise filter
    stopwords = {
        'today', 'news', 'live', 'india', 'world', 'times', 'update', 'latest', 'reported',
        'makes', 'pushes', 'deal', 'ties', 'over', 'with', 'from', 'into', 'after', 'against',
        'says', 'will', 'about', 'more', 'this', 'that', 'been', 'were'
    }
    
    meaningful_words = [w for w in words if w not in stopwords]
    word_counts = Counter(meaningful_words)
    
    # We want word PAIRS that appear together
    topics = []
    candidates = [w for w, count in word_counts.most_common(12)]
    
    for word in candidates:
        if any(word in t for t in topics): continue
        
        # Find the most common companion for this word in titles
        companions = []
        for a in articles:
            t = (a.get('title', '') or '').lower()
            if word in t:
                parts = re.findall(r'\b[a-z]{4,}\b', t)
                companions.extend([p for p in parts if p != word and p not in stopwords])
        
        if companions:
            pair = Counter(companions).most_common(1)[0][0]
            topic_query = f"{word} {pair}"
            topics.append(topic_query)
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
        # Relevance Guard: At least one topic keyword must be in the title
        if keywords and not any(k in title for k in keywords):
            continue
            
        s_name = a.get('source', {}).get('name', 'Unknown')
        if s_name not in seen_sources:
            diverse_articles.append(a)
            seen_sources.add(s_name)
    
    # Final fallback: if relevance guard was too strict, take top 3 original
    if not diverse_articles and articles:
        return articles[:3]
        
    return diverse_articles

def triangulate_cluster(cluster_articles, topic_query=None):
    """Synthesizes a distinct Factual Core for a specific topic."""
    if not cluster_articles:
        return None
        
    diverse_pool = deduplicate_sources(cluster_articles, topic_query)
    
    contribution_sources = []
    for art in diverse_pool:
        s_name = art.get('source', {}).get('name', 'Source')
        s_url = art.get('url', '#')
        contribution_sources.append({"name": s_name, "url": s_url})

    descriptions = [art.get("description", "") or "" for art in diverse_pool if art.get("description")]
    titles = [art.get("title", "") for art in diverse_pool if art.get("title")]
    
    all_text = " ".join(descriptions + titles)
    
    try:
        if len(all_text) < 200 or len(descriptions) < 2:
             # Improved separator for Headline Digest
             factual_core = " • ".join(titles[:3])
             depth = "Headline Point"
        else:
            parser = PlaintextParser.from_string(all_text, Tokenizer("english"))
            summarizer = LexRankSummarizer()
            summary_sentences = summarizer(parser.document, 2)
            factual_core = " ".join([str(s) for s in summary_sentences])
            depth = "Synthesized Core"
    except:
        factual_core = titles[0] if titles else "Events update."
        depth = "Summary Pending"

    bias_score = max(5, 100 - (len(set([s['name'] for s in contribution_sources])) * 20))
    
    return {
        "title": titles[0] if titles else "Top Story",
        "factual_core": factual_core,
        "bias_score": bias_score,
        "depth": depth,
        "sources": contribution_sources
    }

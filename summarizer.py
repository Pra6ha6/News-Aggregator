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
    """Identifies the top N most frequent story topics using keyword frequency."""
    if not articles:
        return []
        
    all_titles = " ".join([(a.get('title', '') or '').lower() for a in articles])
    # Extract keywords (4+ letters)
    words = re.findall(r'\b[a-z]{4,}\b', all_titles)
    
    # Filter out common news padding but keep meaningful names
    stopwords = {'today', 'news', 'live', 'india', 'world', 'times', 'update', 'latest', 'reported'}
    meaningful_words = [w for w in words if w not in stopwords]
    
    word_counts = Counter(meaningful_words)
    top_keywords = [w for w, count in word_counts.most_common(n * 2)]
    
    # Group keywords that often appear together into "Topics"
    topics = []
    seen = set()
    for word in top_keywords:
        if word in seen: continue
        # Find associated words in titles that contain this word
        assocs = []
        for a in articles:
            t = (a.get('title', '') or '').lower()
            if word in t:
                assocs.extend(re.findall(r'\b[a-z]{4,}\b', t))
        
        most_common_assoc = Counter([w for w in assocs if w != word and w not in stopwords]).most_common(1)
        topic_str = f"{word} {most_common_assoc[0][0]}" if most_common_assoc else word
        topics.append(topic_str)
        seen.add(word)
        if most_common_assoc: seen.add(most_common_assoc[0][0])
        if len(topics) >= n: break
        
    return topics

def deduplicate_sources(articles):
    """Enforces source diversity by keeping only 1 article per unique provider."""
    seen_sources = set()
    diverse_articles = []
    for a in articles:
        s_name = a.get('source', {}).get('name', 'Unknown')
        if s_name not in seen_sources:
            diverse_articles.append(a)
            seen_sources.add(s_name)
    return diverse_articles

def triangulate_cluster(cluster_articles):
    """Triangulates a cluster into a concise 2-3 sentence Factual Core."""
    if not cluster_articles:
        return None
        
    # Enforce Source Diversity
    diverse_pool = deduplicate_sources(cluster_articles)
    
    contribution_sources = []
    for art in diverse_pool:
        s_name = art.get('source', {}).get('name', 'Source')
        s_url = art.get('url', '#')
        contribution_sources.append({"name": s_name, "url": s_url})

    # Content synthesis
    descriptions = [art.get("description", "") or "" for art in diverse_pool if art.get("description")]
    titles = [art.get("title", "") for art in diverse_pool if art.get("title")]
    
    all_text = " ".join(descriptions + titles)
    
    try:
        if len(all_text) < 150:
             factual_core = titles[0] if titles else "Events unfolding."
             depth = "Low"
        else:
            parser = PlaintextParser.from_string(all_text, Tokenizer("english"))
            summarizer = LexRankSummarizer()
            # Enforce 2 sentences for conciseness
            summary_sentences = summarizer(parser.document, 2)
            factual_core = " ".join([str(s) for s in summary_sentences])
            depth = "High" if len(summary_sentences) >= 2 else "Medium"
    except:
        factual_core = titles[0] if titles else "Update pending."
        depth = "Low"

    bias_score = max(5, 100 - (len(set([s['name'] for s in contribution_sources])) * 20))
    
    return {
        "title": titles[0] if titles else "Top Story",
        "factual_core": factual_core,
        "bias_score": bias_score,
        "depth": depth,
        "sources": contribution_sources
    }

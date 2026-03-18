import nltk
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
import re
from collections import defaultdict

# Ensure nltk resources are available
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt')
    nltk.download('punkt_tab')

def cluster_stories(articles, num_clusters=4):
    """Refined keyword-based clustering of articles into stories."""
    if not articles:
        return []
        
    if len(articles) <= 5:
        return [articles]
        
    clusters = defaultdict(list)
    for art in articles:
        title = (art.get('title', '') or '').lower()
        words = re.findall(r'\b[a-z]{4,}\b', title)
        key = " ".join(sorted(words[:2])) if words else "trending"
        clusters[key].append(art)
    
    final_clusters = []
    others = []
    for c in clusters.values():
        if len(c) >= 2:
            final_clusters.append(c)
        else:
            others.extend(c)
            
    if others:
        final_clusters.append(others)
    
    sorted_clusters = sorted(final_clusters, key=len, reverse=True)
    return sorted_clusters[:num_clusters]

def triangulate_cluster(cluster_articles):
    """Triangulates a cluster with content-aware depth and attribution."""
    if not cluster_articles:
        return None
        
    # Extract sources early for attribution
    contribution_sources = []
    for art in cluster_articles:
        s_name = art.get('source', {}).get('name', 'Unknown Source')
        s_url = art.get('url', '#')
        contribution_sources.append({"name": s_name, "url": s_url})

    # Combine text, identifying depth
    descriptions = [art.get("description", "") or "" for art in cluster_articles if art.get("description")]
    titles = [art.get("title", "") for art in cluster_articles if art.get("title")]
    
    all_text = " ".join(descriptions + titles)
    
    is_sparse = len(descriptions) < (len(cluster_articles) / 2)
    
    if not all_text.strip() or len(all_text) < 100:
        factual_core = "Headline Digest: " + " | ".join(titles[:3])
        depth_label = "Low (Headlines only)"
    else:
        try:
            parser = PlaintextParser.from_string(all_text, Tokenizer("english"))
            summarizer = LexRankSummarizer()
            summary_sentences = summarizer(parser.document, 3)
            factual_core = " ".join([str(s) for s in summary_sentences])
            depth_label = "High (Detailed synthesis)" if not is_sparse else "Medium (Mixed depth)"
        except:
            factual_core = titles[0] if titles else "Events in progress..."
            depth_label = "Low (Fallback)"

    # Bias score (based on source diversity)
    unique_sources = set([s['name'] for s in contribution_sources])
    bias_score = max(5, 100 - (len(unique_sources) * 20))
    
    return {
        "title": titles[0] if titles else "Major Story",
        "factual_core": factual_core,
        "bias_score": bias_score,
        "depth": depth_label,
        "sources": contribution_sources
    }

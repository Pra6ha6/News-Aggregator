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
        return [articles] # Too few to cluster, return as one story
        
    clusters = defaultdict(list)
    for art in articles:
        title = (art.get('title', '') or '').lower()
        # Extract main keywords (3+ chars, excluding common words)
        words = re.findall(r'\b[a-z]{4,}\b', title)
        # Sort words to create a stable key
        key = " ".join(sorted(words[:2])) if words else "trending"
        clusters[key].append(art)
    
    # Merge very small clusters into a "Catch-all" if they are too small
    final_clusters = []
    others = []
    for c in clusters.values():
        if len(c) >= 2:
            final_clusters.append(c)
        else:
            others.extend(c)
            
    if others:
        final_clusters.append(others)
    
    # Sort clusters by size and take top N
    sorted_clusters = sorted(final_clusters, key=len, reverse=True)
    return sorted_clusters[:num_clusters]

def triangulate_cluster(cluster_articles):
    """Triangulates a specific cluster of articles using LexRank."""
    if not cluster_articles:
        return None
        
    all_text = " ".join([(art.get("description", "") or art.get("title", "") or "") for art in cluster_articles])
    
    if not all_text.strip() or len(all_text) < 50:
        return {
            "title": cluster_articles[0].get('title', 'Breaking News'),
            "factual_core": cluster_articles[0].get('description', 'Detailed report pending from multiple sources.'),
            "bias_score": 50,
            "sources": cluster_articles
        }

    # Summarization
    try:
        parser = PlaintextParser.from_string(all_text, Tokenizer("english"))
        summarizer = LexRankSummarizer()
        summary_sentences = summarizer(parser.document, 3)
        factual_core = " ".join([str(s) for s in summary_sentences])
    except:
        factual_core = cluster_articles[0].get('description', 'Synthesis in progress...')

    # Basic bias score based on source diversity
    sources = set([art.get('source', {}).get('name', 'Unknown') for art in cluster_articles])
    bias_score = max(10, 100 - (len(sources) * 20)) 
    
    return {
        "title": cluster_articles[0].get('title', 'Major Story Update'),
        "factual_core": factual_core or "Factual core synthesis complete.",
        "bias_score": bias_score,
        "sources": cluster_articles
    }

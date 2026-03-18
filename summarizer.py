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
    """Simple keyword-based clustering of articles into stories."""
    if not articles:
        return []
        
    clusters = defaultdict(list)
    for art in articles:
        title = art.get('title', '').lower()
        # Extract main keywords (very simple heuristic)
        words = re.findall(r'\w{5,}', title) 
        key = " ".join(sorted(words[:2])) if words else "other"
        clusters[key].append(art)
    
    # Sort clusters by size and take top N
    sorted_clusters = sorted(clusters.values(), key=len, reverse=True)
    return sorted_clusters[:num_clusters]

def triangulate_cluster(cluster_articles):
    """Triangulates a specific cluster of articles using LexRank."""
    all_text = " ".join([art.get("description", "") or art.get("title", "") for art in cluster_articles])
    
    if not all_text.strip():
        return None

    # Summarization
    parser = PlaintextParser.from_string(all_text, Tokenizer("english"))
    summarizer = LexRankSummarizer()
    summary_sentences = summarizer(parser.document, 3)
    factual_core = " ".join([str(s) for s in summary_sentences])
    
    # Basic bias score based on source diversity
    sources = set([art['source']['name'] for art in cluster_articles])
    bias_score = max(0, 100 - (len(sources) * 20)) # More sources = lower bias
    
    return {
        "title": cluster_articles[0]['title'], # Representative title
        "factual_core": factual_core,
        "bias_score": bias_score,
        "sources": cluster_articles
    }

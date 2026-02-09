import numpy as np
import re
from typing import List, Set

def calculate_cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    if not v1 or not v2:
        return 0.0
    a = np.array(v1)
    b = np.array(v2)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))

def tokenize(text: str) -> Set[str]:
    """Simple tokenizer that lowers and removes non-alphanumeric chars."""
    if not text:
        return set()
    return set(re.findall(r'\w+', text.lower()))

def calculate_keyword_overlap(text1: str, text2: str) -> float:
    """Calculate Jaccard similarity (keyword overlap) between two texts."""
    set1 = tokenize(text1)
    set2 = tokenize(text2)
    
    if not set1 and not set2:
        return 1.0
    
    if not set1 or not set2:
        return 0.0
    
    intersection = set1.intersection(set2)
    union = set1.union(set2)
    
    return len(intersection) / len(union)

def calculate_bleu_score(reference: str, candidate: str) -> float:
    """
    Very simple BLEU-like n-gram overlap.
    Currently implements unigram and bigram overlap.
    """
    def get_ngrams(text: str, n: int):
        tokens = re.findall(r'\w+', text.lower())
        if len(tokens) < n:
            return set()
        return set(tuple(tokens[i:i+n]) for i in range(len(tokens)-n+1))

    ref_1grams = get_ngrams(reference, 1)
    cand_1grams = get_ngrams(candidate, 1)
    
    if not cand_1grams:
        return 0.0
    
    p1 = len(cand_1grams.intersection(ref_1grams)) / len(cand_1grams)
    
    ref_2grams = get_ngrams(reference, 2)
    cand_2grams = get_ngrams(candidate, 2)
    
    if not cand_2grams:
        p2 = p1 # Fallback to unigram if too short
    else:
        p2 = len(cand_2grams.intersection(ref_2grams)) / len(cand_2grams)
        
    return (p1 + p2) / 2.0

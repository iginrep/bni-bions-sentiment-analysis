from __future__ import annotations

import re
from pipeline.sentiment.rules import TOPIC_RULES

__all__ = ["TOPIC_RULES", "detect_topics"]


def detect_topics(text: str) -> list[str]:
    """
    Detect topics in a text based on keyword rules.
    Returns a list of matching topic names.
    """
    if not text:
        return []
    
    # Normalize text to lowercase
    text_lower = text.lower()
    
    # Tokenize the text into individual words
    words = set(re.findall(r'\b\w+\b', text_lower))
    
    matched_topics = []
    for topic, keywords in TOPIC_RULES.items():
        for kw in keywords:
            # Handle multi-word keywords or keywords with hyphen/special characters
            if " " in kw or "-" in kw:
                if kw in text_lower:
                    matched_topics.append(topic)
                    break
            else:
                if kw in words:
                    matched_topics.append(topic)
                    break
                    
    return matched_topics


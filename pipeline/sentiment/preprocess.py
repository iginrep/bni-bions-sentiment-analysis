# Re-export from the comprehensive preprocessing module
# Kept for backward compatibility — classifier.py imports clean_text from here
from functools import partial
from pipeline.sentiment.preprocessing import preprocess  # noqa: F401

# clean_text(text) → preprocess(text, mode="rule_based")
clean_text = partial(preprocess, mode="rule_based")

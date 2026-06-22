# Re-export from the comprehensive preprocessing module
# Kept for backward compatibility — clean_text defaults to indobert mode
from functools import partial
from pipeline.sentiment.preprocessing import preprocess  # noqa: F401

# clean_text(text) → preprocess(text, mode="indobert")
clean_text = partial(preprocess, mode="indobert")

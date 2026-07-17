"""
Configuration for NVIDIA LLM.
Optimized for token efficiency and rate limit management.
"""

MODEL_NAME = "meta/llama-3.1-70b-instruct"
TEMPERATURE = 0.2
MAX_TOKENS = 800  # Reduced from 1024 to optimize token usage while maintaining quality
TOP_P = 0.9

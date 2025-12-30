import yaml
import os
from functools import lru_cache

# Path relative to this file: ../config/prompts.yaml
PROMPTS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "prompts.yaml")

@lru_cache()
def load_prompts():
    """Load prompts from the YAML configuration file."""
    if not os.path.exists(PROMPTS_PATH):
        # Fallback for different CWD scenarios or testing
        # Try absolute path based on known structure if relative fails? 
        # For now, assume structure is consistent.
        raise FileNotFoundError(f"Prompts file not found at {PROMPTS_PATH}")
    
    with open(PROMPTS_PATH, "r") as f:
        return yaml.safe_load(f)

def get_system_prompt():
    """Retrieve the system prompt configuration."""
    prompts = load_prompts()
    return prompts.get("system", {})

def get_fallback_prompts():
    """Retrieve fallback message prompts."""
    prompts = load_prompts()
    return prompts.get("fallback", {})

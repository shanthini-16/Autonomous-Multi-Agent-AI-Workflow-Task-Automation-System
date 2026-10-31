import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

class Config:
    HOST = os.environ.get("HOST", "127.0.0.1")
    PORT = int(os.environ.get("PORT", 5000))
    DEBUG = os.environ.get("DEBUG", "False").lower() in ("true", "1")
    
    # Task Orchestration settings
    MAX_RETRIES = int(os.environ.get("MAX_RETRIES", 3))
    TOOL_TIMEOUT_SECONDS = int(os.environ.get("TOOL_TIMEOUT_SECONDS", 15))
    VERIFICATION_THRESHOLD_SCORE = float(os.environ.get("VERIFICATION_THRESHOLD_SCORE", 75.0))
    
    # LLM & AI Settings
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
    USE_HYBRID_ENGINE = True # Uses intelligent agentic heuristic engine, augmented with generative AI when keys are present
    
    # Colors defined in specification for consistent server-side reports
    MOCHA_BROWN = "#5B4632"
    CHAMPAGNE_GOLD = "#F4D9A0"
    BURNT_AMBER = "#C87926"

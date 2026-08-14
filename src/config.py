import logging
from pathlib import Path

# Base Paths (Relative to project root)
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

# Ensure required directories exist automatically
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Input & Output File Paths
SHORTLIST_CSV = DATA_DIR / "multinational_brand_shortlist.csv"
CLEANED_CSV = DATA_DIR / "multinational_brand_cleaned.csv"
BENCHMARK_JSON = DATA_DIR / "benchmark_candidates.json"
LOG_FILE = LOGS_DIR / "phase1.log"

# Brand Typo Mapping Dictionary
BRAND_REPLACEMENTS = {
    "HERSHYEYS": "HERSHEYS",
    "BOUENVITA": "CADBURY",
    "CADBERY BORNVITA": "CADBURY",
    "MOUMTAIN DEW": "MOUNTAIN DEW",
    "DR OETKERS FUNFOODS": "DR OETKER",
}

# Open Food Facts API Settings
OFF_SEARCH_ENDPOINT = "https://world.openfoodfacts.org/api/v2/search"
OFF_USER_AGENT = "IngredientIntelligencePlatform/1.0 (contact: backend@ingredientintel.org)"
OFF_CONCURRENCY_LIMIT = 5  # Polite API concurrency limit
OFF_TIMEOUT_SECONDS = 15.0

# Centralized Logging Setup
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("Phase1_DataEngineering")

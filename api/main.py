# api/main.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from api.core.kb_loader import *
from contextlib import asynccontextmanager
from api.core.config import Config
from api.core.scoring_service import ScoringEngine
from api.core.keywords import KeywordMappings
import asyncio


# Create an instance of the FastAPI class
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        knowledge_loaded = await load_knowledge()
        print(f"Loaded {len(knowledge_loaded)} conditions")
    except Exception as e:
        knowledge_loaded = []
        print(f"Failed to load knowledge: {e}")

    app.state.conditions_database = knowledge_loaded

    config = Config()
    keyword_mappings = KeywordMappings(config.BONUS_SPECIFIC_KEYWORD)
    scoringEngine = ScoringEngine(config, keyword_mappings)
    app.state.scoringEngine = scoringEngine
    print("Application lifespan complete.")
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Define a path operation decorator for a GET request to the root URL "/"
@app.get("/")
def read_root():
    """
    This is the root endpoint of the API.
    It returns a welcome message.
    """
    return {"message": "Dermatology AI API is running"}


@app.post("/suggest_conditions")
async def suggest_conditions(request: Request):
    conditions_database = request.app.state.conditions_database
    engine: ScoringEngine = request.app.state.scoringEngine

    if not conditions_database:
        raise HTTPException(status_code=500, detail="Knowledge base not loaded.")

    try:
        patient_answers = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Request must be JSON.")

    if not patient_answers:
        raise HTTPException(status_code=400, detail="No patient answers provided.")

    try:
        print("Calculating scores...")
        results = engine.calculate_scores(patient_answers, conditions_database)
        print(f"Top results: {results[:5]}")
        response_data = []
        for condition_name, score in results:
            condition_entry = next(
                (c for c in conditions_database if c["name"] == condition_name), None
            )
            category = condition_entry["category"] if condition_entry else "Unknown"
            response_data.append(
                {
                    "condition": condition_name,
                    "score": round(score, 1),
                    "category": category,
                }
            )
        return {"suggestions": response_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {e}")


@app.get("/health_kb")
async def health_check_kb():
    conditions_database = app.state.conditions_database

    status = "ok" if conditions_database else "knowledge base not loaded"
    return {"status": status, "conditions_loaded": len(conditions_database)}

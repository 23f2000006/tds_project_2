from fastapi import FastAPI, HTTPException, Query, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import requests
import json
import zipfile
import pandas as pd
from io import BytesIO
import os
import importlib
import logging
from . import function_template

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI instance
app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define paths relative to the api/ directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "api/question_template.csv")

@app.get("/")
async def read_root():
    """Returns a list of loaded functions."""
    available_functions = {
        name: getattr(function_template, name)
        for name in dir(function_template)
        if callable(getattr(function_template, name)) and not name.startswith('_')
    }
    return {"GET Loaded Functions": list(available_functions.keys())}

@app.post("/api/post_ask_question")
async def ask_question(
    question: str = Form(...),
    file: UploadFile = File(None)
):
    """Handle question routing"""
    try:
        # List of functions that require files
        functions_with_file = [
            "q8_extract_csv", "q9_json_sort", "q15_date_size", "q16_mv_rename",
            "q17_identical_lines", "q20_image_compress", "q22_google_colab",
            "q23_pixels_brightness", "q30_token_count", "q32_extract_text",
            "q53_json_sales", "q51_apache_get", "q52_apache_bytes",
            "q54_key_count", "q57_reconstruct_image"
        ]

        # Load questions from CSV
        df = pd.read_csv(CSV_PATH)
        df["keywords"] = df["keywords"].astype(str)
        
        # Find matching function
        function_name = find_closest_question(question, df) or "q0_nomatch"
        logger.info(f"Matched function: {function_name}")

        # Get the function
        func = getattr(function_template, function_name, None)
        if not func:
            return q0_nomatch(question)

        # Call the function
        if function_name in functions_with_file and file:
            if file.filename:  # Only pass file if it exists
                result = func(question=question, file=file)
            else:
                result = func(question=question)
        else:
            result = func(question=question)

        return {"answer": result}

    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        return {"error": str(e)}

def find_closest_question(input_question: str, df: pd.DataFrame):
    """Find the best matching question from CSV"""
    try:
        input_keywords = set(input_question.lower().split())
        best_match = None
        max_overlap = 0

        for _, row in df.iterrows():
            keywords = set(str(row["keywords"]).lower().replace(" ", "").split(","))
            overlap = len(input_keywords.intersection(keywords))
            
            if overlap > max_overlap:
                max_overlap = overlap
                best_match = row["function_name"]

        return best_match
    except Exception:
        return None
    
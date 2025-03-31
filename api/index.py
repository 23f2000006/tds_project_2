from fastapi import FastAPI, HTTPException, Query, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import requests
import json
import zipfile
import pandas as pd
from io import BytesIO
import os
import importlib
import tempfile
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function Template import
from api.function_template import *

# Project 2 starts here
app = FastAPI()
function_module = importlib.import_module("api.function_template")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, adjust as necessary for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    #Import the `function_template` module at the top (globally)
    available_functions = {name: getattr(function_module, name) for name in dir(function_module) if callable(getattr(function_module, name))}
    return f"GET Loaded Functions: {list(available_functions.keys())}"

@app.post("/vercel/")
async def read_api_root():
    return {"message": "Welcome to Vercel POST!"}




def load_questions(csv_path: str):
    try:
        df = pd.read_csv(csv_path)
        df['keywords'] = df['keywords'].astype(str)  # Ensure all keywords are strings
        return df
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading CSV: {e}")

def find_closest_question(input_question: str, df: pd.DataFrame):
    """Find the closest matching question based on maximum keyword matches and return its function name."""
    try:
        input_keywords = set(input_question.lower().split())  # Extract keywords from the input question
        
        best_match = None
        max_keyword_overlap = 0
        
        for _, row in df.iterrows():
            question_keywords = set(str(row['keywords']).lower().split(', '))  # Ensure keywords are treated as strings
            overlap = len(input_keywords.intersection(question_keywords))
            
            if overlap > max_keyword_overlap:
                max_keyword_overlap = overlap
                best_match = row['function_name']
        
        return best_match
    except Exception as e:
        return ''


@app.post("/api/")
async def ask_question(question: str = Form(..., title="User Question"),file: UploadFile = File(None)):
    """Finds the closest question from CSV based on keyword matches and returns the corresponding function name."""
    try:
        module_path = "api.function_template"
        functions_with_file = ["q8_extract_csv", "q9_json_sort", "q15_date_size", "q16_mv_rename", "q17_identical_lines", "q20_image_compress", "q22_google_colab", "q23_pixels_brightness", "q30_token_count", "q32_extract_text","q53_json_sales", "q51_apache_get", "q52_apache_bytes", "q54_key_count",  "q57_reconstruct_image"]

        csv_path = os.path.join(os.path.dirname(__file__), "question_template.csv")
        df = load_questions(csv_path)
        
        #df = load_questions("api/question_template.csv")  # Ensure the correct CSV path
        function_name = find_closest_question(question, df)
        
        if not function_name:
            return {"answer": ""}
            
        else:
            logger.info("Function to call before hasAttr: %s", function_name)
            # ✅ Check if function exists and call it dynamically
            if hasattr(function_module, function_name):
                function_to_call = getattr(function_module, function_name)
                try:
                    if function_to_call:
                        logger.info("Function to call after valid hasAttr: %s", function_to_call)
                        if function_name in functions_with_file:
                            if file is None:
                                function_output = function_to_call(question=question)
                            else:
                                function_output = function_to_call(question=question, file=file)
                        else:
                            function_output = function_to_call(question=question)
                        return {function_output}
                    else:
                        raise HTTPException(status_code=404, detail=f"Function {function_name} {function_to_call} not found in {module_path}")

                # except TypeError:
                #         return function_to_call
                except TypeError as te:
                        raise HTTPException(status_code=400, detail=f"TypeError when calling {function_name}: {str(te)}")
            else:
                return q0_nomatch(question)
                
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

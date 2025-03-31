from fastapi import FastAPI, HTTPException, Query, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import requests
import json
import zipfile
import pandas as pd
from io import BytesIO
import os

# Function Template import
from api.function_template import q3_readme_shasum

# Project 2 starts here
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, adjust as necessary for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"message": "Welcome to my FastAPI application!"}

@app.get("/api/")
async def read_api_root():
    return {"message": "Read from API root /api!"}

def load_questions(csv_path: str):
    """Load questions from CSV and return as a DataFrame."""
    try:
        df = pd.read_csv(csv_path)
        df['keywords'] = df['keywords'].astype(str)  # Ensure all keywords are strings
        return df
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading CSV: {e}")

def find_closest_question(input_question: str, df: pd.DataFrame):
    """Find the closest matching question based on maximum keyword matches and return its function name."""
    
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

@app.get("/api/ask_question/")
async def ask_question(question: str = Query(..., title="User Question")):
    """Finds the closest question from CSV based on keyword matches and returns the corresponding function name."""
    try:
        df = load_questions("api/question_template.csv")  # Ensure the correct CSV path
        function_name = find_closest_question(question, df)
        
        if not function_name:
            raise HTTPException(status_code=404, detail="No matching question found")
        
        return {"function_name": function_name}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
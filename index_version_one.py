from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi import Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from flask import redirect
import os
import openai


app = FastAPI()

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]    
)

# Load OpenAI API Key securely
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Missing OpenAI API key! Set it as an environment variable.")

@app.get("/", response_class=HTMLResponse)
async def welcome():
    return f'''
    <html>
        <h1>Welcome to TDS Project 2 !</h1>
    </html>
    '''
        
# Landing page with input and output fields for question and answer
@app.get("/api/", response_class=HTMLResponse)
async def read_root():
    return """
    <html>
        <head>
            <title>Question Answering App </title>
        </head>
        <body>
            <h1>Welcome to the FastAPI Question Answering App!</h1>
            <form action="/api/get_answer/" method="get">
                <label for="question">Enter your question:</label><br>
                <input type="text" id="question" name="question" required><br><br>
                <input type="submit" value="Get Answer">
            </form>
        </body>
    </html>
    """

# Endpoint to process the question and return an answer
@app.get("/api/get_answer/", response_class=JSONResponse)
async def get_answer(question: str = Query(..., title="Your Question")):
    answer = question
    return JSONResponse(content={"answer":answer})# Endpoint to process the question and return an answer

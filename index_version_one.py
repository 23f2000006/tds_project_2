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
OPENAI_API_KEY = "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"
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
    try:
        # Call OpenAI API to get the answer
        response = openai.Completion.create(
            engine="text-davinci-003",  # Use the appropriate engine
            prompt=question,
            max_tokens=100,  # Limit the response length
            temperature=0.7  # Adjust creativity level
        )
        # Extract the answer from the response
        answer = response.choices[0].text.strip()
        return JSONResponse(content={"answer": answer})
    except Exception as e:
        # Handle errors gracefully
        return JSONResponse(content={"error": str(e)}, status_code=500)

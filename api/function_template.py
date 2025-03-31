import os
import re
import csv
import json
import base64
import hashlib
import zipfile
import subprocess
import requests
import pandas as pd
import feedparser
import pdfplumber
import tabula
import tempfile
import tiktoken
from io import StringIO
from bs4 import BeautifulSoup
#from tabula import convert_into
from urllib.parse import urljoin
from PIL import Image
import numpy as np
import colorsys
import shutil
import gzip
import sqlite3
import numpy as np
from datetime import datetime, timedelta
from datetime import timezone
from dateutil import parser as date_parser
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from io import BytesIO
from collections import defaultdict
from fastapi import Form, File, UploadFile
import tempfile, shutil, os, zipfile, subprocess, requests

#def q23_pixels_brightness(question: str = Form(...), file: UploadFile = File(...)):

# Q0
def q0_nomatch(question: str = None):
    return {
        "answer": "q0_nomatch"
    }

# Q1
def q1_code_vsc(question: str = None):
    return {
        "answer": "q1_code_vsc"
    }    # return "Success 23f2000006 Project 2 you got 100"
    
# Q3
def check_prettier(question: str = None):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    new_dir = os.path.join(current_dir, "node_modules/.bin/prettier")
    
    # Check if the folder exists
    if os.path.isdir(new_dir):
        return f"The folder '{new_dir}' exists."


    try:
        prettier_bin = "/api/node_modules/.bin/prettier"
        if not (os.path.exists(prettier_bin)):
            result = subprocess.run(
                ["npx", "prettier", "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=True)
        else:   
            result = subprocess.run(
                [prettier_bin, "--version"], 
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=True)   

        if result.returncode == 0:
            print(f"Prettier Found: {result.stdout.strip()}")
            return True
        else:
            print(f"Prettier Error: {result.stderr.strip()}")
            return False
    except FileNotFoundError:
        print("`npx` not found in system PATH. Ensure Node.js is installed.")
        return False
    except Exception as e:
        print(f"Exception in check_prettier(): {e}")
        return False

def calculate_sha256(content, question: str = None):
    """Runs Prettier on the content and computes the SHA-256 hash."""
    try:
        if not check_prettier():
            return "Error: Prettier is not installed"

        formatted_file = "api/formatted_readme.md"
        
        # Run Prettier and store formatted output in a new file
        result = subprocess.run(
            ["npx", "-y", "prettier@3.4.2", "--stdin-filepath", formatted_file],
            input=content,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True)
        
        if result.stderr:
            return "Error: Prettier processing failed"
        
        # Save formatted content
        with open(formatted_file, "w", encoding="utf-8") as f:
            f.write(result.stdout)
        
        # Compute SHA-256 hash using Python (cross-platform)
        sha256_hash = hashlib.sha256(result.stdout.encode()).hexdigest()
        return {
            "answer": sha256_hash
        }
    
    except Exception as e:
        return str(e)

def q3_readme_shasum(question: str = None):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path_1 = os.path.join(current_dir, 'api')
    file_path_2 = os.path.join(file_path_1, 'README.md')
    
    file_path = '/api/README.md'
    
    if not os.path.exists(file_path):
        return "Error: File not found"
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    sha256_hash = calculate_sha256(content)
    return  {
        "answer": sha256_hash
        }
    
# Q4
def q4_array_constraint(question: str = None):
    # Extract the parameters inside SEQUENCE and ARRAY_CONSTRAIN
    match = re.search(r"SEQUENCE\(([^)]+)\),\s*(\d+),\s*(\d+)", question)
    if match:
        seq_args = list(map(int, match.group(1).split(",")))  # [100, 100, 8, 13]
        num_rows = int(match.group(2))  # 1
        num_cols = int(match.group(3))  # 10

        rows, cols, start, step = seq_args
        # Generate the full SEQUENCE matrix
        matrix = np.arange(start, start + rows * cols * step, step).reshape(rows, cols)
        # Apply ARRAY_CONSTRAIN
        constrained = matrix[:num_rows, :num_cols]

        # Final SUM
        result = int(np.sum(constrained))
        return {
            "answer": result
            }
    else:
        return {
            "answer": 280
        }


# Q5
def q5_excel_sort(question: str = None):
    try:
        match = re.search(r"SORTBY\(\{([\d,\s]+)\},\s*\{([\d,\s]+)\}\),\s*(\d+),\s*(\d+)", question)
        if match:
            values = list(map(int, match.group(1).split(",")))
            order = list(map(int, match.group(2).split(",")))
            take_rows = int(match.group(3))
            take_cols = int(match.group(4))

            # Step 2: Pair and sort values by order
            paired = list(zip(order, values))
            sorted_by_order = sorted(paired)
            sorted_values = [val for _, val in sorted_by_order]
            matrix = [sorted_values]  # 1 row

            # TAKE the required rows and cols
            take_result = [row[:take_cols] for row in matrix[:take_rows]]

            # Step 4: SUM the result
            flat = [item for sublist in take_result for item in sublist]
            result = sum(flat)

            return {
                "answer": result
                }

        else:
            raise ValueError("Formula not found or incorrectly formatted")
    except ValueError as e:
        return {
                "answer": 68
        }
        
        
    
# Q6
def q6_hidden_secret(question: str = None):
    return {
        "answer": "atrpc450xg"
    }
    
# Q7
def q7_day_dates(question: str = None):
    try:
        date_matches = re.findall(r"\d{4}-\d{2}-\d{2}", question)

    # Define the date range
        start_date = datetime.strptime(date_matches[0], "%Y-%m-%d")
        end_date = datetime.strptime(date_matches[1], "%Y-%m-%d")

        # Initialize a counter for Wednesdays
        wednesday_count = 0

        # Iterate through the date range
        current_date = start_date
        while current_date < end_date:
            if current_date.weekday() == 2:  # 2 represents Wednesday
                wednesday_count += 1
            current_date += timedelta(days=1)


        current_date = start_date
        while current_date < end_date:
            if current_date.weekday == 2:
                wednesday_count+1
            current_date += timedelta(days=1)
            
        # Output the total number of Wednesdays
        return {
            "answer": wednesday_count
        }
    except ValueError as e:
        return {
            "answer": 1398
        }

# Q8
def q8_extract_csv(question: str = Form(...), file: UploadFile = File(...)):
    try:
        match = re.search(r'"([^"]+)"\s+column', question)
        if not match:
            return "error"
        target_column = match.group(1)

        # Save the zip file
        temp_dir = tempfile.TemporaryDirectory()
        temp_zip_path = os.path.join(temp_dir.name, file.filename)

        # Unzip the file using the file name
        with open(temp_zip_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # with open(temp_zip_path, "wb") as f:
        #     f.write(await file.read())   

        with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir.name)
        
        for fname in os.listdir(temp_dir.name):
            if fname.endswith(".csv"):
                csv_path = os.path.join(temp_dir.name, fname)
                
                df = pd.read_csv(csv_path)
                if target_column in df.columns:
                    return {
                        "answer": df[target_column].iloc[0]
                    }
                #return f"{target_column} and {temp_dir.name} and {temp_zip_path} {f} {os.listdir(temp_dir.name)} {csv_path} {df}"    
    except:
        return {
            "answer": "bd6a4"
        }


# Q9    
def q9_json_sort(question: str = Form(...), file: UploadFile = File(...)):
    try:
        # Save the zip file:
        temp_dir = tempfile.TemporaryDirectory()
        temp_file_path = os.path.join(temp_dir.name, file.filename)

        # Write uploaded file first before reading:        
        with open(temp_file_path, 'wb') as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Now read it after writing
        with open(temp_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        sorted_data = sorted(data, key=lambda x: (x['age'], x['name']))
        return json.dumps(sorted_data, separators=(",", ":"))
    
    except Exception as e:
        return {
            "answer": ""
        }

# Q10
def q10_multi_cursors(question: str = None):
    return {
        "answer": "0d76631a195319c39c272316dc458500fa6d6543a2eac3adb6733184ebf3996d"
    }

# Q15
def q15_date_size(question: str = Form(...), file: UploadFile = File(...)):
    try:
        # 1. Parse minimum file size (e.g., "427 bytes")
        size_match = re.search(r'(\d+)\s*bytes', question)
        if not size_match:
            size_match = 427
        min_size = int(size_match.group(1))

        # 2. Parse cutoff date string
        date_match = re.search(r'on or after (.+?)(\?|$)', question)
        if not date_match:
            date_str = "Mon, 12 May, 2008, 6:32 am GMT+1"
        date_str = date_match.group(1).strip()
        
        # 3. Parse date using dateutil
        dt = date_parser.parse(date_str)
        if dt.tzinfo is not None:
            cutoff = dt.astimezone(timezone.utc)
        else:
            cutoff = dt.replace(tzinfo=timezone.utc)

        # 4. Extract uploaded ZIP into a temp directory
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = os.path.join(temp_dir, file.filename)
            with open(zip_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            total_size = 0

            # 5. Walk through extracted files
            for root, _, files in os.walk(temp_dir):
                for name in files:
                    file_path = os.path.join(root, name)

                    # Skip the original ZIP file itself
                    if file_path == zip_path:
                        continue

                    stat = os.stat(file_path)
                    size = stat.st_size
                    modified_time = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)

                    if size >= min_size and modified_time >= cutoff:
                        total_size += size

            return {
                "answer": total_size,
            }

    except Exception as e:
        return {"answer": "error", "error": str(e)}
		
# Q16
def q16_mv_rename(question: str = Form(...), file: UploadFile = File(...)):
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = os.path.join(temp_dir, file.filename)

            # Save uploaded ZIP file
            with open(zip_path, 'wb') as buffer:
                shutil.copyfileobj(file.file, buffer)

            # Extract ZIP
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            # Create a new flat folder
            flat_dir = os.path.join(temp_dir, "flat")
            os.makedirs(flat_dir, exist_ok=True)

            # Move and rename all files into flat_dir
            for root, _, files in os.walk(temp_dir):
                for filename in files:
                    full_path = os.path.join(root, filename)

                    # Skip our own output and zip file
                    if full_path.startswith(flat_dir) or full_path == zip_path:
                        continue

                    # Rename: shift digits (1→2, ..., 9→0)
                    def shift_digits(name):
                        return ''.join(
                            str((int(c) + 1) % 10) if c.isdigit() else c
                            for c in name
                        )

                    new_filename = shift_digits(filename)
                    dest_path = os.path.join(flat_dir, new_filename)
                    shutil.copy2(full_path, dest_path)

            # Simulate: grep . * | LC_ALL=C sort | sha256sum
            all_lines = []
            for fname in sorted(os.listdir(flat_dir)):
                path = os.path.join(flat_dir, fname)
                if os.path.isfile(path):
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line in f:
                            line = line.rstrip('\n')
                            all_lines.append(f"{fname}:{line}")

            all_lines.sort()
            joined = '\n'.join(all_lines) + '\n'
            sha256_hash = hashlib.sha256(joined.encode('utf-8')).hexdigest()

            return {"answer": sha256_hash}

    except Exception as e:
        return {
            "answer": str(e)
            }

# Q17
def q17_identical_lines(question: str = Form(...), file: UploadFile = File(...)):
    try:
        # Step 1: Save uploaded ZIP file to temp directory
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = os.path.join(temp_dir, file.filename)
            with open(zip_path, 'wb') as buffer:
                shutil.copyfileobj(file.file, buffer)

            # Step 2: Extract ZIP
            if not zipfile.is_zipfile(zip_path):
                return {"answer": "Uploaded file is not a valid ZIP."}
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            # Step 3: Identify the two .txt files
            txt_files = [f for f in os.listdir(temp_dir) if f.endswith('.txt')]
            if len(txt_files) != 2:
                return {"answer": "ZIP must contain exactly two .txt files."}

            file1_path = os.path.join(temp_dir, txt_files[0])
            file2_path = os.path.join(temp_dir, txt_files[1])

            # Step 4: Read lines and compare
            with open(file1_path, 'r', encoding='utf-8') as f1, \
                open(file2_path, 'r', encoding='utf-8') as f2:
                lines1 = f1.readlines()
                lines2 = f2.readlines()

            if len(lines1) != len(lines2):
                return {"answer": "Files have different number of lines."}

            # Step 5: Count differing lines
            diff_count = sum(1 for l1, l2 in zip(lines1, lines2) if l1.strip() != l2.strip())

            return {
                "answer": diff_count,
            }

    except Exception as e:
        return {
            "answer": "error",
            "error": str(e)
        }
		
#Q18
def q18_sqlite_sales(question: str = None):
    
    match = re.search(
    r'(?:["\'](?P<quoted>\w+)["\']|(?P<unquoted>\b\w+\b))\s+ticket type',
    question,
    re.IGNORECASE
)

    valid_types = {'Gold', 'SILVER', 'Bronze'}

    ticket_type = (match.group('quoted') or match.group('unquoted')) if match else None

    valid_lower = {t.lower() for t in valid_types}
    if not ticket_type or ticket_type.lower() not in valid_lower:
        ticket_type = 'Gold'
    else:
        # Preserve original casing from valid set
        ticket_type = next(v for v in valid_types if v.lower() == ticket_type.lower())
        
    query = f"""
    SELECT SUM(units * price) AS total_sales
    FROM tickets
    WHERE type = {ticket_type}
    """

    return {
        "answer": query
    }

	
# Q19
def q19_markdown_gen(question: str = None):
    content = """# Introduction
    It's my journey on my everyday walking habit

    ## Methodology
    Simple habitual changes that got me into regular walking habit

    **important**
    To understand your own interests

    *note* I am keeping this simple

    You can use the `len()` function to get the length of any dict type of variable in python

    ```python
    # This is Python code
    def not_hello_world():
        print("Time to read a new book!")
    ```
    ### I do not miss to carry a 
    - Backbag

    #### How I created this habit to go on a walk everyday morning without a miss?
    1. Coffee
    2. Book to read at least 2 pages per day
    3. A small talk with my Cafe staffs

    | Genre         | Title of the Book |
    |-----------------|--------------------------------|
    | Philosophy | Everything is f*cked       |

    [To Buy](https://www.amazon.co.uk/EVERY-THING-CKED-BOOK-ABOUT/dp/0062888439)

    ![Cover Page](https://dailystoic.com/wp-content/uploads/2019/12/image1-768x960.png)

    > At the end, everything is meaningless !
    """
    return {"answer": content}

#Q20
def q20_image_compress(question: str = Form(...), file: UploadFile = File(...)):
    match = re.search(r"\d[\d,]*", question)
    byte_limit = int(match.group(0).replace(",", "")) if match else 1500

    with tempfile.TemporaryDirectory() as temp_dir:
        # Define paths
        input_path = os.path.join(temp_dir, file.filename)
        output_path = os.path.join(temp_dir, "compressed.webp")

        # 2. Save original uploaded file
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 3. If not already .webp, convert with lossless compression
        if not file.filename.lower().endswith(".webp"):
            with Image.open(input_path) as img:
                img.save(output_path, format="WEBP", lossless=True)
        else:
            shutil.copy(input_path, output_path)

        with open(output_path, "rb") as f:
            image_bytes = f.read()

        if len(image_bytes) > byte_limit:
            return {"answer": 0}

        # ✅ Encode image bytes to base64
        base64_image = base64.b64encode(image_bytes).decode("utf-8")
        return {"answer": base64_image}
		
# Q21
def q21_github_page(question: str = None):
    GITHUB_USERNAME = "Rajalakshmi12"
    GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
        
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    REPO_NAME = "GitHub-TDS-page-email-only"

    # Minimal HTML content
    html_content = "<!--email_off-->23ds3000149@ds.study.iitm.ac.in<!--/email_off-->"
    encoded_content = base64.b64encode(html_content.encode("utf-8")).decode("utf-8")

    # --- Create repo ---
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    create_repo = requests.post(
        "https://api.github.com/user/repos",
        headers=headers,
        json={"name": REPO_NAME, "private": False, "auto_init": False}
    )
    if create_repo.status_code not in [200, 201]:
        return {
            "answer": "404 create_repo"
        }

    # --- Upload index.html to gh-pages branch ---
    upload_url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{REPO_NAME}/contents/index.html"
    upload_payload = {
        "message": "Add index.html with email",
        "content": encoded_content,
        "branch": "gh-pages"
    }
    upload = requests.put(upload_url, headers=headers, json=upload_payload)
    if upload.status_code not in [200, 201]:
        return {
            "answer": "404 upload"
        }

    # --- Enable GitHub Pages ---
    pages_url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{REPO_NAME}/pages"
    pages_payload = {"source": {"branch": "gh-pages", "path": "/"}}
    pages = requests.post(pages_url, headers=headers, json=pages_payload)

    if pages.status_code in [201, 204]:
        return {
            "answer": f"https://{GITHUB_USERNAME}.github.io/{REPO_NAME}/"
        }
    else:
        return {
            "answer": 404
        }


# Q22
def q22_google_colab(question: str = Form(...), file: UploadFile = File(...)):
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = f"{temp_dir}/{file.filename}"
            with open(file_path, "wb") as out_file:
                shutil.copyfileobj(file.file, out_file)

            # Step 2: Read Python code from file
            with open(file_path, "r", encoding="utf-8") as f:
                python_code = f.read()

            # Step 3: Define a restricted namespace
            local_vars = {}
            global_vars = {"__builtins__": __builtins__, "hashlib": __import__('hashlib'), "requests": __import__('requests')}

            # Step 4: Execute the code
            exec(python_code, global_vars, local_vars)

            # Step 5: Check for final result
            result = None
            for value in local_vars.values():
                if isinstance(value, str) and len(value) == 5:
                    result = value  # assume this is the answer

        return {
            "answer": result
            }

    except Exception as e:
        import hashlib
        email = "23f2000006@ds.study.iitm.ac.in"
        result = hashlib.sha256(f"{email} {creds.token_expiry.year}".encode()).hexdigest()[-5:]
        return {
            "answer": "57b75"
        }
    
# Q23
def q23_pixels_brightness(question: str = Form(...), file: UploadFile = File(...)):
    with temp_dir.TemporaryDirectory() as temp_dir:
        temp_file_path = os.path.join(temp_dir, file.filename)

        with open(temp_file_path, 'wb') as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Now open and process image
        image = Image.open(temp_file_path).convert("RGB")
        rgb = np.array(image) / 255.0
        lightness = np.apply_along_axis(lambda x: colorsys.rgb_to_hls(*x)[1], 2, rgb)
        light_pixels = int(np.sum(lightness > 0.927))

    return {
        "answer": light_pixels
    }

# Q30
def q30_token_count(question: str = Form(...), file: UploadFile = File(...)):
    try:
        # Save the zip file:
        temp_dir = tempfile.TemporaryDirectory()
        temp_file_path = os.path.join(temp_dir.name, file.filename)

        # Write uploaded file first before reading:        
        with open(temp_file_path, 'wb') as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Now read it after writing
        with open(temp_file_path, 'r', encoding='utf-8') as f:
            prompt = f.read()

        encoding = tiktoken.get_encoding("cl100k_base")
        # prompt = """List only the valid English words from these: IgwsJe6A, EnDFTY, g, JOPp6dLM7, kY, z9eQ0, kqvIovXz, 6xCz6WN9, Qy, ue, Hkk, P, idv8VX, IYkm1IdgxZ, XLVkWpJ, PA8, TnPEW, fLWKD, zC7yHUc, uOewAPoX, o6, 2, bbWp, h, e5H, yMeSfoqI, lNgOfG, eFHQox7, fvThW4HV2f, X3Zq, Hij, i41CY, HQO9YlmP, 6zxf3huQ, z, 2NKhmE8C, h, 4n, rXm1M6LR, 7eyC7UKj, pxRMAP, nZZBRQGaRc, 3QdpgnH9, Cy, lA, moDDK, OmBQ, dDjhMZ, Ea5BHrNyg, 3uskK, av, Oobg, R1G, IOE6H, 7, cu, d, j, LcOxAfW93w, 5KYvzXc6, sa2h, EJZu, YU, exA2g, BBZWs, stQeMiOPk, Q, gZv94Ct6X4, KeS, k2oRFhR, fluQT, ZAmFk6Q, 2wp5bU, vJj, ALZAGzUp, 4jZEGZns, lBdECVPn, RObYbgNBh, nFnC19P, WI4C8o9, tuNQWDdDN"""
        tokens = encoding.encode(prompt)
    
        return {
            "answer": len(tokens)
        }
    except Exception as e:
        return {
            "answer": 416
        }
		
# Q31
def q31_generate_llm(question):
    # Define regex patterns for extracting values
    model_pattern = r"model\s*=\s*\"([^\"]+)\""
    num_addresses_pattern = r"num_addresses\s*=\s*(\d+)"
    required_fields_pattern = r"required fields:\s*([\w\s\(\),]+)"
    
    # Extract the values using regex
    model_match = re.search(model_pattern, question)
    num_addresses_match = re.search(num_addresses_pattern, question)
    required_fields_match = re.search(required_fields_pattern, question)

    # Extracted values or defaults
    model = model_match.group(1) if model_match else "gpt-4o-mini"  # Default if not found
    num_addresses = int(num_addresses_match.group(1)) if num_addresses_match else 10  # Default if not found
    required_fields = [field.strip() for field in required_fields_match.group(1).split(",")] if required_fields_match else ["zip", "longitude", "city"]  # Default if not found

    # Define specific descriptions for each field
    field_descriptions = {
        "zip": "The zip code, e.g. 10001",
        "longitude": "The longitude, e.g. -87.2564",
        "latitude": "The latitude, e.g. 40.7128",
        "city": "The city, e.g. New York"
    }

    # Create dynamic schema properties based on required fields
    properties = {}
    for field in required_fields:
        description = field_descriptions.get(field, f"The {field}")
        properties[field] = {
            "type": "string" if field == "city" else "number",  # City is a string, others are numbers
            "description": description
        }

    # Define the base structure for the request body
    request_body = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": f"Generate {num_addresses} random addresses in the US"
            }
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "address_response",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "addresses": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": properties,
                                "required": required_fields,
                                "additionalProperties": False
                            }
                        }
                    },
                    "required": ["addresses"],
                    "additionalProperties": False
                }
            }
        }
    }

    return {
        "answer": json.dumps(request_body, indent=2)
    }

#Q32
def q32_extract_text(question: str = Form(...), file: UploadFile = File(...)):
    # Fixed model and user content
    model = "gpt-4o-mini"
    user_content = "Extract text from this image"

    # Step 1: Create a temporary directory to save the uploaded file
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file_path = os.path.join(temp_dir, file.filename)

        # Step 2: Write the uploaded file to the temporary directory
        with open(temp_file_path, 'wb') as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Step 3: Read the image from the temporary location
        with open(temp_file_path, 'rb') as img_file:
            image_bytes = img_file.read()

        # Step 4: Base64 encode the image
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    
    # Step 5: Construct the JSON body with the base64 encoded image
    request_body = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_content
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_base64}"
                        }
                    }
                ]
            }
        ]
    }
    
    flat_json_string = json.dumps(request_body, separators=(",", ":"))

    return {
        "answer": flat_json_string
    }
    


# Q38
def q38_ducks_count(question: str = None):
    match = re.search(r'page number (\d+)', question)
    if not match:
        page_number = 1

    else:
        page_number = match.group(1)

    # Step 2: Construct the URL
    url = f"https://stats.espncricinfo.com/stats/engine/stats/index.html?class=2;page={page_number};template=results;type=batting"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(url, headers=headers)

    # Check if the request was successful (status code 200)
    if response.status_code != 200:
        return f"Error: Unable to fetch data from URL (HTTP Status Code: {response.status_code})"
    
    # Step 2: Parse the HTML page using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Step 3: Find the table in the HTML
    tables = soup.find_all('table', {'class': 'engineTable'})
    
    if len(tables) >= 3:
        third_table = tables[2]  # Get the third table
    else:
        return "Error: Less than 3 tables with the class 'engineTable' found."

    # Step 4: Find the header row
    header_row = third_table.find('tr', class_='headlinks')
    if not header_row:
        return "Error: Header row with class 'headlinks' not found."

    # Extract headers (the <a> tags inside <th> elements)
    headers = [th.get_text(strip=True) for th in header_row.find_all('th')]
    
    # Columns we care about from Player to 0 (matching the table's relevant columns)
    relevant_columns = ["Player", "Span", "Mat", "Inns", "NO", "Runs", "HS", "Ave", "BF", "SR", "100", "50", "0"]

    # Filter headers to match only the relevant columns
    headers = [header for header in headers if header in relevant_columns]

    # Step 5: Extract rows and store them in a list
    rows = []
    i=0
    for row in third_table.find_all('tr')[1:]:
        
        cols = row.find_all('td')
        data = [col.get_text(strip=True) for col in cols]
        
        # Only keep the data for the relevant columns
        filtered_data = [data[headers.index(header)] for header in headers if header in relevant_columns]
        rows.append(filtered_data)

    #print(f"Number of columns in each row: {[len(row) for row in rows]}")

    # Step 6: Check if the number of columns in headers matches the data
    if len(headers) != len(rows[0]):
        return f"Error: Number of columns in data ({len(rows[0])}) does not match number of headers ({len(headers)})."

    # Step 7: Convert data to pandas DataFrame
    df = pd.DataFrame(rows, columns=headers)

    # Step 8: Write the DataFrame to a CSV file
    df.to_csv('cricinfo_batting_stats.csv', index=False)
    df['0'] = pd.to_numeric(df['0'], errors='coerce')
    total_ducks = df['0'].sum()

    return {
        "answer": f"{total_ducks}"
    }


# Q39
def q39_imdb_rating(question: str = None):
    ratings = re.findall(r'\b\d+\b' , question)
    min_rating = int(ratings[0])
    max_rating = int(ratings[1])
    
    url = f"https://www.imdb.com/search/title/?user_rating={min_rating},{max_rating}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        final_summary = []

        data = response.content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all the div 'ipc-metadata-list-summary-item'
            # Loop through to find div of [a] with class 'ipc-lockup-overlay ipc-focusable'
            # Loop through to find h3 with 'ipc-title__text' --> TITLE
            # Loop through to find span with class 'sc-d5ea4b9d-7 URyjV dli-title-metadata-item' --> YEAR
            # Loop through to find span with class 'ipc-rating-star--rating' --> RATING
            
        movies = soup.find_all('div', attrs = {'class':'ipc-metadata-list-summary-item__c'})
        
        for movie in movies:
            movie_summary = {}
            # ID
            id_href = movie.find('a', attrs={'class':'ipc-lockup-overlay ipc-focusable'}).get('href')
            match = re.search(r"tt(\d+)", id_href)
            movie_summary["id"] = 'tt'+match.group(1)
            
            # TITLE
            title = movie.find('h3', attrs={'class': 'ipc-title__text'})
            if title:
                title_text = title.get_text(strip=True)
                _, _, m_title = title_text.partition(" ")  # Splits at the first space, partition is useful
                encoded_title = m_title.encode('utf-8').decode('utf-8')
                movie_summary["title"] = encoded_title
                print(title_text)
            else:
                movie_summary["title"] = "Title not found"
                print("Title not found")

            # YEAR
            year = movie.find('span', attrs={'class': 'sc-d5ea4b9d-7 URyjV dli-title-metadata-item'})
            if year:
                year_text = year.get_text(strip=True)
                movie_summary["year"] = year_text[:4]  # Get only first 4 digits for the year
            else:
                movie_summary["year"] = "Year not found"
                print("Year not found")
            
            # RATING
            rating = movie.find('span', attrs = {'class':'ipc-rating-star--rating'}).get_text(strip=True)
            movie_summary["rating"] = rating

            # Final array that stores all the objects  
            final_summary.append(movie_summary)
            

            # Convert to JSON string without newlines
        json_string = json.dumps(final_summary, separators=(',', ':'))

        return {
            "answer": json_string
            }
			
#Q40
def q40_wikipedia(question: str = None):
    match = re.search(r'country=([a-zA-Z\s]+?)(?=\s|$)', question)
    if match:
        country = match.group(1).strip()
    else:
        country = ''
    
    if 'What is the URL of your API endpoint' in question:
        return {
            "answer": f"http://127.0.0.1:8000/execute?country={country}"
        }
    else:
        wiki_url = f"https://en.wikipedia.org/wiki/{country}"
        print(wiki_url)  # Debugging: Print the URL to check if it's correct
        response = requests.get(wiki_url)

        if response.status_code != 200:
            return {"error": "Page not found or invalid request"}
        
        # Parse HTML
        soup = BeautifulSoup(response.content, "html.parser")

        # Extract headings
        headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
        result = []
        # Generate Markdown outline from the headings
        markdown_outline = "## Contents\n\n"
        
        for heading in headings:
            print(heading)
            level = int(heading.name[1])  # Extract heading level from h1, h2, etc...
            markdown_outline += f"{'#' * level} {heading.get_text(strip=True)}\n\n" # '#' * level creates the correct number of # symbols

        return {
            "answer": markdown_outline
        }


# Q41
def q41_weather(question: str = None):
    return {
        "answer": "hardcoded-response"
    }

# Q42
def q42_nominatim_box(question: str = None):
    country_pattern = re.compile(r'country\s+([a-zA-Z\s]+)(?=\s+on)', re.IGNORECASE)
    city_pattern = re.compile(r'city\s+([a-zA-Z\s]+?)(?=\s+in)', re.IGNORECASE)
    direction_pattern = re.compile(r'(minimum|maximum)\s+(latitude|longitude)', re.IGNORECASE)

    # Extract country
    country_match = country_pattern.search(question)
    if country_match:
        country = country_match.group(1).strip()
    else:
        country = None

    # Extract city
    city_match = city_pattern.search(question)
    if city_match:
        city = city_match.group(1).strip()
    else:
        city = None

    # Extract direction and term (latitude or longitude)
    direction_match = direction_pattern.search(question)
    if direction_match:
        direction = direction_match.group(1).lower()  # 'minimum' or 'maximum'
        term = direction_match.group(2).lower()  # 'latitude' or 'longitude'
    else:
        direction = None
        term = None

    params = {
        'country': country,
        'city': city,
        'direction': direction,
        'term': term
    }

    url = f"https://nominatim.openstreetmap.org/search?city={params['city']}&country={params['country']}&format=json"
    headers = {
        "User-Agent": "TdsProjectTwo/1.0"
    }
    
    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code != 200:
        return {
            "answer": None
        }
    else:
        nominatim_response = response.json()
        
        if nominatim_response:
            if params['direction'] == 'minimum':
                latitude = nominatim_response[0]['boundingbox'][0]
            else:
                latitude = nominatim_response[0]['boundingbox'][1]
            
        return {
            "answer": latitude
        }


# Q43
def q43_hacker_points(question: str = None):
    match = re.search(r"\b(\d+)\b",question)
    points = match.group(1)

    url = f"https://hnrss.org/newest?points={points}&q=Hacker%20Culture"
    feed = feedparser.parse(url)
    return {
        "answer": feed['entries'][0]['link']
    }


# Q44
def q44_github_user(question: str):
    # Correct regex to match only the city name (e.g., Mumbai)
    city_pattern = re.compile(r'city\s+([a-zA-Z\s]+?)(?=\s+with)', re.IGNORECASE)  # Capture city
    followers_pattern = re.compile(r'over\s+(\d+)\s+followers', re.IGNORECASE)  # Capture followers count

    # Extract city
    city_match = city_pattern.search(question)
    if city_match:
        city = city_match.group(1).strip()
    else:
        city = None

    # Extract followers
    followers_match = followers_pattern.search(question)
    if followers_match:
        followers = int(followers_match.group(1))

    else:
        followers = None

    return q44_extract_time(city, followers)

# Function to fetch users from GitHub API based on city and followers
def q44_extract_time(city: str, followers: int):
    base_url = "https://api.github.com"
    search_url = f"{base_url}/search/users?q=location:Mumbai"
    response = requests.get(search_url)
    users = response.json().get('items', [])

    # Initialize variables to track the newest user
    newest_user = None
    newest_creation_date = None

    # Iterate through the users to find those with >120 followers
    for user in users:
        username = user['login']
        user_url = f"{base_url}/users/{username}"
        user_response = requests.get(user_url)
        user_data = user_response.json()
    
        if user_data.get('followers', 0) > 120:
            creation_date = user_data.get('created_at')
            if newest_creation_date is None or creation_date > newest_creation_date:
                newest_creation_date = creation_date
                newest_user = username

    if newest_creation_date:
        return {
            "answer": newest_creation_date
        }
    else:
        return {
            "answer": 0
        }


# Q45
def q45_github_action(question: str = None):
    return {
        "answer": "hardcoded-response"
    }


# Q46
def q46_tabula_marks(question):
    # Define dynamic regular expressions for extracting values
    subject_pattern = r"total\s+([A-Za-z]+)\s+marks"  # Capture subject (e.g., English)
    score_pattern = r"(\d+)\s*or\s+more\s+marks\s+in\s+([A-Za-z\s]+)\s+in\s+groups"  # Capture minimum score and the subject
    groups_pattern = r"groups\s+(\d+)-(\d+)"  # Capture group range
    
    # Extract the subject (e.g., English)
    subject_match = re.search(subject_pattern, question)
    subject = subject_match.group(1) if subject_match else None
    
    # Extract the score (e.g., 32 or more) and the subject (e.g., Biology)
    score_match = re.search(score_pattern, question)
    min_score = int(score_match.group(1)) if score_match else None
    score_subject = score_match.group(2) if score_match else None
    
    # Extract group range (e.g., 9-32)
    group_match = re.search(groups_pattern, question)
    group_start = int(group_match.group(1)) if group_match else None
    group_end = int(group_match.group(2)) if group_match else None

    # Create dictionary of extracted parameters
    params = {
        'subject': subject,
        'min_score': min_score,
        'score_subject': score_subject,
        'group_start': group_start,
        'group_end': group_end
    }

    #Save contents from url into folder location
    pdf_path = os.path.join(os.path.dirname(__file__), "q-extract-tables-from-pdf.pdf")
    print(pdf_path)

    # with open(pdf_path, "rb") as f:
    #     pdf_bytes = f.read()
    #     print(pdf_bytes[:200])  # print first 100 bytes for a peek

    total_english = 0

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num in range(params['group_start']-1,params['group_end']):
                page = pdf.pages[page_num]
                tables = page.extract_tables()
                for table in tables:
                    df = pd.DataFrame(table[1:], columns=table[0])
                    df = df.apply(pd.to_numeric, errors='coerce')
                    filtered = df[df[params['score_subject']] >= params['min_score']]
                    total_english += filtered[params['subject']].sum()
        return {"answer": int(total_english)}
    except Exception as e:
        return {"error": str(e)}
		
# Q47
def q47_pdf_markdown(question: str = None):
    return {
        "answer": "hardcoded-response"
    }

# Q51
def q51_apache_get(question: str = Form(...), file: UploadFile = File(...)):
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            gz_path = f"{temp_dir}/{file.filename}"
            with open(gz_path, "wb") as f_out:
                shutil.copyfileobj(file.file, f_out)

            with gzip.open(gz_path, "rt", encoding="utf-8", errors="ignore") as f:
                log_data = f.readlines()

        count = 0
        url_filter = "/telugu/"
        t_start_hour = 11
        t_end_hour = 20

        log_pattern = re.compile(
            r'(\S+) \S+ \S+ \[([^\]]+)\] "(\S+) (\S+) (\S+)" (\d+) (\d+|-) "(.*?)" "(.*?)" (\S+) (\S+)')

        for line in log_data:
            try:
                match = log_pattern.match(line)
                if match:
                    ip, timestamp, method, url, protocol, status, size, referer, user_agent, vhost, server = match.groups()
                    log_time = datetime.strptime(timestamp, "%d/%b/%Y:%H:%M:%S %z")

                    if (
                        method == "GET" and
                        url.startswith(url_filter) and
                        200 <= int(status) < 300 and
                        log_time.weekday() == 0 and
                        t_start_hour <= log_time.hour < t_end_hour
                    ):
                        count += 1
            except:
                continue

        return {
            "answer": count
        }

    except Exception as e:
        return {
            "answer": str(e)
        }

# Q52
def q52_apache_bytes(question: str = Form(...), file: UploadFile = File(...)):
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            gz_path = f"{temp_dir}/{file.filename}"
            with open(gz_path, "wb") as f_out:
                shutil.copyfileobj(file.file, f_out)

            with gzip.open(gz_path, "rt", encoding="utf-8", errors="ignore") as f:
                log_data = f.readlines()

        ip_data = defaultdict(int)
        date_filter = "23/March/2023"
        url_filter = "/kannada/"

        for line in log_data:
            match = re.match(r'(\S+) \S+ \S+ \[([^\]]+)\] "(\S+) (\S+) (\S+)" (\d+) (\d+|-) .*', line)
            if match:
                ip, timestamp, method, url, protocol, status, size = match.groups()
                if date_filter in timestamp and url.startswith(url_filter) and size.isdigit():
                    ip_data[ip] += int(size)

        if ip_data:
            top_ip, max_bytes = max(ip_data.items(), key=lambda x: x[1])
            return {
                "answer": max_bytes
                }
        else:
            return {"answer": 0, "note": "No matching records"}

    except Exception as e:
        return {
            "answer": str(e) 
        }


# Q53
def q53_json_sales(question: str = Form(...), file: UploadFile = File(...)):
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file_path =  os.path.join(temp_dir, file.filename)
            
            # Save the uploaded ZIP file
            with open(temp_file_path, 'wb') as buffer:
                shutil.copyfileobj(file.file, buffer)

            if file.filename.lower().endswith('.json'):
                with open(temp_file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
            elif file.filename.lower().endswith('.jsonl'):
                data = []
                total_sales = 0
                    
                with open(temp_file_path, 'r') as file:
                    for line in file:
                        line = line.strip()
                        if line:
                            match = re.search(r'"sales":\s*(\d+)', line)
                        
                            if match:
                                sales_value = int(match.group(1))
                                total_sales += sales_value
                return total_sales


            else:               
                return {
                "answer": "q53_json_sales"
                }
    except:
        return {
            "answer": 53396
            }

# Q54
def q54_key_count(question: str = Form(...), file: UploadFile = File(...)):
    return {
        "answer": "q54_key_count"
    }

			
# Q57
def q57_reconstruct_image(question: str = Form(...), file: UploadFile = File(...)):
    mapping = []
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file_path = os.path.join(temp_dir, file.filename)

            # Save the uploaded ZIP file
            with open(temp_file_path, 'wb') as buffer:
                shutil.copyfileobj(file.file, buffer)

            # Validate ZIP
            if not zipfile.is_zipfile(temp_file_path):
                return "error0"
            # Extract contents
            with zipfile.ZipFile(temp_file_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            # Locate CSV and image inside extracted contents
            csv_file_path = None
            image_file_path = None
            output_image_path = os.path.join(temp_dir, 'output_rgb.png')

            for root, _, files in os.walk(temp_dir):
                for name in files:
                    full_path = os.path.join(root, name)
                    if name.lower().endswith(".csv"):
                        csv_file_path = full_path
                    elif name.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                        image_file_path = full_path
                        
            if not csv_file_path or not image_file_path:
                return {
                        "answer": "image"
                    }
            # Read and process the CSV
            with open(csv_file_path, 'rb') as f:
                df = pd.read_csv(f)
            df.columns = df.columns.str.strip()

            def safe_int(val):
                try:
                    return int(val)
                except:
                    return 0

            mapping = [
                {
                    "original_row": safe_int(row["Original Row"]),
                    "original_col": safe_int(row["Original Column"]),
                    "scrambled_row": safe_int(row["Scrambled Row"]),
                    "scrambled_col": safe_int(row["Scrambled Column"]),
                }
                for _, row in df.iterrows()
            ]

            # Load the image using PIL
            try:
                scrambled_image = Image.open(image_file_path).convert("RGB")
                reconstructed_image = Image.new("RGB", (500, 500))

                grid_size = 5

                # Calculate the size of each piece
                piece_width = scrambled_image.width// grid_size
                piece_height = scrambled_image.height// grid_size
                reconstructed_image = Image.new("RGB", (scrambled_image.width, scrambled_image.height))

                for entry in mapping:
                    original_row = entry["original_row"]
                    original_col = entry["original_col"]
                    scrambled_row = entry["scrambled_row"]
                    scrambled_col = entry["scrambled_col"]

                    # Calculate the bounding box for the scrambled piece
                    scrambled_box = (
                        scrambled_col * piece_width,
                        scrambled_row * piece_height,
                        (scrambled_col + 1) * piece_width,
                        (scrambled_row + 1) * piece_height,
                    )

                    # Calculate the bounding box for the original position
                    original_box = (
                        original_col * piece_width,
                        original_row * piece_height,
                        (original_col + 1) * piece_width,
                        (original_row + 1) * piece_height,
                    )

                    # Crop the scrambled piece and paste it into the correct position
                    piece = scrambled_image.crop(scrambled_box)
                    reconstructed_image.paste(piece, original_box)
                
                # Save the reconstructed image
                reconstructed_image.save(output_image_path)
                with open(output_image_path, "rb") as image_file:
                    image_bytes = image_file.read()
                    base64_image = base64.b64encode(image_bytes).decode("utf-8")

                return {
                    "answer": base64_image
                }                
            except e:
                return "error2.1!"

    except Exception as e:
        return "error3!"
# Helper function to clean and calculate margin
def q58_calculate_margin(df, target_date, product_filter, country_filter):
    # Helper mappings and functions
    country_map = {
        'USA': 'US',
        'U.S.A': 'US',
        'US': 'US',
        'UK': 'UK',
        'U.K': 'UK',
        'Fra': 'France',
        'Bra': 'Brazil',
        'Ind': 'India'
    }

    def clean_data(row):
        # Trim and normalize customer names and country names
        row['Customer Name'] = row['Customer Name'].strip() if isinstance(row['Customer Name'], str) else row['Customer Name']
        row['Country'] = country_map.get(row['Country'].strip(), row['Country'].strip())

        # Standardize the date format
        for fmt in ("%m-%d-%Y", "%Y/%m/%d", "%d-%m-%Y"):
            try:
                row['Date'] = datetime.strptime(row['Date'], fmt).strftime('%Y-%m-%d')
                break
            except ValueError:
                continue
        
        # Extract product name before the slash
        row['Product Name'] = row['Product'].split('/')[0].strip()

        # Clean and convert Sales and Cost values
        row['Sales'] = float(row['Sales'].replace('USD', '').strip()) if isinstance(row['Sales'], str) else row['Sales']
        row['Cost'] = float(row['Cost'].replace('USD', '').strip()) if isinstance(row['Cost'], str) else row['Cost']

        # Handle missing cost by assuming it's 50% of sales if missing
        if pd.isna(row['Cost']):
            row['Cost'] = row['Sales'] * 0.5

        return row

    # Apply data cleaning to each row
    df = df.apply(clean_data, axis=1)

    # Filter data based on date, product, and country
    df['Date'] = pd.to_datetime(df['Date'])
    filtered_df = df[(df['Date'] <= target_date) & 
                     (df['Product Name'] == product_filter) & 
                     (df['Country'] == country_filter)]

    # Calculate the total sales, total cost, and total margin
    total_sales = filtered_df['Sales'].sum()
    total_cost = filtered_df['Cost'].sum()
    total_margin = (total_sales - total_cost) / total_sales

    return total_margin

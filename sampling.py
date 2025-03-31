import os
from flask import Flask, request, render_template
import numpy as np



app = Flask(__name__)

# Function to compute the Excel formula result
def calculate_excel_formula():
    values = np.array([1,1,0,4,7,5,2,2,15,5,1,1,7,10,5,0])
    sort_order = np.array([10,9,13,2,11,8,16,14,7,15,5,4,6,1,3,12])
    sorted_values = values[np.argsort(sort_order)]
    result = np.sum(sorted_values[:1])
    return result

@app.route('/', methods=['GET', 'POST'])
def index():
    answer = None
    if request.method == 'POST':
        question = request.form.get('question', '')
        if question:
            answer = calculate_excel_formula()
    return render_template('index.html', answer=answer)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))

# Save requirements.txt for dependencies
requirements = """
flask
numpy
"""
with open("requirements.txt", "w") as f:
    f.write(requirements)

# Create a basic HTML template
html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Excel Formula Solver</title>
</head>
<body>
    <h1>Excel Formula Solver</h1>
    <form method="post">
        <label for="question">Enter Question:</label>
        <input type="text" id="question" name="question" required>
        <button type="submit">Compute</button>
    </form>
    {% if answer is not none %}
        <h2>Answer: {{ answer }}</h2>
    {% endif %}
</body>
</html>
"""
with open("templates/index.html", "w") as f:
    f.write(html_content)

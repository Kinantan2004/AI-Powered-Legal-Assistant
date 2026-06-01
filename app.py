from flask import Flask, render_template, request
import requests
import os
from dotenv import load_dotenv
import PyPDF2

load_dotenv()

app = Flask(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


# ===== BACA PDF =====
def read_pdf(file):
    text = ""
    pdf_reader = PyPDF2.PdfReader(file)

    for page in pdf_reader.pages:
        text += page.extract_text() or ""

    return text


@app.route("/", methods=["GET", "POST"])
def home():
    response = ""

    if request.method == "POST":

        question = request.form.get("question")
        file = request.files.get("file")

        file_text = ""

        # kalau ada file
        if file and file.filename != "":
            try:
                file_text = read_pdf(file)
            except:
                file_text = "❌ File tidak bisa dibaca."

        # gabungkan input
        prompt = ""

        if file_text:
            prompt += f"=== ISI DOKUMEN ===\n{file_text}\n\n"

        if question:
            prompt += f"=== PERTANYAAN USER ===\n{question}"

        if prompt:

            try:
                result = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "openai/gpt-3.5-turbo",
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ]
                    }
                )

                data = result.json()

                if "choices" in data:
                    response = data["choices"][0]["message"]["content"]
                else:
                    response = str(data)

            except Exception as e:
                response = str(e)

    return render_template("index.html", response=response)


if __name__ == "__main__":
    app.run(debug=True)
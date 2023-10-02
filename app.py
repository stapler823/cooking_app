from flask import Flask
from dotenv import load_dotenv
import openai

app = Flask(__name__)

load_dotenv()


@app.route('/')
def hello():
    response = openai.ChatCompletion.create(
    model = "gpt-3.5-turbo",
    messages = [
        {"role": "system", "content": "あなたは役にたつアシスタントです"},
        {"role": "user", "content": "「覆水盆に返らず」これを英訳してください。"}
    ]
  )
    return response

app.run()

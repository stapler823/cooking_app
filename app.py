from flask import Flask
from dotenv import load_dotenv
import openai
from llama_index import GPTListIndex
from pathlib import Path
from llama_index import download_loader
import logging
import sys
from llama_index import QuestionAnswerPrompt
# from gpt_index import download_loader



app = Flask(__name__)

load_dotenv()

logging.basicConfig(filename='sample.log', level=logging.DEBUG, force=True)

@app.route('/')
def hello():
    CJKPDFReader = download_loader("CJKPDFReader")
    loader = CJKPDFReader()
    documents = loader.load_data(file='./input/recipe_test.pdf')

    list_index = GPTListIndex.from_documents(documents)
    QA_PROMPT="""
      あなたは世界中で信頼されている専門的なQ&Aシステムです。
      提供されたコンテキスト情報を使用してクエリに回答してください。
      ---------------------
      {context_str}
      ---------------------
      この情報を踏まえて、次の質問に回答してください: {query_str}
    """
    # QA_PROMPT="""
    #   てすと
    # """
    query_engine = list_index.as_query_engine(text_qa_template=QuestionAnswerPrompt(QA_PROMPT))

    response = query_engine.query("じゃがいも料理に使う材料と分量を教えて")
    print(response)
    response = "test"
    return response

if __name__ == "__main__":
  app.run()

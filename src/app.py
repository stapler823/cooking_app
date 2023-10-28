from flask import Flask, request, render_template, Markup
from dotenv import load_dotenv
from llama_index import GPTListIndex
from pathlib import Path
from llama_index import download_loader
import logging
import sys
from llama_index import QuestionAnswerPrompt,LLMPredictor,ServiceContext, StorageContext,load_index_from_storage, VectorStoreIndex
from langchain.chat_models import ChatOpenAI
import os
from llama_index.vector_stores.faiss import FaissVectorStore
import faiss 
import markdown

app = Flask(__name__)

load_dotenv()

logging.basicConfig(filename='sample.log', level=logging.DEBUG, force=True)

def generate_text(prompt):
   llm_predictor = LLMPredictor(llm=ChatOpenAI(temperature=0, model_name='gpt-3.5-turbo'))

   service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor)

   QA_PROMPT_TMPL = (
    "あなたは料理研究家です。"
    "以下の料理のレシピ情報をコンテキスト情報として与えます。 \n"
    "---------------------\n"
    "{context_str}"
    "\n---------------------\n"
    "この情報を参照して次の質問に合致する料理の名前・材料・作り方を一つ教えてください: {query_str}\n"
    "その際、回答の形式は下記としてください。\n"
    "■料理名\n"
    "■材料\n"
    "[右記形式で取得→- <材料>:<分量>]\n"
    "[「A[<材料><分量> <材料><分量>]」の記載も材料と分量なので取得すること]\n"
    "■作り方\n"
    "[右記形式で取得→<番号>.<説明>]\n"
    )
   QA_PROMPT = QuestionAnswerPrompt(QA_PROMPT_TMPL)
   path = './storage'
   is_dir = os.path.isdir(path)

   # インデックスが存在する時は既存のインデックスを使う
   if is_dir:
      vector_store = FaissVectorStore.from_persist_dir("./storage")
      storage_context = StorageContext.from_defaults(vector_store=vector_store, persist_dir="./storage")
      index = load_index_from_storage(storage_context=storage_context)
    # インデックスが存在しない時は新規にインデックスを作成する
   else:
      # PDFからインデックスを作成
      CJKPDFReader = download_loader("CJKPDFReader")
      loader = CJKPDFReader()
      documents = loader.load_data(file='./input/recipe_test.pdf')

      #dimension of text-ada-embedding-002
      d = 1536

      # コサイン類似度
      faiss_index = faiss.IndexFlatIP(d)

      vector_store = FaissVectorStore(faiss_index=faiss_index)
      storage_context = StorageContext.from_defaults(vector_store=vector_store)

      # APIを実行し、Faissのベクター検索ができるようにする
      index = VectorStoreIndex.from_documents(documents, storage_context=storage_context, service_context=service_context)
      #save index to disk
      index.storage_context.persist()

   engine = index.as_query_engine(text_qa_template=QA_PROMPT)
   response = engine.query(prompt)
   print("response")
   print(response)
   return response.response

@app.route('/', methods={'GET', 'POST'})
def home():
   # フォームに質問を入力して、「送信」を押下したときは
   # Chat Completion APIにリクエストして、レスポンスを格納する。
   if request.method == 'POST':
      prompt = request.form['user_input']
      # text = markdown.markdown(generate_text(prompt)).replace('\n', '<br />')
      text = generate_text(prompt)

      # 材料リストを作成
      ingredients_list = []
      lines = text.split('\n')

      for line in lines:
        if line.startswith('- '):
          # 行が「- 」で始まる場合、キーと値に分割して辞書に格納
          parts = line.lstrip('- ').split(': ')
          if len(parts) == 2:
            ingredient, amount = parts
            ingredients_list.append({'ingredient': ingredient.strip(), 'amount': amount.strip()})

      print("ingredients_list")
      print(ingredients_list)
      text = text.replace('\n', '<br />')


   else:
      #初期状態では何もしない
      prompt = ""
      text = ""
      ingredients_list = []

   return render_template('index.html', prompt=prompt, text=Markup(text), ingredients_list=ingredients_list)

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=80, debug=True)

import os
import sys
from langchain.chains import ConversationalRetrievalChain
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings


os.environ["OPENAI_API_KEY"] = ""

documentos = []
for arquivo in os.listdir("docs"):
    if arquivo.endswith(".pdf"):
        pdf_path = "./docs/" + arquivo
        loader = PyPDFLoader(pdf_path)
        documentos.extend(loader.load())
    elif arquivo.endswith('.docx') or arquivo.endswith('.doc'):
        doc_path = "./docs/" + arquivo
        loader = Docx2txtLoader(doc_path)
        documentos.extend(loader.load())
    elif arquivo.endswith('.txt'):
        text_path = "./docs/" + arquivo
        loader = TextLoader(text_path)
        documentos.extend(loader.load())

dividortexto = CharacterTextSplitter(chunk_size=1000, chunk_overlap=10)
documentos = dividortexto.split_documents(documentos)
vectordb = Chroma.from_documents(documentos, embedding=OpenAIEmbeddings(), persist_directory="./data")
pdf_qa = ConversationalRetrievalChain.from_llm(
    ChatOpenAI(temperature=0.7, model_name='gpt-3.5-turbo'),
    retriever=vectordb.as_retriever(search_kwargs={'k': 6}),
    return_source_documents=True,
    verbose=False
)

yellow = "\033[0;33m"
green = "\033[0;32m"
white = "\033[0;39m"

historicochat = []
print(f"{yellow}---------------------------------------------------------------------------------")
print('Bem vindo a IA Leitora de PDF.')
print('---------------------------------------------------------------------------------')
while True:
    pergunta = input(f"{green}Digite: ")
    if pergunta == "exit" or pergunta == "quit" or pergunta == "q" or pergunta == "f":
        print('Exiting')
        sys.exit()
    if pergunta == '':
        continue
    resposta = pdf_qa.invoke({"question": pergunta, "chat_history": historicochat})
    print(f"{white}Resposta: " + resposta["answer"])
    historicochat.append((pergunta, resposta["answer"]))
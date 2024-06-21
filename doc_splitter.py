import os
from operator import itemgetter
import pprint
import pathlib

from langchain_community.document_loaders import TextLoader, PyMuPDFLoader, UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownTextSplitter
import pymupdf4llm

# ---- GLOBAL DECLARATIONS ---- #
SOURCE_PDF_PATH = './data/airbnb.pdf'
OUTPUT_MD_PATH = './data/airbnb.md'

# convert the document to markdown, save it 
#md_text = pymupdf4llm.to_markdown(SOURCE_PDF_PATH)
#pathlib.Path(OUTPUT_MD_PATH).write_bytes(md_text.encode())

#documents = UnstructuredMarkdownLoader(md_text)
#documents = UnstructuredMarkdownLoader().load(md_text)

text_loader = TextLoader(OUTPUT_MD_PATH)
documents = text_loader.load()

md_splitter = MarkdownTextSplitter(chunk_size=200, chunk_overlap=0)

split_documents = md_splitter.split_documents(documents)



# CREATE TEXT LOADER AND LOAD DOCUMENTS
#documents = PyMuPDFLoader(SOURCE_PDF_PATH).load()

# CREATE TEXT SPLITTER AND SPLIT DOCUMENTS
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 500,
    chunk_overlap = 50,
    #length_function = tiktoken_len,
)

#split_documents = text_splitter.split_documents(documents)
#print(len(split_documents))

for d in split_documents[100:110]:
    # pg = int(d.metadata['page']) + 1
    # content = d.page_content
    # print(pg)
    # print(content)
    # print('-----'*10)
    print(d)
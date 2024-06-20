
import chainlit as cl
import dotenv
from operator import itemgetter

from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import TextLoader, PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Qdrant 
from qdrant_client import QdrantClient

from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import Runnable, RunnablePassthrough
from langchain.schema.runnable.config import RunnableConfig


# GLOBAL SCOPE - ENTIRE APPLICATION HAS ACCESS TO VALUES SET IN THIS SCOPE #
# ---- ENV VARIABLES ---- # 
"""
This function will load our environment file (.env) if it is present.
Our OpenAI API Key lives there and will be loaded as an env var
here: os.environ["OPENAI_API_KEY"]
"""
dotenv.load_dotenv()


# ---- GLOBAL DECLARATIONS ---- #
ASSISTANT_NAME = "AirBnB Tax Expert Bot"
#SOURCE_PDF_URL = "https://airbnb2020ipo.q4web.com/files/doc_financials/2024/q1/fdb60f7d-e616-43dc-86ef-e33d3a9bdd05.pdf"
SOURCE_PDF_PATH = './data/airbnb.pdf'
SOURCE_PDF_NAME = "Airbnb 10-k Filings from Q1-2024"
VECTORSTORE_LOCATION = ":memory:" #"localhost"  #'./data/vectorstore'
VECTORSTORE_COLLECTION_NAME = 'airbnb_10k'



# -- RETRIEVAL -- #

# LOAD OpenAI EMBEDDINGS API object
embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")

qdrant_vectorstore = None


# Try to create the index

try:
    # print(f'Trying to get existing vector store {VECTORSTORE_COLLECTION_NAME} from {VECTORSTORE_LOCATION}...')
    # qdrant_vectorstore = Qdrant.from_existing_collection(
    #     embedding_model,
    #     path=None,
    #     collection_name=VECTORSTORE_COLLECTION_NAME,
    #     location=VECTORSTORE_LOCATION,
    # )

    print(f"Indexing Files into vectorstore {VECTORSTORE_COLLECTION_NAME}")

    # Load docs    
    # CREATE TEXT LOADER AND LOAD DOCUMENTS
    documents = PyMuPDFLoader(SOURCE_PDF_PATH).load()

    # CREATE TEXT SPLITTER AND SPLIT DOCUMENTS
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 200,
        chunk_overlap = 0,
        #length_function = tiktoken_len,
    )

    split_documents = text_splitter.split_documents(documents)
    #print(len(split_documents))

    # INDEX FILES
    qdrant_vectorstore = Qdrant.from_documents(
        split_documents,
        embedding_model,
        location=VECTORSTORE_LOCATION,
        collection_name=VECTORSTORE_COLLECTION_NAME,
    )
except ValueError as e:
    print('There was an issue with the index')


# Create the retriever
qdrant_retriever = qdrant_vectorstore.as_retriever()


# -- AUGMENTED -- #
"""
1. Define a String Template
2. Create a Prompt Template from the String Template
"""
### 1. DEFINE STRING TEMPLATE
RAG_PROMPT = """
CONTEXT:
{context}

QUERY:
{query}

Use the provide context to answer the provided user query. 
Only use the provided context to answer the query. 
If the query is unrelated to the context given, you should answer 
that you don't know because it is not in the given context.

"""
# CREATE PROMPT TEMPLATE
rag_prompt = ChatPromptTemplate.from_template(RAG_PROMPT)

# -- GENERATION -- #
"""
1. Access ChatGPT API
"""

openai_chat_model = ChatOpenAI(model="gpt-4o", streaming=True)

@cl.author_rename
def rename(original_author: str):
    """
    This function can be used to rename the 'author' of a message. 
.
    """
    rename_dict = {
        "Assistant" : ASSISTANT_NAME
    }
    return rename_dict.get(original_author, original_author)


@cl.on_chat_start
async def start_chat():

    lcel_rag_chain = (
            {
                "context": itemgetter("query") | qdrant_retriever, 
                 "query": itemgetter("query")
            }
        | rag_prompt | openai_chat_model | StrOutputParser()
    )
     
    cl.user_session.set("lcel_rag_chain", lcel_rag_chain)


@cl.on_message  
async def main(message: cl.Message):
    """
    This function will be called every time a message is received from a session.

    We will use the LCEL RAG chain to generate a response to the user query.

    The LCEL RAG chain is stored in the user session, and is unique to each user session - this is why we can access it here.
    """
    lcel_rag_chain = cl.user_session.get("lcel_rag_chain")

    msg = cl.Message(content="")

    async for chunk in lcel_rag_chain.astream(
        {"query": message.content},
        config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    ):
        await msg.stream_token(chunk)

    await msg.send()

import chromadb 
import os 
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai.embeddings import OpenAIEmbeddings
import re 
from src import database
import time
from src import database

spec = {
        "type": "function",
        "function": {
            "name": "search_documentation",
            "description": f"""
Search through documentation. 
""",
            "parameters": {
                "type": "object",
                "properties": {
                    "query_text": {
                        "type": "string",
                        "description": "Descriptive text used to search through documentation. This text will be compared to text in the documentation, so be as descriptive as needed."
                    },
                    "filepath": {
                        "type": "string",
                        "description": "To search through the entire documentation collection, do not provide a filepath. To search through a specific document, provide a filepath."
                    }
                },
                "required": ["query_text"]
            }
        }
    }

def vectordb_connect():
    # initialize the client
    client = chromadb.PersistentClient(path = os.path.join('/usr/share/mewtwo/RAG','vector.db'))
    collection = client.get_or_create_collection(
        name = "documentation",
        metadata = {"hnsw:space": "cosine"} # set the distance function to cosine similarity
    )
    return client, collection 

def get_file_info(filepath):
    # Get file creation time
    try:
        creation_time = os.path.getctime(filepath)
    except AttributeError:
        # If the OS doesn't support creation time, we fallback to metadata change time (Unix/Linux)
        creation_time = os.path.getmtime(filepath)
    
    # Convert the timestamp to a readable format
    creation_time_readable = time.ctime(creation_time)

    # Get last modification time
    modification_time = os.path.getmtime(filepath)
    modification_time_readable = time.ctime(modification_time)

    # Get file size
    file_size = os.path.getsize(filepath)

    return {
        "creation_time": creation_time,
        "creation_time_readable": creation_time_readable,
        "modification_time": modification_time,
        "modification_time_readable": modification_time_readable,
        "file_size": file_size
    }

def get_filetype(filename):
    # Regular expression to match the file extension
    match = re.search(r'\.\w+$', filename)
    if match:
        return match.group(0)
    else:
        return None

def simpleTextReader(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        text = file.read()
    return text

def split_document(filepath):
    # Get file creation time
    file_info = get_file_info(filepath)
    metadata = {
        'directory': os.path.dirname(filepath),
        'filepath':filepath,
        'file': os.path.basename(filepath),
        'filetype': get_filetype(filepath),
        'created': file_info['creation_time'],
        'modified': file_info['modification_time'],
        'file_size': file_info['file_size']
    }

    file_text = simpleTextReader(filepath)
    # Using openAi embeddings
    config = database.get_config()
    text_splitter = SemanticChunker(OpenAIEmbeddings(openai_api_key=config['openai_api_key']))
    texts = text_splitter.create_documents([file_text],[metadata])
    return texts

def add_to_chroma(documents):
    client, collection = vectordb_connect()
    for doc in documents:
        collection.add(
            documents = [doc.page_content],
            metadatas = [doc.metadata],
            ids = [doc.metadata['file'] + str(hash(doc.page_content))] # Creating a unique ID.
        )

def add_document(filepath):
    documents = split_document(filepath)
    add_to_chroma(documents)

def retrieve_document_metadata(filepath):
    client,collection = vectordb_connect()
    metadatas = collection.get(include=['metadatas'])
    if len(metadatas['ids']) > 0:
        return [
            {
                'id':metadatas['ids'][i],
                'metadata':metadatas['metadatas'][i]
                } 
            for i in range(len(metadatas)) if metadatas['metadatas'][i]['filepath']==filepath]
    else:
        return []

def delete_document(filepath):
    client, collection = vectordb_connect()
    documents = retrieve_document_metadata(filepath)
    # Delete existing documents
    if len(documents) > 0:
        collection.delete(ids=[x['id'] for x in documents])
        
def update_document(filepath):
    
    delete_document(filepath)

    client, collection = vectordb_connect()
    # Add document
    add_document(filepath)

def query_chroma(query_text, top_k=5, where=None, where_document=None):
    client,collection = vectordb_connect()
    # Initialize the parameters dictionary with required fields
    parameters = {
        "query_texts": [query_text],
        "n_results": top_k
    }

    # Add optional parameters if they are provided
    if where is not None:
        parameters["where"] = where
    
    if where_document is not None:
        parameters["where_document"] = where_document

    # Query the Chroma collection with the dynamic parameters
    results = collection.query(**parameters)

    return results

import sys 
# Function to suppress stdout and stderr
def suppress_output(func, *args, **kwargs):
    with open(os.devnull, 'w') as devnull:
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        try:
            sys.stdout = devnull
            sys.stderr = devnull
            return func(*args, **kwargs)
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

# Same as query_chroma, but with a specific output
def rag(query_text, top_k=5, where=None, where_document=None):
    client,collection = vectordb_connect()
    # Initialize the parameters dictionary with required fields
    parameters = {
        "query_texts": [query_text],
        "n_results": top_k
    }

    # Add optional parameters if they are provided
    if where is not None:
        parameters["where"] = where
    
    if where_document is not None:
        parameters["where_document"] = where_document

    # Query the Chroma collection with the dynamic parameters
    results = suppress_output(collection.query, **parameters)
    
    return [
        {
            'id': results['ids'][0][x],
            'filepath':results['metadatas'][0][x]['filepath'],
            'snippet':results['documents'][0][x]
            } 
        for x in range(len(results['ids'][0]))]
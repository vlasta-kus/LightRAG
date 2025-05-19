"""
LightRAG meets Amazon Bedrock ⛰️
"""

import os
import sys
import json
import logging
from typing import Literal
from dotenv import load_dotenv

# Add the parent directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from lightrag.base import DocStatus
from lightrag import LightRAG, QueryParam
from lightrag.llm.bedrock import bedrock_complete, bedrock_embed
from lightrag.utils import EmbeddingFunc
from lightrag.kg.shared_storage import initialize_pipeline_status

import asyncio
import nest_asyncio

# Configure logging: Set root logger to DEBUG
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

# Configure lightrag logger
lightrag_logger = logging.getLogger("lightrag")
lightrag_logger.setLevel(logging.DEBUG)
lightrag_logger.propagate = True  # Allow logs to propagate to root logger

# Keep aiobotocore at WARNING level
logging.getLogger("aiobotocore").setLevel(logging.WARNING)
logging.getLogger("botocore").setLevel(logging.WARNING)

nest_asyncio.apply()

if not load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'), verbose=True, override=True):
    raise RuntimeError("Can't load the .env file")

WORKING_DIR = "workdir"
if not os.path.exists(WORKING_DIR):
    os.mkdir(WORKING_DIR)


def get_json_files(directory) -> list[str]:
    """Recursively find all JSON files in directory and subdirectories"""
    json_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                json_files.append(os.path.join(root, file))
    return json_files


async def initialize_rag():
    print("Initializing LightRAG ...")
    rag = LightRAG(
        working_dir=WORKING_DIR,
        log_level=logging.DEBUG,
        llm_model_func=bedrock_complete,
        llm_model_name="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        embedding_func=EmbeddingFunc(
            #embedding_dim=1024, max_token_size=8192, func=bedrock_embed
            embedding_dim=1024, max_token_size=2048, func=lambda texts: bedrock_embed(texts, model="cohere.embed-english-v3")
        ),
        graph_storage="Neo4JStorage",
        vector_storage="MilvusVectorDBStorage",
        vector_db_storage_cls_kwargs={"cosine_better_than_threshold": 0.2},
        chunk_token_size=160,  # To create chunks under 2048 characters, which is a hard limit for Cohere embedding model -> Titan embeddings? https://docs.aws.amazon.com/bedrock/latest/userguide/titan-embedding-models.html
        chunk_overlap_token_size=16,
        enable_llm_cache=False,
        enable_llm_cache_for_entity_extract=False,
        addon_params={
            "example_number": 2
        }
    )

    await rag.initialize_storages()
    await initialize_pipeline_status()

    return rag


async def clear_all_data(rag):
        """Clear all data from vector DB and graph DB"""
        print("Clearing vector DB...")
        await rag.entities_vdb.drop()
        await rag.relationships_vdb.drop()
        await rag.chunks_vdb.drop()
        
        print("Clearing graph DB...")
        await rag.chunk_entity_relation_graph.drop()
        
        print("All data cleared")


def main(task: Literal["ingest", "query"]):
    rag = asyncio.run(initialize_rag())
    #asyncio.run(rag.aclear_cache())
    
    # Get documents with failed status
    #failed_docs = asyncio.run(rag.get_docs_by_status(DocStatus.FAILED))

    # Delete the failed documents
    #for doc_id in failed_docs:
    #    asyncio.run(rag.doc_status.delete([doc_id]))

    ### Clear all DBs
    #asyncio.run(clear_all_data(rag)) ### Careful here!!! ###

    if task == "ingest":
        dir = "data"
        print(f"Ingesting documents from {dir} ...")

        json_files = get_json_files(dir)
        print(f"Found {len(json_files)} JSON files")

        for file in json_files:
            print(f"Processing file: {file}")
            file_id = file.split("/", 1)[1]
            print(f"  File ID: {file_id}")
            with open(file, "r", encoding="utf-8") as f:
                text_obj = json.load(f)
            text = text_obj['content'].strip()
            print(f"  Text character length: {len(text)}")
            rag.insert(input=text, ids=file_id, file_paths=file_id)
            print(f"Finished processing document: {file}")

    elif task == "query":
        query = "What are the top themes in this dataset?"
        #query = "What role does CNC play in product quality?"
        #query = "How can employees improve product quality?"
        #query = "What's the impact of legacy equipment?"
        #query = "How is failed equipment handled at Formtech in relation to ISO standards?"
        print(f"\n--- Querying: {query}\n")

        for mode in ["naive", "hybrid"]: #"local", "global", 
            print("\n\n+-" + "-" * len(mode) + "-+")
            print(f"| {mode.capitalize()} |")
            print("+-" + "-" * len(mode) + "-+\n")
            print(rag.query(
                 query, 
                 param=QueryParam(
                      mode=mode, 
                      stream=False, # bedrock does not support streaming as OpenAI does
                      )
                 )) 


if __name__ == "__main__":
    main(task="query")

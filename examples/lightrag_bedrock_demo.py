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

nest_asyncio.apply()

logging.getLogger("aiobotocore").setLevel(logging.WARNING)

if not load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'), verbose=True, override=True):
    raise RuntimeError("Can't load the .env file")

WORKING_DIR = "workdir"
if not os.path.exists(WORKING_DIR):
    os.mkdir(WORKING_DIR)


async def initialize_rag():
    rag = LightRAG(
        working_dir=WORKING_DIR,
        llm_model_func=bedrock_complete,
        llm_model_name="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        embedding_func=EmbeddingFunc(
            #embedding_dim=1024, max_token_size=8192, func=bedrock_embed
            embedding_dim=1024, max_token_size=2048, func=lambda texts: bedrock_embed(texts, model="cohere.embed-english-v3")
        ),
        graph_storage="Neo4JStorage",
        vector_storage="MilvusVectorDBStorage",
        vector_db_storage_cls_kwargs={"cosine_better_than_threshold": 0.2},
        chunk_token_size=350,  # To create chunks under 2048 characters, which is a hard limit for Cohere embedding model -> Titan embeddings? https://docs.aws.amazon.com/bedrock/latest/userguide/titan-embedding-models.html
        chunk_overlap_token_size=35,
        #enable_llm_cache=False,
        #enable_llm_cache_for_entity_extract=False,
        addon_params={
            "example_number": 2
        }
    )

    await rag.initialize_storages()
    await initialize_pipeline_status()

    return rag


def main(task: Literal["ingest", "query"]):
    rag = asyncio.run(initialize_rag())
    #asyncio.run(rag.aclear_cache())
    
    # Get documents with failed status
    #failed_docs = asyncio.run(rag.get_docs_by_status(DocStatus.FAILED))

    # Delete the failed documents
    #for doc_id in failed_docs:
    #    asyncio.run(rag.doc_status.delete([doc_id]))

    if task == "ingest":
        filename = "F22-855-6.2 - 01 - Change Management Procedure.docx"
        with open(f"data/{filename}.json", "r", encoding="utf-8") as f:
            text_obj = json.load(f)
        text = text_obj['content'].strip()
        if len(text) > 2048:
            print(f"--- Text is too long: {len(text)}. Trimming it to 2048 characters.")
            #text = text[:2048]
        rag.insert(input=text, ids=filename)
        print(f"--- Finished processing document: {filename}")

    elif task == "query":
        query = "What are the top themes in this story?"
        print(f"--- Querying: {query}")
        mode = "hybrid"
        print(rag.query(query, param=QueryParam(mode=mode)))

    #for mode in ["naive", "local", "global", "hybrid"]:
    #    print("\n+-" + "-" * len(mode) + "-+")
    #    print(f"| {mode.capitalize()} |")
    #    print("+-" + "-" * len(mode) + "-+\n")
    #    print(
    #        rag.query(
    #            "What are the top themes in this story?", param=QueryParam(mode=mode)
    #        )
    #    )


if __name__ == "__main__":
    main(task="ingest")

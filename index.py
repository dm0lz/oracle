import re
import ipdb
import torch
import http.client
import json
import os
from llama_index import Document, ServiceContext, StorageContext, VectorStoreIndex, download_loader, load_index_from_storage
from llama_index.llms import HuggingFaceLLM
from llama_index.prompts import PromptTemplate
from llama_index import (VectorStoreIndex, get_response_synthesizer)
from llama_index.retrievers import VectorIndexRetriever
from llama_index.query_engine import RetrieverQueryEngine
from llama_index.indices.postprocessor import SimilarityPostprocessor
from huggingface_hub import login

login()


def fetch_gist(gist_id):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}
    connection = http.client.HTTPSConnection("api.github.com")
    connection.request("GET", f"/gists/{gist_id}", headers=headers)
    response = connection.getresponse()
    json_response = json.loads(response.read())
    files = json_response['files']
    text_list = []
    for k, v in files.items():
        text_list.extend(json.loads(v['content']))
    return text_list


def get_llm():
    return HuggingFaceLLM(
        context_window=4096,
        max_new_tokens=256,
        generate_kwargs={"temperature": 0.75, "do_sample": True, "top_p": 0.95},
        # query_wrapper_prompt=PromptTemplate("<|USER|>{query_str}<|ASSISTANT|>"),
        tokenizer_name="stabilityai/stablelm-3b-4e1t",
        model_name="stabilityai/stablelm-3b-4e1t",
        model_kwargs={"trust_remote_code": True, "torch_dtype": torch.float16, "use_safetensors": True},
        device_map="auto",
        tokenizer_kwargs={"max_length": 4096},
    )


def get_service_context():
    return ServiceContext.from_defaults(chunk_size=1024, llm=get_llm(), embed_model="local")


def get_documents():
    text_list = fetch_gist("d2e4bc616cbc85ebfe4999fe2a19212e")
    documents = [Document(text=t['content']) for t in text_list]
    BeautifulSoupWebReader = download_loader("BeautifulSoupWebReader")
    loader = BeautifulSoupWebReader()
    websites = loader.load_data(urls=["https://www.remote-neural-monitoring.com"])
    url_pattern = r'https?://\S+|www\.\S+'
    text_without_urls = re.sub(url_pattern, '', websites[0].text)
    websites[0].text = text_without_urls
    documents.extend(websites)
    return documents


def find_or_create_vector_store():
    if (not os.path.exists('./storage')):
        index = VectorStoreIndex.from_documents(get_documents(), service_context=get_service_context())
        index.storage_context.persist(persist_dir='./storage')
    else:
        storage_context = StorageContext.from_defaults(persist_dir='./storage')
        index = load_index_from_storage(storage_context)
        index._service_context = get_service_context()
    return index


def build_query_engine(index):
    retriever = VectorIndexRetriever(
        index=index,
        similarity_top_k=5,
    )
    response_synthesizer = get_response_synthesizer(service_context=index.service_context, response_mode='tree_summarize')
    return RetrieverQueryEngine(
        retriever=retriever,
        response_synthesizer=response_synthesizer,
        node_postprocessors=[
            SimilarityPostprocessor(similarity_cutoff=0.7)
        ]
    )


index = find_or_create_vector_store()
query_engine = build_query_engine(index)
ipdb.set_trace(context=5)
response = query_engine.query("how can the metaverse be accessed ?")
print(response.response)

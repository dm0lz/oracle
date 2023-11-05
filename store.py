import datetime
from llama_index import Document, ServiceContext, VectorStoreIndex, download_loader
from llama_index import (VectorStoreIndex)
from huggingface_hub import login
from llm import get_llm
import http.client
import re
import json
import ipdb
# login()


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


def parse_websites(websites):
    BeautifulSoupWebReader = download_loader("BeautifulSoupWebReader")
    loader = BeautifulSoupWebReader()
    websites = loader.load_data(urls=websites)
    url_pattern = r'https?://\S+|www\.\S+'
    websites_without_urls = []
    for site in websites:
        text_without_urls = re.sub(url_pattern, '', site.text)
        site.text = text_without_urls
        websites_without_urls.append(site)
    return websites_without_urls


def get_documents():
    text_list = fetch_gist("d2e4bc616cbc85ebfe4999fe2a19212e")
    documents = []
    for t in text_list:
        doc = Document(text=t['content'])
        date = datetime.datetime.fromtimestamp(int(t['timestamp'])/1000)
        formatted_date = date.strftime("%B %d, %Y à %H:%M")
        doc.metadata = {"day": formatted_date}
        documents.append(doc)
    websites = parse_websites(["https://www.remote-neural-monitoring.com"])
    documents.extend(websites)
    return documents


documents = get_documents()
service_context = ServiceContext.from_defaults(chunk_size=1024, llm=get_llm(), embed_model="local")
index = VectorStoreIndex.from_documents(documents=documents, service_context=service_context)
index.storage_context.persist(persist_dir='./storage')

# ipdb.set_trace(context=5)

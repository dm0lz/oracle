from flask_socketio import SocketIO
from flask import Flask, render_template
from llama_index import ServiceContext, StorageContext, load_index_from_storage
from llama_index import get_response_synthesizer
from llama_index.retrievers import VectorIndexRetriever
from llama_index.query_engine import RetrieverQueryEngine
from llama_index.indices.postprocessor import SimilarityPostprocessor
from llm import get_llm
import ipdb


def build_query_engine(index):
    retriever = VectorIndexRetriever(
        index=index,
        similarity_top_k=3,
    )
    response_synthesizer = get_response_synthesizer(service_context=index.service_context, response_mode='compact', streaming=True)
    return RetrieverQueryEngine(
        retriever=retriever,
        response_synthesizer=response_synthesizer,
        node_postprocessors=[
            SimilarityPostprocessor(similarity_cutoff=0.7)
        ]
    )


storage_context = StorageContext.from_defaults(persist_dir='./storage')
index = load_index_from_storage(storage_context)
index._service_context = ServiceContext.from_defaults(chunk_size=1024, llm=get_llm(), embed_model="local")
query_engine = build_query_engine(index)


app = Flask(__name__)
socketio = SocketIO(app)


@app.route('/')
def index():
    return render_template('index.html', title='Oracle')


@socketio.on('connect')
def handle_connect():
    print('WebSocket client connected')


@socketio.on('disconnect')
def handle_disconnect():
    print('WebSocket client disconnected')


@socketio.on('message')
def handle_message(message):
    print('Received message:', message)
    # ipdb.set_trace(context=5)
    response = query_engine.query(message['query'])
    socketio.emit('streaming_status', 'streaming')
    for res in response.response_gen:
        socketio.emit('response', {'message': res})
    socketio.emit('streaming_status', 'not_streaming')


if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", allow_unsafe_werkzeug=True, debug=True)

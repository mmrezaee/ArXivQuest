import os
import json
import argparse
from collections import defaultdict
import pandas as pd
from sentence_transformers import SentenceTransformer
from pymilvus import Collection, CollectionSchema, FieldSchema, DataType, connections, utility

import json
import argparse
from collections import defaultdict
import pandas as pd
from sentence_transformers import SentenceTransformer
from pymilvus import Collection, CollectionSchema, FieldSchema, DataType, connections, utility

def connect_to_milvus():
    """Connect to the Milvus server and create a collection for storing document embeddings."""
    connections.connect()
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="text_vector", dtype=DataType.FLOAT_VECTOR, dim=384)
    ]
    schema = CollectionSchema(fields, description="Document Collection")
    collection_name = "document_collection"
    if collection_name in utility.list_collections():
        utility.drop_collection(collection_name)
    collection = Collection(name=collection_name, schema=schema)
    return collection

def encode_text(model, texts, text_type):
    """Encode text into embeddings using a pre-trained model."""
    print(f'Encoding {text_type} to embeddings...')
    embeddings = model.encode(texts, convert_to_tensor=True)
    return embeddings

def create_and_load_index(collection, index_type="IVF_FLAT", metric_type="L2"):
    """Create and load an index for the Milvus collection."""
    index_params = {
        "metric_type": metric_type,
        "index_type": index_type,
        "params": {"nlist": 128}
    }
    collection.create_index(field_name="text_vector", index_params=index_params)
    collection.load()

def search_similar_texts(collection,
                         question_embedding,
                         doc_texts,
                         id_to_index_mapping,
                         doc_question,
                         write_log = False,
                         top_k=10,
                         index_type="IVF_FLAT",
                         metric_type="L2",
                         search_params=None,
                         output_file_path=None):
    """Search for texts similar to the query embeddings in the Milvus collection."""

    # Create and load index with the specified index type and parameters
    create_and_load_index(collection, index_type=index_type, metric_type=metric_type)

    # Set default search parameters if none are provided
    if search_params is None:
        search_params = {"metric_type": metric_type, "params": {"nprobe": 10}}
        #search_params = {"metric_type": metric_type}

    results_list = []

    # Perform search with the specified search parameters
    #for i, query_embedding in enumerate(query_embeddings):
    #if True:
    query_result = {
        "query": doc_question,
        "top_k": top_k,
        "index_type": index_type,
        "metric_type": metric_type,
        "search_params": search_params,
        "results": []
    }

    print(f'*** search_params in collection.search() are {search_params} ***')
    #exit()
    try: 
        results = collection.search([question_embedding.tolist()], "text_vector", search_params, top_k)
    except:
        print(f'couldnt run search because of {search_params}')
        print(f'question_embedding: {question_embedding}')
        print(f'top_k: {top_k}')
        exit()

    for result in results[0]:
        text_index = id_to_index_mapping.get(result.id)
        if text_index is not None:
            query_result["results"].append({
                "text": doc_texts[text_index],
                "score": result.distance
            })
    results_list.append(query_result)

    # Write the results to a JSONLines file
    print(f'writing the results in {output_file_path}')
    print(f'results_list: {results_list}')
    if write_log:
        with open(output_file_path, 'w') as output_file:
            for result in results_list:
                #print(json.dumps(result,indent=4))
                output_file.write(json.dumps(result) + '\n')
    return results_list

def find_answer(doc_texts_list,
                question,
                doc_name,
                write_log=False,
                top_k=10,
                index_type='IVF_FLAT',
                metric_type='L2',
                search_params=None):
    """Main function to process the document and questions."""
    collection = connect_to_milvus()
    model = SentenceTransformer('all-MiniLM-L6-v2')
    text_embeddings = encode_text(model, doc_texts_list, 'sentences')
    mr = collection.insert([text_embeddings.tolist()])
    id_to_index_mapping = {id: index for index, id in enumerate(mr.primary_keys)}
    question_embedding = encode_text(model, question, 'question')
    # Construct the configuration string and output file path
    config_str = f"{index_type}_{metric_type}_top{top_k}_params{str(search_params).replace(' ', '').replace(':', '')}"
    output_folder = os.path.join("logs", config_str)
    os.makedirs(output_folder, exist_ok=True)
    output_file_path = os.path.join(output_folder, f"{doc_name}_{config_str}.json")
    # Pass the output file path to the search_similar_texts function
    results_list= search_similar_texts(collection,
                                       question_embedding,
                                       doc_texts_list,
                                       id_to_index_mapping,
                                       question,
                                       write_log,
                                       top_k,
                                       index_type,
                                       metric_type,
                                       search_params,
                                       output_file_path)
    return results_list

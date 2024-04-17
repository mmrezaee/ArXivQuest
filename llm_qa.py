import os
import json
import argparse
from collections import defaultdict
import pandas as pd
from sentence_transformers import SentenceTransformer
from pymilvus import Collection, CollectionSchema, FieldSchema, DataType, connections, utility
import numpy as np
from utils import MODEL_EMBEDDING_DIMENSIONS
from numpy import save

def connect_to_milvus(embed_dim):
    """
    Connect to the Milvus server and create a collection for storing document embeddings.
    
    Args:
        embed_dim (int): The dimension of the embeddings.

    Returns:
        Collection: A Milvus Collection object for storing embeddings.
    """
    connections.connect()
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="text_vector", dtype=DataType.FLOAT_VECTOR, dim=embed_dim)
    ]
    schema = CollectionSchema(fields, description="Document Collection")
    collection_name = "document_collection"
    if collection_name in utility.list_collections():
        utility.drop_collection(collection_name)
    collection = Collection(name=collection_name, schema=schema)
    return collection

def encode_text(model, texts, text_type):
    """
    Encode text into embeddings using a pre-trained Sentence Transformer model.
    
    Args:
        model (SentenceTransformer): The pre-trained Sentence Transformer model.
        texts (list of str): Texts to be encoded.
        text_type (str): A descriptive type label for logging purposes.

    Returns:
        np.ndarray: An array of embeddings.
    """
    print(f'Encoding {text_type} to embeddings...')
    embeddings = model.encode(texts, convert_to_tensor=True)
    return embeddings

def create_and_load_index(collection,
                          index_type="IVF_FLAT",
                          metric_type="L2"):
    """
    Create and load an index for the Milvus collection to optimize search operations.
    
    Args:
        collection (Collection): The Milvus collection to create the index on.
        index_type (str): The type of index to create.
        metric_type (str): The metric type to use with the index.
    """
    index_params = {
        "metric_type": metric_type,
        "index_type": index_type,
        "params": {"nlist": 10}
    }
    collection.create_index(field_name="text_vector", index_params=index_params)
    collection.load()

def search_similar_texts(collection,
                         question_embedding,
                         doc_texts,
                         id_to_index_mapping,
                         doc_question, 
                         use_cache,
                         write_log = False,
                         top_k=10,
                         index_type="IVF_FLAT",
                         metric_type="L2",
                         search_params=None,
                         probe_params = None,
                         output_file_path=None):
    """
    Searches for texts in the Milvus collection that are similar to the 
    query represented by the question_embedding.

    Args:
        collection (Collection): The Milvus collection where the documents are stored.
        question_embedding (ndarray): The embedding vector of the query question.
        doc_texts (list of str): List of document texts available in the collection.
        id_to_index_mapping (dict): A mapping from Milvus returned ids to the document 
        indices in doc_texts.
        doc_question (str): The original text of the query question.
        use_cache (bool): Flag to determine whether to use cached data or not.
        write_log (bool): If True, search results will be written to a log file specified
        by output_file_path.
        top_k (int): Number of top results to retrieve in the search.
        index_type (str): The type of index used in the Milvus collection for searching.
        metric_type (str): The metric type used in the search index (e.g., L2, cosine).
        search_params (dict, optional): Additional search parameters for Milvus. 
        probe_params (dict, optional): Parameters for search probing, unused if None.
        output_file_path (str, optional): Path to the file where results should be logged.

    Returns:
        list: A list containing dictionaries of search results with the matching texts and their scores.
    """

    # Create and load index with the specified index type and parameters
    create_and_load_index(collection, index_type=index_type, metric_type=metric_type)

    # Set default search parameters if none are provided
    if search_params is None:
        search_params = {"metric_type": metric_type, "params": {"nprobe": 10}}

    results_list = []

    # Perform search with the specified search parameters
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
    if write_log:
        with open(output_file_path, 'w') as output_file:
            for result in results_list:
                #print(json.dumps(result,indent=4))
                output_file.write(json.dumps(result) + '\n')
    return results_list

def prepare_output_paths(doc_name,
                         model_name,
                         index_type,
                         metric_type,
                         search_params):
    """
    Generates and prepares file paths for storing results and embeddings.

    Args:
        doc_name (str): Name of the document or dataset being processed.
        model_name (str): Name of the Sentence Transformer model used for generating embeddings.
        index_type (str): Type of index used in the Milvus search.
        metric_type (str): Metric type used for the index in Milvus.
        search_params (dict): Search parameters used in Milvus search.

    Returns:
        tuple: A tuple containing the path for the output file and the output tensor file.
    """
    config_str = f"{doc_name}_{index_type}_{metric_type}_params{str(search_params).replace(' ', '').replace(':', '')}"
    output_folder = os.path.join("logs", config_str)
    os.makedirs(output_folder, exist_ok=True)
    output_file_path = os.path.join(output_folder, f"{doc_name}_{model_name}_{config_str}.json")
    output_tensors_path = os.path.join(os.getcwd(), output_folder, f"{doc_name}_{model_name}_{config_str}.npy")
    return output_file_path, output_tensors_path

# Example of how to use the function in your main code:
def find_answer(doc_texts_list,
                question,
                doc_name,
                model_name ='all-MiniLM-L6-v2',
                use_cache = True,
                write_log=False,
                top_k=10,
                index_type='IVF_FLAT',
                metric_type='L2',
                search_params=None):
    """
    Processes the document and questions using embeddings, managing their storage,
    retrieval, and searching within the Milvus collection. It involves encoding texts,
    saving configurations, and results in a structured format in the 'logs' folder.

    Args:
        doc_texts_list (list): List of document texts to process.
        question (str): Question string whose answer is to be found in the document texts.
        doc_name (str): Name of the document being processed, used for naming files and logs.
        model_name (str): Name of the Sentence Transformer model used for generating embeddings.
        use_cache (bool): Flag to determine whether to use cached embeddings or generate new ones.
        write_log (bool): Flag to enable logging of the search results to a file.
        top_k (int): Number of top results to return from the search.
        index_type (str): Type of index used in Milvus for searching embeddings.
        metric_type (str): Metric type used in Milvus for the index.
        search_params (dict, optional): Additional search parameters for Milvus. Defaults to None.

    Returns:
        list: A list containing the search results with documents that best match the question.
    """



    # Prepare paths for output files and embeddings
    output_file_path, output_tensors_path = prepare_output_paths(doc_name, model_name,
                                                                 index_type, metric_type,
                                                                 search_params)

    model = SentenceTransformer(model_name)
    embed_dim = MODEL_EMBEDDING_DIMENSIONS[model_name]
    collection = connect_to_milvus(embed_dim)


    if not use_cache or not os.path.exists(output_tensors_path):
        text_embeddings = encode_text(model, doc_texts_list, 'sentences')
        text_embeddings_npy = text_embeddings.cpu().numpy()
        text_embeddings_list = text_embeddings.tolist()
        save(output_tensors_path,text_embeddings_npy)
        #mr = collection.insert([text_embeddings.tolist()])
    else:
        print(f'loading from {output_tensors_path}')
        text_embeddings_npy = np.load(output_tensors_path)
        text_embeddings_list = text_embeddings_npy.tolist()


    mr = collection.insert([text_embeddings_list])
    id_to_index_mapping = {id: index for index, id in enumerate(mr.primary_keys)}
    question_embedding = encode_text(model, question, 'question')
    # Construct the configuration string and output file path
    # Pass the output file path to the search_similar_texts function
    results_list= search_similar_texts(collection,
                                       question_embedding,
                                       doc_texts_list,
                                       id_to_index_mapping,
                                       question,
                                       use_cache,
                                       write_log,
                                       top_k,
                                       index_type,
                                       metric_type,
                                       search_params,
                                       output_file_path)
    return results_list


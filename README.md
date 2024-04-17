# ArXivQuest: Ask Questions From ArXiv Papers!

ArXiv now offers an HTML version of (recent) papers. This project provides a web-based interface that allows users to load, view, and interactively query these HTML documents. It uses Milvus to retrieve and highlight document sections relevant to the user's queries and automatically scrolls to these highlights.



## Problem Statement

Retrieving specific information from large documents based on user queries poses a significant challenge that demands efficient text searching capabilities. This project leverages vector embeddings for semantic search to address this challenge.

## Features

![Image](./figs/sample_usage.gif)

This application is built on Flask and is designed to run locally. Start the server by running:
  ```
  python app.py
  ```
- **HTML Document Viewer**: Loads and displays HTML content from specified URLs.
- **Interactive Query Interface**: Enables users to input questions and receive contextually relevant answers.
- **Highlighting Relevant Content**: Automatically highlights and scrolls to sections of the document relevant to the user's query.
- **Milvus Integration**: Utilizes [Milvus](https://milvus.io/) for efficient retrieval of document sections based on vector similarity.

## Approach

The project follows these steps:
1. **HTML Preprocessing**: Parses HTML using BeautifulSoup to extract sentences and tables.
2. **Sentence Embedding**: Uses the SentenceTransformer library to transform extracted sentences into vector embeddings, crucial for efficient similarity searches.
3. **Milvus Collection and Indexing**: Establishes a Milvus Collection to store sentence embeddings and creates an index for fast and accurate retrieval.
4. **Query Processing**: Converts sample questions into embeddings using the same SentenceTransformer model to ensure consistency.
5. **Exploring Different Configurations**: Explores various configurations to search for similar texts based on query embeddings, testing different combinations of the following parameters:
   - **Index Types**: [IVF_FLAT](https://milvus.io/docs/index.md), [IVF_SQ8](https://milvus.io/docs/index.md)
   - **Metric Types**: [L2](https://milvus.io/docs/metric.md), [IP](https://milvus.io/docs/metric.md)
   - **Models**: Sentence transformers for embeddings. Options include:
     - [all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
     - [all-MiniLM-L12-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L12-v2)
     - [all-distilroberta-v1](https://huggingface.co/sentence-transformers/all-distilroberta-v1)
     - [all-mpnet-base-v2](https://huggingface.co/sentence-transformers/all-mpnet-base-v2)
   - **Top K Results**: Specifies the number of top answers to show.

## Project Structure

- `app.py`: Main Flask application file.
- `llm_qa.py`: Converts arXiv papers and questions to sentence transformer embeddings and retrieves the top K answers.
- `utils.py`: Provides preprocessing tools for extracting sentences and tables from papers.
- `templates/`: Contains HTML files for the web interface.
- `static/`: Stores CSS and JavaScript files.
- `requirements.txt`: Lists all Python libraries required by the project.

## Installation

- [Install Milvus Standalone with Docker](https://milvus.io/docs/install_standalone-docker.md)
- Required packages are listed in `requirements.txt`. Install them using the command:
  ```
  pip install -r requirements.txt
  ```

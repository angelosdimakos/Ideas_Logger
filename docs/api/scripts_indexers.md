# Docstring Report for `scripts/indexers/`


## `scripts\indexers\__init__`


The `indexers` module provides classes and utilities for building, managing, and searching vector indexes over log and summary data.
Core features include:
- Construction of FAISS indexes for both raw log entries and summarized corrections.
- Support for semantic search using SentenceTransformer embeddings.
- Management of index and metadata persistence for efficient retrieval.
- Utilities for rebuilding, updating, and searching indexes across different data granularities.
This module enables fast and flexible semantic search over structured and unstructured idea logs, supporting downstream applications such as idea retrieval, analytics, and intelligent querying.


## `scripts\indexers\base_indexer`


base_indexer.py
This module defines the BaseIndexer class, which provides core functionality for building, saving, loading, and searching FAISS vector indexes over log and summary data.
Core features include:
- Initializing index and metadata paths based on project configuration and index type (summary or raw).
- Building a FAISS index from text data using SentenceTransformer embeddings.
- Saving and loading both the FAISS index and associated metadata.
- Performing semantic search over indexed data, returning the most relevant results with similarity scores.
- Supporting flexible configuration and robust error handling for index operations.
Intended for use as a base class for specialized indexers in the Zephyrus project, enabling fast and flexible semantic search over structured logs and summaries.


### Classes

#### BaseIndexer

### Functions

#### __init__

Initializes the BaseIndexer object.
Sets the paths to the summaries file, FAISS index file, and metadata file based on the
provided `index_name` and the `ZephyrusPaths` object.  If `index_name` is "summary",
the paths are set to the correction summaries file, FAISS index file, and metadata file.
If `index_name` is "raw", the paths are set to the JSON log file, raw log index file,
and raw log metadata file.  In all other cases, a ValueError is raised.
Also, loads the SentenceTransformer model specified by the "embedding_model"
configuration key, or defaults to "all-MiniLM-L6-v2" if the key is missing.

**Arguments:**
paths (ZephyrusPaths): The paths configuration for the indexer.
index_name (str): The name of the index to create, either "summary" or "raw".
Raises:
ValueError: If `index_name` is not "summary" or "raw".

#### _load_model

#### load_index

Loads the FAISS index and associated metadata from their respective files.
This method reads the index from the file specified by `self.index_path` and loads
the metadata from the file specified by `self.metadata_path`. If either file does not
exist, a FileNotFoundError is raised.
Raises:
FileNotFoundError: If the index file or metadata file is not found.

#### search

Searches the FAISS index for the given query and returns the top-k most relevant results.

**Arguments:**
query (str): The search query.
top_k (int, optional): The number of top results to return. Defaults to 5.

**Returns:**
List[Dict[str, Any]]: A list of dictionaries containing the search results. Each dictionary includes the
following keys:
- "date"
- "main_category"
- "subcategory"
- "timestamp"
- "similarity" (the similarity score, computed as 1.0 / (1.0 + distance))

#### build_index

Builds a FAISS index from provided texts and metadata.

**Arguments:**
texts (List[str]): A list of texts to encode and index.
meta (List[Dict[str, Any]]): Metadata per text entry.
fail_on_empty (bool): Raise ValueError if input is empty (useful for tests).

**Returns:**
bool: True if successful, False otherwise.

#### save_index

Saves the FAISS index to a file, and the associated metadata.
This method must be called after `build_index` or `load_index` has been called.

## `scripts\indexers\raw_log_indexer`


This module defines the RawLogIndexer class for building and managing a FAISS vector index
over raw log entries from zephyrus_log.json.
Core features:
- Loading and parsing raw log entries by date, main category, and subcategory.
- Extracting entry content and metadata for semantic indexing.
- Building, saving, loading, and rebuilding a FAISS index for full-text vector search.
- Robust error handling and logging for file I/O and data processing.
- Designed for use in the Zephyrus project to enable fast, flexible semantic search.


### Classes

#### RawLogIndexer

Builds a FAISS index from raw entries in zephyrus_log.json.
Used for full-text vector search across all logged ideas (not just summaries).
Attributes:
log_path (str): The path to the JSON log file.

### Functions

#### __init__

Initializes the RawLogIndexer with the specified paths and optionally loads the index.

**Arguments:**
paths (ZephyrusPaths): The paths configuration for the indexer.
autoload (bool): Whether to automatically load the index on initialization.
Defaults to True.
Raises:
FileNotFoundError: If the index files are not found during autoload.

#### load_entries

Loads raw entries from the zephyrus_log.json file.

**Returns:**
Tuple[List[str], List[Dict[str, Any]]]: A tuple containing a list of entry contents
and a list of metadata dictionaries.
Raises:
FileNotFoundError: If the log file does not exist.
json.JSONDecodeError: If the JSON file is malformed.

#### _process_categories

Processes categories for a given date, updating the texts and metadata.

**Arguments:**
date (str): The date of the entries being processed.
categories (Dict[str, Any]): A dictionary of main categories.
texts (List[str]): The list to append entry contents to.
meta (List[Dict[str, Any]]): The list to append entry metadata to.

**Returns:**
Tuple[List[str], List[Dict[str, Any]]]: Updated texts and metadata lists.

#### _process_subcategories

Processes subcategories within a main category for a given date.

**Arguments:**
date (str): The date of the entries being processed.
main_cat (str): The main category of the entries.
subcats (Dict[str, Any]): A dictionary of subcategories.
texts (List[str]): The list to append entry contents to.
meta (List[Dict[str, Any]]): The list to append entry metadata to.

**Returns:**
Tuple[List[str], List[Dict[str, Any]]]: Updated texts and metadata lists.

#### _process_entries

Processes a list of entries for a given date, main category, and subcategory.

**Arguments:**
date (str): The date of the entries being processed.
main_cat (str): The main category of the entries.
subcat (str): The subcategory of the entries.
entries (List[Any]): A list of entries to process.
texts (List[str]): The list to append entry contents to.
meta (List[Dict[str, Any]]): The list to append entry metadata to.

**Returns:**
Tuple[List[str], List[Dict[str, Any]]]: Updated texts and metadata lists.

#### build_index_from_logs

Loads entries from file and rebuilds FAISS index.

**Returns:**
bool: Whether the index was successfully rebuilt.
Raises:
Exception: If an error occurs while building the index.

#### rebuild

Rebuilds the raw log index from scratch.
This method loads entries from the log file, rebuilds the FAISS index, and saves the new index.
Raises:
Exception: If an error occurs while rebuilding the index.

## `scripts\indexers\summary_indexer`


summary_indexer.py
This module defines the SummaryIndexer class for building and managing a FAISS vector index over summarized entries from correction_summaries.json.
Core features include:
- Loading and parsing summarized entries organized by date, main category, and subcategory.
- Extracting summary texts and associated metadata for semantic indexing.
- Building, saving, loading, and rebuilding a FAISS index for semantic search across all summarized corrections.
- Robust error handling and logging for file I/O and data processing.
- Designed for use in the Zephyrus project to enable fast, flexible semantic search over all summarized log data.


### Classes

#### SummaryIndexer

Builds a FAISS index from summarized entries in correction_summaries.json.
Core features include loading and parsing summarized entries, extracting summary texts,
and managing the FAISS index for semantic search.

### Functions

#### __init__

Initializes a SummaryIndexer object.

**Arguments:**
paths (ZephyrusPaths): An instance containing the necessary file paths.
autoload (bool, optional): Flag indicating whether to load the index automatically. Defaults to True.

#### load_entries

Loads summarized entries from the correction_summaries.json file.

**Returns:**
Tuple[List[str], List[Dict[str, Any]]]: Summarized entry texts and metadata.

#### _process_categories

#### _process_subcategories

#### _process_batches

#### load_index

Load the FAISS index and associated metadata from their respective files.
Raises:
FileNotFoundError: If the index file or metadata file is not found.

#### save_index

Save the FAISS index and associated metadata to their respective files.
This method delegates to the BaseIndexer implementation.

#### rebuild_index

Rebuild the FAISS index from the summarized entries.
This method invokes building index from logs and saving it.

#### build_index_from_logs

Loads entries from file and rebuilds FAISS index.

**Returns:**
bool: Whether the index was successfully rebuilt.

#### rebuild

Rebuild the summary index from scratch.
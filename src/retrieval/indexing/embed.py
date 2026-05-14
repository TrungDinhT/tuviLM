import pdfplumber
import requests
import json
from typing import List, Dict, Any, Optional

from tqdm import tqdm

from src.retrieval.constant import REMOVE_PHRASE


class JinaEmbeddings:
    """
    A class to handle embeddings using Jina AI API
    """

    def __init__(self, api_key: str = "jina_609ca1a965aa4cf5bc41ef4b4908c709Bfd_GQY4ET4Q0OQkZ15Jt1y3aN9b"):
        """
        Initialize the JinaEmbeddings client

        Args:
            api_key (str): Jina AI API key
        """
        self.api_key = api_key
        self.base_url = "https://api.jina.ai/v1/embeddings"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

    def get_embeddings(
        self,
        texts: List[str],
        model: str = "jina-embeddings-v3",
        task: str = "text-matching"
    ) -> Optional[Dict[str, Any]]:
        """
        Get embeddings for a list of texts

        Args:
            texts (List[str]): List of texts to embed
            model (str): Model to use for embeddings (default: jina-embeddings-v3)
            task (str): Task type for embeddings (default: text-matching)

        Returns:
            Optional[Dict[str, Any]]: API response containing embeddings or None if failed
        """
        payload = {
            "model": model,
            "task": task,
            "input": texts
        }

        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Error making request to Jina API: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return None

    def get_single_embedding(
        self,
        text: str,
        model: str = "jina-embeddings-v3",
        task: str = "text-matching"
    ) -> Optional[List[float]]:
        """
        Get embedding for a single text

        Args:
            text (str): Text to embed
            model (str): Model to use for embeddings (default: jina-embeddings-v3)
            task (str): Task type for embeddings (default: text-matching)

        Returns:
            Optional[List[float]]: Embedding vector or None if failed
        """
        result = self.get_embeddings([text], model, task)
        if result and "data" in result and len(result["data"]) > 0:
            return result["data"][0]["embedding"]
        return None

    def get_embeddings_batch(
        self,
        texts: List[str],
        batch_size: int = 100,
        model: str = "jina-embeddings-v3",
        task: str = "text-matching"
    ) -> List[List[float]]:
        """
        Get embeddings for texts in batches

        Args:
            texts (List[str]): List of texts to embed
            batch_size (int): Size of each batch (default: 100)
            model (str): Model to use for embeddings (default: jina-embeddings-v3)
            task (str): Task type for embeddings (default: text-matching)

        Returns:
            List[List[float]]: List of embedding vectors
        """
        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            result = self.get_embeddings(batch, model, task)

            if result and "data" in result:
                batch_embeddings = [item["embedding"] for item in result["data"]]
                all_embeddings.extend(batch_embeddings)
            else:
                print(f"Failed to get embeddings for batch {i//batch_size + 1}")
                # Add empty embeddings for failed batch to maintain alignment
                all_embeddings.extend([[] for _ in batch])

        return all_embeddings


# Convenience function for quick usage
def get_embeddings(
    texts: List[str],
    api_key: str = "jina_609ca1a965aa4cf5bc41ef4b4908c709Bfd_GQY4ET4Q0OQkZ15Jt1y3aN9b",
    model: str = "jina-embeddings-v3",
    task: str = "text-matching"
) -> Optional[Dict[str, Any]]:
    """
    Convenience function to get embeddings

    Args:
        texts (List[str]): List of texts to embed
        api_key (str): Jina AI API key
        model (str): Model to use for embeddings (default: jina-embeddings-v3)
        task (str): Task type for embeddings (default: text-matching)

    Returns:
        Optional[Dict[str, Any]]: API response containing embeddings or None if failed
    """
    embedder = JinaEmbeddings(api_key)
    return embedder.get_embeddings(texts, model, task)


# Example usage
if __name__ == "__main__":
    # Example texts from the curl request
    PDF_PATH   = "data/tuvitanbien.pdf"
    CHUNK_SIZE = 1500            # characters
    STRIDE     = 400             # overlap

    chunks, metas = [], []

    with pdfplumber.open(PDF_PATH) as pdf:
        for page_num, page in tqdm(enumerate(pdf.pages, 1)):
            txt = page.extract_text() or ""
            for start in range(0, len(txt), CHUNK_SIZE - STRIDE):
                chunk = txt[start : start + CHUNK_SIZE]
                chunk = chunk.replace(REMOVE_PHRASE, "")
                chunk = chunk.replace("\n", " \n ").strip()
                chunks.append(chunk)
                metas.append({"page": page_num})


    # Create embedder instance
    embedder = JinaEmbeddings()
    results = []

    # Get embeddings
    with open("data/index/faiss/jina_embeddings.jsonl", "w") as fo:
        for ids, chunk in tqdm(enumerate(chunks)):
            result = embedder.get_embeddings([chunk])
            if result and "data" in result:
                data = result["data"][0]
                data["text"] = chunk
                data["index"] = ids
                fo.write(json.dumps(data) + "\n")






    # if result:
    #     print(f"Successfully got embeddings for {len(result['data'])} texts")
    #     print(result)
    # else:
    #     print("Failed to get embeddings")

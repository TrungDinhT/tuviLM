import re
import pdfplumber
from typing import List, Dict, Tuple, Optional
from tqdm import tqdm

from src.retrieval.constant import REMOVE_PHRASE


def extract_chunks_with_headers(
    file_path: str,
    *,
    start_page: int = 30,
    end_page: int | None = None,
    lower_only : bool = False
) -> Tuple[List[str], List[Dict]]:
    """
    Extract chunks from PDF starting from a specific page, using headers as chunk boundaries.

    Args:
        start_page: Page number to start extraction from (1-indexed)

    Returns:
        Tuple of (chunks, metadata) where each chunk contains text between headers
    """
    # Header patterns
    header_patterns = [
        (r'\n(\d+)\.\s+(.+?)\n', 1),  # Type 1: "\n{number}. {text}\n"
        (r'\n(\d+)\.(\d+)\.\s+(.+?)\n', 2),  # Type 2: "\n{number}.{number}. {text}\n"
        (r'\n(\d+)\.(\d+)\.(\d+)\.\s+(.+?)\n', 3)  # Type 3: "\n{number}.{number}.{number}. {text}\n"
    ]

    chunks = []
    metas = []
    last_header = None
    current_chunk = ""
    current_header = None

    # Track hierarchical headers
    current_type1_header = None
    current_type2_header = None

    with pdfplumber.open(file_path) as pdf:
        total_pages = end_page if end_page else len(pdf.pages)

        for page_num in tqdm(range(start_page - 1, total_pages), desc="Processing pages"):

            page = pdf.pages[page_num]
            page_text = page.extract_text() or ""

            # Remove the specified phrase
            page_text = page_text.replace(REMOVE_PHRASE, "")

            # Remove \n for newline in same paragraph - replace {text_lower}\n{text_lower} with {text_lower} {text_lower}
            page_text = re.sub(r'([a-zàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ])\n([a-zàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ])', r'\1 \2', page_text)

            if lower_only:
                # Convert to lowercase
                page_text = page_text.lower()

            # Find all headers in the page
            headers_found = []
            for pattern, header_type in header_patterns:
                matches = list(re.finditer(pattern, page_text))
                for match in matches:
                    headers_found.append({
                        'start': match.start(),
                        'end': match.end(),
                        'match': match,
                        'type': header_type,
                        'full_text': match.group(0)
                    })

            # Sort headers by position
            headers_found.sort(key=lambda x: x['start'])

            # Process text between headers
            page_start = 0

            for i, header_info in enumerate(headers_found):
                # Get text before this header
                text_before_header = page_text[page_start:header_info['start']]

                # If we have accumulated text from previous processing, add it to current chunk
                if current_chunk or text_before_header.strip():
                    chunk_text = current_chunk + text_before_header

                    if chunk_text.strip():
                        # Create chunk with previous header or current header if no previous
                        header_to_use = current_header if current_header else _extract_header_info(header_info)

                        chunks.append(chunk_text.strip())

                        # Build simplified header metadata
                        header_1 = current_type1_header['full_header'] if current_type1_header else None
                        header_2 = current_type2_header['full_header'] if current_type2_header else None
                        header_3 = None

                        if header_to_use:
                            if header_to_use.get('type') == 1:
                                header_1 = header_to_use['full_header']
                            elif header_to_use.get('type') == 2:
                                header_2 = header_to_use['full_header']
                            elif header_to_use.get('type') == 3:
                                header_3 = header_to_use['full_header']

                        metas.append({
                            'header_1': header_1,
                            'header_2': header_2,
                            'header_3': header_3
                        })

                # Start new chunk with current header
                current_header = _extract_header_info(header_info)

                # Update hierarchical header tracking
                if header_info['type'] == 1:
                    current_type1_header = current_header
                    current_type2_header = None  # Reset type 2 when we encounter new type 1
                elif header_info['type'] == 2:
                    current_type2_header = current_header
                elif header_info['type'] == 3:
                    pass  # Type 3 doesn't reset anything, just uses current hierarchy

                current_chunk = header_info['full_text']
                page_start = header_info['end']

            # Handle remaining text on the page
            remaining_text = page_text[page_start:]
            if remaining_text.strip():
                current_chunk += remaining_text

            # If no headers found on this page, add all text to current chunk
            if not headers_found and page_text.strip():
                current_chunk += page_text

        # Add final chunk if there's remaining content
        if current_chunk.strip():
            chunks.append(current_chunk.strip())

            # Build simplified header metadata for final chunk
            header_1 = current_type1_header['full_header'] if current_type1_header else None
            header_2 = current_type2_header['full_header'] if current_type2_header else None
            header_3 = None

            if current_header:
                if current_header.get('type') == 1:
                    header_1 = current_header['full_header']
                elif current_header.get('type') == 2:
                    header_2 = current_header['full_header']
                elif current_header.get('type') == 3:
                    header_3 = current_header['full_header']

            metas.append({
                'header_1': header_1,
                'header_2': header_2,
                'header_3': header_3
            })

    return chunks, metas


def _extract_header_info(header_info: Dict) -> Dict:
    """Extract header information from regex match."""
    match = header_info['match']
    header_type = header_info['type']

    if header_type == 1:
        # Type 1: "\n{number}. {text}\n"
        return {
            'type': 1,
            'number': match.group(1),
            'text': match.group(2).strip(),
            'full_header': f"{match.group(1)}. {match.group(2).strip()}"
        }
    elif header_type == 2:
        # Type 2: "\n{number}.{number}. {text}\n"
        return {
            'type': 2,
            'number': f"{match.group(1)}.{match.group(2)}",
            'text': match.group(3).strip(),
            'full_header': f"{match.group(1)}.{match.group(2)}. {match.group(3).strip()}"
        }
    elif header_type == 3:
        # Type 3: "\n{number}.{number}.{number} {text}\n"
        return {
            'type': 3,
            'number': f"{match.group(1)}.{match.group(2)}.{match.group(3)}",
            'text': match.group(4).strip(),
            'full_header': f"{match.group(1)}.{match.group(2)}.{match.group(3)}. {match.group(4).strip()}"
        }

    return {}


def get_chunks_and_metadata(start_page: int = 30) -> Tuple[List[str], List[Dict]]:
    """
    Main function to extract chunks and metadata from PDF.

    Args:
        start_page: Page number to start extraction from (1-indexed)

    Returns:
        Tuple of (chunks, metadata)
    """
    return extract_chunks_with_headers(start_page)


if __name__ == "__main__":
    print("Testing header-based chunking...")
    print("=" * 50)

    # Test the chunking function
    chunks, metas = extract_chunks_with_headers(start_page=31)

    print(f"Total chunks extracted: {len(chunks)}")
    print(f"Total metadata entries: {len(metas)}")
    print("=" * 50)

    # Display first few chunks with their metadata
    for i in range(min(10, len(chunks))):
        print(f"\n--- Chunk {i+1} ---")
        if metas[i]['header_1']:
            print(f"Header 1: {metas[i]['header_1']}")
        if metas[i]['header_2']:
            print(f"Header 2: {metas[i]['header_2']}")
        if metas[i]['header_3']:
            print(f"Header 3: {metas[i]['header_3']}")

        print(f"Content (first 200 chars): {chunks[i][:200]}...")
        print("-" * 30)

    # Display some statistics
    header_levels = {'level_1': 0, 'level_2': 0, 'level_3': 0, 'no_header': 0}
    for meta in metas:
        if meta['header_3']:
            header_levels['level_3'] += 1
        elif meta['header_2']:
            header_levels['level_2'] += 1
        elif meta['header_1']:
            header_levels['level_1'] += 1
        else:
            header_levels['no_header'] += 1

    print(f"\nHeader level distribution:")
    for level, count in header_levels.items():
        print(f"  {level}: {count} chunks")

import hashlib

from langchain_text_splitters import RecursiveCharacterTextSplitter


def create_chunk_id(document_id: str, chunk_index: int, text: str) -> str:
    content = f"{document_id}:{chunk_index}:{text}"

    digest = hashlib.sha256(
        content.encode("utf-8")
    ).hexdigest()[:16]

    return f"{document_id}_{chunk_index:04d}_{digest}"


def chunk_documents(
    documents: list[dict],
    chunk_size: int = 800,
    chunk_overlap: int = 120,
) -> list[dict]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            "",
        ],
    )

    chunks = []

    for document in documents:
        text_chunks = splitter.split_text(document["text"])

        for index, text in enumerate(text_chunks):
            cleaned_text = text.strip()

            if not cleaned_text:
                continue

            chunk_id = create_chunk_id(
                document_id=document["document_id"],
                chunk_index=index,
                text=cleaned_text,
            )

            chunks.append(
                {
                    "chunk_id": chunk_id,
                    "document_id": document["document_id"],
                    "file_name": document["file_name"],
                    "chunk_index": index,
                    "text": cleaned_text,
                }
            )

    return chunks

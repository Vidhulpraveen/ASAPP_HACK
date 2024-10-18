import uuid
import cohere
import qdrant_client
from qdrant_client.http import models
import pdfplumber
import os
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from langchain.text_splitter import RecursiveCharacterTextSplitter
from retrying import retry
from typing import Optional

# FastAPI app setup
app = FastAPI(
    title="PDF Chatbot API with Qdrant and Cohere",
    version="2.0",
    description="A chatbot that allows you to upload PDFs, stores embeddings in Qdrant, and answers questions using Cohere.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Cohere client
cohere_api_key = "7niJGSzUgsOJFjtvdy6jOhvFK8rp0xnGdR9QVOAI"
cohere_client = cohere.Client(cohere_api_key)

# Initialize Qdrant Cloud client (replace with your actual Qdrant Cloud URL and API key)
qdrant_client = qdrant_client.QdrantClient(
    url="https://91192707-948f-4785-b4f6-348c269428ab.europe-west3-0.gcp.cloud.qdrant.io",
    api_key="4dJlEkfLKM0SDdO86qtwf_SMOHLiWHBTLammQRLnCz6ddMN5jasNNg",
    timeout=60,
)

collection_name = "research_papers"

# Create Qdrant collection if it doesn't exist
try:
    qdrant_client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(size=4096, distance=models.Distance.COSINE),
    )
except Exception as e:
    print("Collection already exists:", e)


# Model for chat request
class ChatRequest(BaseModel):
    user_id: str
    question: str
    document_index: Optional[int] = None


# Function to extract text from a PDF
def extract_text_from_pdf(file: UploadFile) -> str:
    try:
        with pdfplumber.open(file.file) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error processing PDF")


# Function to chunk text
def chunk_text(text: str) -> list:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        length_function=len,
        separators=["\n\n", "\n", " ", ""],
    )
    return text_splitter.split_text(text)


# Function to generate embeddings using Cohere
def generate_embeddings(texts: list) -> list:
    response = cohere_client.embed(texts=texts).embeddings
    return response


# Retry mechanism for upsert operation
@retry(stop_max_attempt_number=5, wait_fixed=2000)
def upsert_with_retry(points_batch):
    qdrant_client.upsert(
        collection_name=collection_name,
        points=points_batch
    )


# Endpoint to upload PDFs, process them, and store embeddings in Qdrant
@app.post("/upload_pdfs/")
async def upload_pdfs(files: List[UploadFile] = File(...), user_id: str = "default_user"):
    # Ensure all files are PDFs
    for file in files:
        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Invalid file type. Only PDF files are accepted.")

    # Process each PDF
    for file in files:
        # Extract text
        text = extract_text_from_pdf(file)

        # Chunk text
        chunks = chunk_text(text)

        # Generate embeddings
        embeddings = generate_embeddings(chunks)

        # Store embeddings in Qdrant
        points_batch = []
        for idx, (embedding, chunk) in enumerate(zip(embeddings, chunks)):
            point = models.PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={"filename": file.filename, "chunk": chunk}
            )
            points_batch.append(point)

        if points_batch:
            upsert_with_retry(points_batch)

    return {"message": f"{len(files)} PDFs uploaded successfully and embeddings stored in Qdrant."}


# Function to search for similar chunks in Qdrant
# def search_similar_chunks(user_query: str, top_k=5):
#     query_embedding = generate_embeddings([user_query])[0]
#     search_result = qdrant_client.search(
#         collection_name=collection_name,
#         query_vector=query_embedding,
#         limit=top_k
#     )

#     similar_chunks = [
#         {"chunk": result.payload["chunk"], "filename": result.payload["filename"], "score": result.score}
#         for result in search_result
#     ]
#     return similar_chunks

# Function to search for similar chunks in Qdrant
def search_similar_chunks(user_query: str, top_k=5):
    # Generate embedding for the user query
    query_embedding = generate_embeddings([user_query])[0]

    # Search for top_k similar chunks in Qdrant Cloud
    search_result = qdrant_client.search(
        collection_name=collection_name,
        query_vector=query_embedding,
        limit=top_k
    )

    # Extract context from search results
    similar_chunks = [
        {
            "chunk": result.payload["chunk"],
            "filename": result.payload["filename"],
            "score": result.score
        }
        for result in search_result
    ]

    # Print the source documents and chunks
    print("\nSource Documents:")
    for chunk in similar_chunks:
        print(f"Document: {chunk['filename']} (Score: {chunk['score']:.4f})")  # Displaying up to 4 decimal places for the score
        print(f"Chunk: {chunk['chunk']}\n")

    return similar_chunks


# Function to generate an answer based on context
def generate_answer_with_context(user_query: str, similar_chunks: list) -> str:
    #context_text = "\n\n".join([chunk["chunk"] for chunk in similar_chunks])
    context_text = "\n\n".join([f"Filename: {chunk['filename']}\nChunk: {chunk['chunk']}" for chunk in similar_chunks])
    prompt = f"Context:\n{context_text}\n\nQuestion: {user_query}\n\nAnswer:"

    response = cohere_client.generate(
        model='command-xlarge-nightly',
        prompt=prompt,
        max_tokens=150,
        temperature=0.7,
        stop_sequences=["\n"]
    )

    return response.generations[0].text.strip()


# Endpoint for asking questions based on PDF contents
@app.post("/ask/")
async def ask_question(request: ChatRequest):
    user_query = request.question

    # Search for similar chunks based on the user's query
    similar_chunks = search_similar_chunks(user_query)

    if not similar_chunks:
        raise HTTPException(status_code=404, detail="No relevant information found.")

    # Generate an answer based on the found chunks
    answer = generate_answer_with_context(user_query, similar_chunks)

    return {"answer": answer}


# Run the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)

# PDF Chatbot with Qdrant and Cohere

This project is a chatbot application built using FastAPI, Cohere, and Qdrant. It allows users to upload multiple PDFs, process and chunk their contents, store the embeddings in Qdrant, and ask questions based on the PDF content. The chatbot retrieves the most relevant chunks of text from the uploaded PDFs and generates responses using Cohere's language model.

## Features

- **Upload Multiple PDFs**: Users can upload multiple PDFs, and the chatbot processes and chunks their content for efficient querying.
- **Embedding Storage**: The chatbot generates embeddings using Cohere's API and stores them in Qdrant for fast and efficient retrieval.
- **Question-Answering**: Users can ask questions, and the chatbot retrieves relevant information from the PDFs, generating an answer using Cohere.
- **Source Document Display**: The chatbot shows the source document and the relevant chunks for each answer, along with the similarity score.
- **Node.js Frontend**: A React-based frontend that allows users to upload PDFs and ask questions interactively.

## Technology Stack

- **Backend**: FastAPI
- **Embedding Generation**: Cohere API
- **Vector Database**: Qdrant
- **Frontend**: React with Axios for API requests
- **PDF Processing**: `pdfplumber`
- **Text Chunking**: LangChain's `RecursiveCharacterTextSplitter`
- **Deployment**: FastAPI server with Uvicorn

## Prerequisites

- Python 3.8+
- Node.js 14+
- Cohere API Key (for generating embeddings)
- Qdrant Cloud instance (or local setup for Qdrant)
- FastAPI, Uvicorn, and necessary Python packages

## Installation

### Backend (FastAPI)

1. **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd <repository-folder>
    ```

2. **Set up a Python virtual environment**:
    ```bash
    python -m venv env
    source env/bin/activate  # On Windows use `env\Scripts\activate`
    ```

3. **Install the required dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Set your environment variables**:
    Set the Cohere API Key and Qdrant API key in your environment or within the script.

5. **Run the FastAPI server**:
    ```bash
    uvicorn main:app --reload
    ```

    The server will start at `http://localhost:8000`.

### Frontend (React)

1. **Navigate to the frontend directory**:
    ```bash
    cd frontend
    ```

2. **Install dependencies**:
    ```bash
    npm install
    ```

3. **Start the frontend development server**:
    ```bash
    npm start
    ```

    The React app will be running on `http://localhost:3000`.

## Usage

### 1. Upload PDFs

- Select multiple PDFs from the frontend using the file upload section.
- Click on "Upload PDFs" to upload the documents to the backend.
- The backend processes the PDFs, chunks the content, and stores the embeddings in Qdrant.

### 2. Ask Questions

- Once PDFs are uploaded, you can enter your question in the input field and click "Send".
- The chatbot will retrieve the relevant chunks from the uploaded PDFs and generate an answer.
- The response will include the source document name and the similarity score, providing transparency about the answer's source.

### Example Query Flow:

1. Upload a set of research papers or documents.
2. Ask a question, e.g., "What is the role of AI in healthcare?"
3. The chatbot will retrieve the most relevant sections and generate a response based on the PDFs' content.

## Project Structure


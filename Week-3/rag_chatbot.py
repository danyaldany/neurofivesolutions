"""
Neurofive Solutions RAG Resume Chatbot
Chat with your resume using Google Gemini + FAISS vector search
"""

import os
import numpy as np
from dotenv import load_dotenv
from google import genai
from google.genai import types
import faiss

# Try PyPDF2, fallback to pypdf
try:
    import PyPDF2
    PDF_READER = "PyPDF2"
except ImportError:
    try:
        from pypdf import PdfReader
        PDF_READER = "pypdf"
    except ImportError:
        print("Error: Please install PyPDF2 or pypdf")
        print("   pip install PyPDF2")
        raise


# ============================================================
# 1. Load Environment
# ============================================================
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("Error: GEMINI_API_KEY not found in .env")
    exit(1)

client = genai.Client(api_key=GEMINI_API_KEY)
EMBEDDING_MODEL = "gemini-embedding-001"
CHAT_MODEL = "gemini-3.6-flash"


# ============================================================
# 2. PDF Text Extraction
# ============================================================
def extract_text_from_pdf(pdf_path):
    """Extract all text from a PDF file."""
    text = ""
    
    if PDF_READER == "PyPDF2":
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    else:
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    
    return text.strip()


# ============================================================
# 3. Text Chunking
# ============================================================
def chunk_text(text, chunk_size=800, overlap=100):
    """Split text into overlapping chunks for better retrieval."""
    chunks = []
    start = 0
    text_len = len(text)
    
    while start < text_len:
        end = min(start + chunk_size, text_len)
        # Try to break at a newline or space for cleaner chunks
        if end < text_len:
            # Look for a good break point within last 50 chars
            search_start = max(start + chunk_size - 50, start)
            newline_pos = text.rfind('\n', search_start, end)
            space_pos = text.rfind(' ', search_start, end)
            if newline_pos != -1:
                end = newline_pos + 1
            elif space_pos != -1:
                end = space_pos + 1
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        start = end - overlap if end - overlap > start else end
    
    return chunks


# ============================================================
# 4. Embeddings
# ============================================================
def get_embeddings(texts):
    """Get embeddings for a list of texts using Google Gemini."""
    if isinstance(texts, str):
        texts = [texts]
    
    # Batch in groups of 100 (API limit)
    all_embeddings = []
    batch_size = 100
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        response = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=batch
        )
        for emb in response.embeddings:
            all_embeddings.append(emb.values)
    
    return np.array(all_embeddings, dtype='float32')


# ============================================================
# 5. FAISS Vector Store
# ============================================================
class ResumeVectorStore:
    def __init__(self):
        self.index = None
        self.chunks = []
        self.dimension = None
    
    def build(self, chunks):
        """Build FAISS index from chunks."""
        self.chunks = chunks
        print(f"🔧 Creating embeddings for {len(chunks)} chunks...")
        
        embeddings = get_embeddings(chunks)
        self.dimension = embeddings.shape[1]
        
        # FAISS L2 index
        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(embeddings)
        
        print(f"✅ Vector store ready! {len(chunks)} chunks indexed.")
        return self
    
    def search(self, query, k=3):
        """Search for top-k relevant chunks."""
        query_embedding = get_embeddings([query])
        distances, indices = self.index.search(query_embedding, k)
        results = []
        for idx in indices[0]:
            if idx < len(self.chunks):
                results.append(self.chunks[idx])
        return results


# ============================================================
# 6. RAG QA Chain
# ============================================================
SYSTEM_PROMPT = (
    "You are a helpful assistant that answers questions STRICTLY based on the provided "
    "resume context. If the answer is not found in the context, say: "
    "'I don't see that information in your resume.' "
    "Do not make up or hallucinate any information. Be concise and accurate."
)


def answer_question(query, context_chunks):
    """Generate answer using retrieved context."""
    context = "\n\n---\n\n".join(context_chunks)
    
    prompt = f"""{SYSTEM_PROMPT}

RESUME CONTEXT:
{context}

USER QUESTION: {query}

INSTRUCTIONS:
- Answer ONLY using the resume context above
- If unsure, say you don't see that information
- Keep the answer clear and professional

ANSWER:"""
    
    response = client.models.generate_content(
        model=CHAT_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.2,
            max_output_tokens=1024,
        )
    )
    return response.text


# ============================================================
# 7. Main
# ============================================================
def main():
    print("\n" + "=" * 60)
    print("  🤖 Neurofive Solutions — RAG Resume Chatbot")
    print("=" * 60)
    
    # Get resume path
    pdf_path = input("\n📄 Enter path to your resume PDF: ").strip().strip('"')
    
    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        return
    
    # Extract and chunk
    print("\n📖 Reading resume...")
    text = extract_text_from_pdf(pdf_path)
    print(f"   Extracted {len(text)} characters")
    
    print("\n✂️ Chunking text...")
    chunks = chunk_text(text)
    print(f"   Created {len(chunks)} chunks")
    
    # Build vector store
    store = ResumeVectorStore()
    store.build(chunks)
    
    # Chat loop
    print("\n" + "-" * 60)
    print("  ✅ Resume loaded! Ask me anything about it.")
    print("  Type 'exit' to quit.")
    print("-" * 60 + "\n")
    
    while True:
        try:
            query = input("You: ").strip()
            if query.lower() in ('exit', 'quit', 'q'):
                print("\n👋 Goodbye!")
                break
            
            if not query:
                continue
            
            # Retrieve relevant chunks
            relevant = store.search(query, k=3)
            
            # Generate answer
            answer = answer_question(query, relevant)
            
            print(f"\n🤖 Assistant: {answer}\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    main()
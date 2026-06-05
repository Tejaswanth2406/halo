"""Initialize project and download models"""
import os
import argparse

def download_models():
    """Download required embedding and reranking models"""
    print("Downloading embedding models...")
    # sentence-transformers models
    from sentence_transformers import SentenceTransformer
    SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    
    print("Downloading reranker models...")
    # Cross-encoder models
    from sentence_transformers import CrossEncoder
    CrossEncoder("cross-encoder/ms-marco-MiniLM-L-12-v2")
    
    print("Models downloaded successfully!")

def setup_directories():
    """Create necessary directories"""
    dirs = [
        'data/raw',
        'data/processed',
        'models',
        'reports',
        'logs',
        'cache'
    ]
    
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        print(f"Created directory: {d}")

def main():
    parser = argparse.ArgumentParser(description="Initialize RAG system")
    parser.add_argument('--download-models', action='store_true', help='Download ML models')
    parser.add_argument('--setup-dirs', action='store_true', help='Setup directories')
    
    args = parser.parse_args()
    
    if args.setup_dirs or not args.download_models:
        setup_directories()
    
    if args.download_models:
        download_models()

if __name__ == "__main__":
    main()

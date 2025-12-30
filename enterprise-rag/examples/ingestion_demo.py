"""
Example: Complete ingestion workflow demonstration

This script demonstrates the full ingestion pipeline from raw data to vector index.
"""

import os
from pathlib import Path
from enterprise_rag.ingest.orchestrator import IngestionOrchestrator
from enterprise_rag.storage.metadata import SourceType


def main():
    """Run complete ingestion workflow example."""
    
    print("=" * 70)
    print("ENTERPRISE RAG INGESTION PLATFORM - DEMONSTRATION")
    print("=" * 70)
    print()
    
    # Initialize orchestrator
    print("1. Initializing Orchestrator...")
    orchestrator = IngestionOrchestrator(
        base_path="data",
        vectorstore_path="data/vectorstore",
        chunk_size=700,
        chunk_overlap=100,
        log_level="INFO"
    )
    print("✓ Orchestrator initialized")
    print()
    
    # Example 1: Ingest a markdown file
    print("2. Ingesting sample markdown file...")
    sample_file = Path("data/raw/aws_budget_policy.md")
    
    if sample_file.exists():
        record = orchestrator.ingest_file(
            str(sample_file),
            uploaded_by="demo_user"
        )
        print(f"✓ Ingested: {record.documents_ingested} documents")
        print(f"  Status: {record.status}")
        print(f"  Bytes: {record.bytes_processed}")
    else:
        print(f"⚠ Sample file not found: {sample_file}")
    print()
    
    # Example 2: Check ingestion history
    print("3. Checking ingestion history...")
    history = orchestrator.get_ingestion_history(limit=5)
    print(f"✓ Found {len(history)} recent ingestions:")
    for idx, record in enumerate(history, 1):
        print(f"  {idx}. {record['source_type']}: {record['status']} "
              f"({record['documents_ingested']} docs)")
    print()
    
    # Example 3: List batches by source
    print("4. Listing data batches...")
    for source_type in [SourceType.MARKDOWN, SourceType.TEXT, SourceType.PDF]:
        batches = orchestrator.get_source_batches(source_type)
        if batches:
            print(f"✓ {source_type.value}: {len(batches)} batches")
            for batch in batches[:2]:  # Show first 2
                print(f"  - {batch.get('batch_name', 'unknown')} "
                      f"({len(batch.get('documents', []))} docs)")
    print()
    
    # Example 4: Check vector index status
    print("5. Checking vector index status...")
    index_info = orchestrator.get_index_info()
    
    if index_info.get("exists"):
        print("✓ Vector index exists:")
        print(f"  Path: {index_info['path']}")
        print(f"  Version: {index_info['version']}")
        print(f"  Documents: {index_info['document_count']}")
        print(f"  Created: {index_info['created_at']}")
        print(f"  Model: {index_info['embedding_model']}")
    else:
        print("⚠ No vector index found")
        print("  Run: orchestrator.initialize_vector_index()")
    print()
    
    # Example 5: Initialize or update index (optional)
    print("6. Vector index operations...")
    
    if not index_info.get("exists"):
        response = input("  Initialize vector index now? (y/n): ")
        if response.lower() == 'y':
            print("  Initializing index (this may take a moment)...")
            try:
                result = orchestrator.initialize_vector_index()
                print(f"  ✓ Index created: {result['document_count']} documents")
            except Exception as e:
                print(f"  ✗ Failed: {e}")
        else:
            print("  Skipped initialization")
    else:
        print(f"  ✓ Index ready ({index_info['document_count']} documents)")
    print()
    
    # Summary
    print("=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("=" * 70)
    print()
    print("Next steps:")
    print("  1. Ingest your own data sources (Slack, Confluence, PDFs)")
    print("  2. Initialize or update the vector index")
    print("  3. Use the index with your RAG query pipeline")
    print()
    print("Documentation: enterprise-rag/INGESTION_PLATFORM.md")
    print()


if __name__ == "__main__":
    main()

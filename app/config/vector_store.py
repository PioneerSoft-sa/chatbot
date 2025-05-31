import os
import chromadb
from chromadb.config import Settings
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()

class VectorStore:
    def __init__(self):
        # Ensure the directory exists
        persist_dir = "./chroma_db"
        os.makedirs(persist_dir, exist_ok=True)
        
        embedding_fn = OpenAIEmbeddingFunction(
            api_key=os.getenv("OPENAI_API_KEY"),
            model_name="text-embedding-3-small"
        )

        # Initialize Chroma client with explicit persistence settings
        self.client = chromadb.PersistentClient(path=persist_dir)
        
        # Create collections
        self.schema_collection = self._get_or_create_collection("batch_schemas", embedding_fn)
    
    def _get_or_create_collection(self, name: str, embedding_fn=None):
        try:
            # First try to get existing collection
            collection = self.client.get_collection(name)
            print(f"Found existing collection: {name}")
            return collection
        except Exception as e:
            print(f"Creating new collection: {name}")
            return self.client.create_collection(name, embedding_function=embedding_fn)
    
    def add_schema_info(self, table_name: str, schema_info: str, description: str):
        """Add database schema information"""
        print(f"Adding schema info for: {table_name}")
        try:
            self.schema_collection.add(
                documents=[schema_info],
                metadatas=[{
                    "table": table_name,
                    "type": "schema",
                    "description": description
                }],
                ids=[f"schema_{table_name}"]
            )
            print(f"Successfully added schema for: {table_name}")
        except Exception as e:
            print(f"Error adding schema for {table_name}: {e}")

    def clear_collections(self):
        """Clear all data from the collection"""
        try:
            # Get all IDs and delete them
            all_data = self.schema_collection.get()
            if all_data['ids']:
                self.schema_collection.delete(ids=all_data['ids'])
                print("Cleared all collection data")
            else:
                print("Collection is already empty")
        except Exception as e:
            print(f"Error clearing collection: {e}")
    
    def get_all_schemas(self):
        """Get all stored schema data - useful for debugging"""
        try:
            return self.schema_collection.get()
        except Exception as e:
            print(f"Error getting schemas: {e}")
            return {"ids": [], "documents": [], "metadatas": []}
    
    def search_schema(self, query: str, n_results: int = 3) -> List[Dict]:
        """Search for relevant schema information"""
        try:
            results = self.schema_collection.query(
                query_texts=[query],
                n_results=n_results
            )
            return self._format_results(results)
        except Exception as e:
            print(f"Error searching schemas: {e}")
            return []

    def _format_results(self, results) -> List[Dict]:
        """Format Chroma results for easier use"""
        formatted = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                formatted.append({
                    'document': doc,
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'distance': results['distances'][0][i] if 'distances' in results and results['distances'] else None
                })
        return formatted

# Initialize vector store
vector_store = VectorStore()

# Populate with initial data
def populate_initial_data():
    """Add initial schema and example data"""
    
    # First, let's check if data already exists
    existing_data = vector_store.get_all_schemas()
    if existing_data['ids']:
        print(f"Found {len(existing_data['ids'])} existing schemas")
        print("Clearing existing data...")
        vector_store.clear_collections()
    
    print("Adding fresh schema data...")
    
    # Add schema information
    vector_store.add_schema_info(
        "employees",
        "Table: employees, Columns: id(int), name(string), email(string), department_id(FK), designation(string), date_joined(date)",
        "Main table storing employee information with department relationships"
    )

    vector_store.add_schema_info(
        "departments",
        "Table: departments, Columns: id(int), name(string), head_id(FK)",
        "Department master table with department head relationships"
    )

    vector_store.add_schema_info(
        "batches",
        "Table: batches, Columns: id(int), product_id(FK), batch_code(string), quantity(int), manufactured_date(date), expiry_date(date), created_by(FK)",
        "Manufacturing batch tracking with product and employee relationships"
    )
    
    vector_store.add_schema_info(
        "batch_tracking",
        "Table: batch_tracking, Columns: id(int), batch_id(FK), location(string), status(enum: Manufactured/In Transit/Delivered), timestamp(datetime), handled_by(FK)",
        "Real-time batch location and status tracking with employee handling info"
    )
    
    vector_store.add_schema_info(
        "products",
        "Table: products, Columns: id(int), name(string), category(string), unit_price(float)",
        "Product master data with pricing information"
    )
    
    # Verify the data was added
    print("\nVerifying added data...")
    all_data = vector_store.get_all_schemas()
    print(f"Total schemas stored: {len(all_data['ids'])}")
    for i, schema_id in enumerate(all_data['ids']):
        print(f"- {schema_id}: {all_data['metadatas'][i]['table']}")

# Call this once when setting up the application
if __name__ == "__main__":
    populate_initial_data()
    print("Vector store populated with initial data!")
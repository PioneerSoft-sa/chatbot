import os
import chromadb
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
            collection = self.client.get_collection(name, embedding_function=embedding_fn)
            print(f"Found existing collection: {name}")
            return collection
        except Exception as e:
            print(f"Creating new collection: {name}")
            return self.client.create_collection(name, embedding_function=embedding_fn)
    
    def add_schema_info(self, table_name: str, schema: str, schema_info: str):
        """Add database schema information"""
        print(f"Adding schema info for: {table_name}")
        try:
            self.schema_collection.add(
                documents=[schema_info],
                metadatas=[{
                    "table": table_name,
                    "type": "schema",
                    "schema": schema
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
        "Stores detailed employee records including personal information (name, email), role (designation), department association, and joining date. Used in multiple modules such as asset assignment, batch tracking, and maintenance reporting."
    )

    vector_store.add_schema_info(
        "departments",
        "Table: departments, Columns: id(int), name(string), head_id(FK)",
        "Contains organizational department information. Each department has a unique name and may optionally specify an employee as the department head. Used to group employees and allocate assets department-wise."
    )

    vector_store.add_schema_info(
        "batches",
        "Table: batches, Columns: id(int), product_id(FK), batch_code(string), quantity(int), manufactured_date(date), expiry_date(date), created_by(FK)",
        "Represents production batches for manufactured products. Each batch includes product reference, unique code, quantity, manufacture/expiry dates, and the employee who created it. Essential for production and inventory tracking."
    )
    
    vector_store.add_schema_info(
        "batch_tracking",
        "Table: batch_tracking, Columns: id(int), batch_id(FK), location(string), status(enum: MANUFACTURED/IN_TRANSIT/DELIVERED), timestamp(datetime), handled_by(FK)",
        "Captures real-time tracking of manufacturing batches across various locations. Stores current status and timestamps along with the employee responsible for handling the batch at that point."
    )
    
    vector_store.add_schema_info(
        "products",
        "Table: products, Columns: id(int), name(string), category(string), unit_price(float)",
        "Master reference table for all manufactured or stocked products. Includes product name, category classification, and unit pricing. Used to link batches and support inventory, pricing, and billing modules."
    )

    vector_store.add_schema_info(
        "assets",
        "Table: assets, Columns: id(int), asset_tag(string), name(string), category(string), location(string), purchase_date(date), warranty_until(date), assigned_to(FK), department_id(FK), status(enum: IN_USE/UNDER_MAINTENANCE/RETIRED)",
        "Comprehensive record of company-owned assets including laptops, machines, or equipment. Tracks purchase and warranty information, assigned employee, location, and current lifecycle status. Supports asset management and audit reporting."
    )

    vector_store.add_schema_info(
        "maintenance_logs",
        "Table: maintenance_logs, Columns: id(int), asset_id(FK), reported_by(FK), description(text), status(enum: REPORTED/IN_PROGRESS/RESOLVED), assigned_employee_id(FK), assigned_vendor_id(FK), created_at(datetime), resolved_date(date)",
        "Logs issues or service events reported against assets. Tracks the lifecycle of maintenance requests including who reported it, who handled it (internal employee or vendor), issue description, current status, and resolution date."
    )

    vector_store.add_schema_info(
        "vendors",
        "Table: vendors, Columns: id(int), name(string), contact_person(string), email(string), phone(string), address(string)",
        "Holds contact and company details for third-party service providers or vendors. Useful for managing outsourced maintenance and asset service partnerships."
    )

    vector_store.add_schema_info(
        "asset_vendor_link",
        "Table: asset_vendor_link, Columns: id(int), asset_id(FK), vendor_id(FK), service_type(string), last_service_date(date)",
        "Links assets to vendors that have performed service on them. Useful for tracking maintenance history by vendor, service type, and last known service date. Enables asset lifecycle analysis and vendor performance reporting."
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
import sqlalchemy
from sqlalchemy import create_engine, inspect, MetaData
import json
from typing import Dict, List, Any
import chromadb
from chromadb.config import Settings
import requests
import os
from google import genai
from dotenv import load_dotenv
load_dotenv()
import re

def extract_sql(raw):
    # Remove surrounding quotes if present
    raw = raw.strip('"').strip("'")
    
    # Remove ```sql and ``` markers
    raw = raw.replace("```sql", "").replace("```", "")
    
    # Remove anything after last semicolon (like stray ;)
    raw = re.split(r';\s*$', raw)[0] + ';'
    
    # Remove double semicolons if any
    raw = re.sub(r';+', ';', raw)

    # Clean whitespace
    raw = " ".join(raw.split())
    
    return raw

class SQLMetadataExtractor:
    """Extract SQL database metadata and prepare it for RAG"""
    
    def __init__(self, connection_string: str,userId: str):
        """
        Initialize with database connection string
        Examples:
        - PostgreSQL: "postgresql://user:password@localhost:5432/dbname"
        - MySQL: "mysql+pymysql://user:password@localhost:3306/dbname"
        - SQLite: "sqlite:///path/to/database.db"
        - SQL Server: "mssql+pyodbc://user:password@server/dbname?driver=ODBC+Driver+17+for+SQL+Server"
        """
        self.userId=userId
        self.engine = create_engine(connection_string)
        self.inspector = inspect(self.engine)
        self.metadata = MetaData()
        self.metadata.reflect(bind=self.engine)
        self.meta_chunks=self.generate_text_chunks(self.extract_all_metadata())
        self.examples_chunks=self.generate_examples()
        self.store_in_chromadb(self.meta_chunks,self.userId)
        self.store_in_chromadb1(self.examples_chunks)
        
        
    def extract_all_metadata(self) -> Dict[str, Any]:
        """Extract comprehensive database metadata"""
        db_metadata = {
            "database_name": self.engine.url.database,
            "dialect": self.engine.dialect.name,
            "tables": self._extract_table_metadata(),
            "views": self._extract_view_metadata(),
            "schemas": self.inspector.get_schema_names(),
        }
        
        # Add foreign key relationships
        db_metadata["relationships"] = self._extract_relationships()
        
        return db_metadata
    
    def _extract_table_metadata(self) -> List[Dict[str, Any]]:
        """Extract detailed metadata for all tables"""
        tables = []
        
        for table_name in self.inspector.get_table_names():
            table_info = {
                "name": table_name,
                "columns": [],
                "primary_keys": self.inspector.get_pk_constraint(table_name),
                "foreign_keys": self.inspector.get_foreign_keys(table_name),
                "indexes": self.inspector.get_indexes(table_name),
                "unique_constraints": self.inspector.get_unique_constraints(table_name),
                "check_constraints": self.inspector.get_check_constraints(table_name),
            }
            
            # Extract column details
            for col in self.inspector.get_columns(table_name):
                column_info = {
                    "name": col["name"],
                    "type": str(col["type"]),
                    "nullable": col["nullable"],
                    "default": str(col.get("default", None)),
                    "autoincrement": col.get("autoincrement", False),
                    "comment": col.get("comment", "")
                }
                table_info["columns"].append(column_info)
            
            # Get table comment if available
            try:
                table_info["comment"] = self.inspector.get_table_comment(table_name).get("text", "")
            except:
                table_info["comment"] = ""
                
            tables.append(table_info)
        
        return tables
    
    def _extract_view_metadata(self) -> List[Dict[str, Any]]:
        """Extract metadata for all views"""
        views = []
        
        for view_name in self.inspector.get_view_names():
            view_info = {
                "name": view_name,
                "columns": []
            }
            
            # Extract column details for views
            for col in self.inspector.get_columns(view_name):
                column_info = {
                    "name": col["name"],
                    "type": str(col["type"]),
                    "nullable": col["nullable"]
                }
                view_info["columns"].append(column_info)
            
            # Try to get view definition
            try:
                view_def = self.inspector.get_view_definition(view_name)
                view_info["definition"] = view_def
            except:
                view_info["definition"] = ""
                
            views.append(view_info)
        
        return views
    
    def _extract_relationships(self) -> List[Dict[str, Any]]:
        """Extract all foreign key relationships"""
        relationships = []
        
        for table_name in self.inspector.get_table_names():
            for fk in self.inspector.get_foreign_keys(table_name):
                relationship = {
                    "from_table": table_name,
                    "from_columns": fk["constrained_columns"],
                    "to_table": fk["referred_table"],
                    "to_columns": fk["referred_columns"],
                    "constraint_name": fk.get("name", "")
                }
                relationships.append(relationship)
        
        return relationships
    def generate_examples(self):
        with open("sql_train.json", "r") as f:
            data = json.load(f)
        chunks=[]
        for item in data:
            content = f"{item['title']}\n{item['description']}\n{item['sql']}"
          
            chunks.append(content)
        return chunks
    def generate_text_chunks(self, metadata: Dict[str, Any]) -> List[Dict[str, str]]:
        """Convert metadata into text chunks suitable for RAG embeddings"""
        chunks = []
        
        # Database overview chunk
        chunks.append({
            "text": f"Database: {metadata['database_name']} (Type: {metadata['dialect']}). "
                   f"Contains {len(metadata['tables'])} tables, {len(metadata['views'])} views, "
                   f"and {len(metadata['relationships'])} foreign key relationships.",
            "type": "database_overview",
            "metadata": {"database": metadata['database_name']}
        })
        
        # Table chunks
        for table in metadata["tables"]:
            # Table overview
            col_names = [col["name"] for col in table["columns"]]
            pk_cols = table["primary_keys"].get("constrained_columns", [])
            
            table_text = (
                f"Table '{table['name']}' has {len(table['columns'])} columns: {', '.join(col_names)}. "
                f"Primary key: {', '.join(pk_cols) if pk_cols else 'None'}. "
            )
            
            if table.get("comment"):
                table_text += f"Description: {table['comment']}. "
            
            chunks.append({
                "text": table_text,
                "type": "table_overview",
                "metadata": {"table": table["name"], "database": metadata['database_name']}
            })
            
            # Column details chunk
            for col in table["columns"]:
                col_text = (
                    f"Column '{col['name']}' in table '{table['name']}': "
                    f"Type: {col['type']}, Nullable: {col['nullable']}, "
                    f"Default: {col['default']}, Auto-increment: {col['autoincrement']}."
                )
                if col.get("comment"):
                    col_text += f" Description: {col['comment']}"
                
                chunks.append({
                    "text": col_text,
                    "type": "column_detail",
                    "metadata": {"table": table["name"], "column": col["name"], 
                               "database": metadata['database_name']}
                })
        
        # Relationship chunks
        for rel in metadata["relationships"]:
            rel_text = (
                f"Foreign key relationship: {rel['from_table']}.{', '.join(rel['from_columns'])} "
                f"references {rel['to_table']}.{', '.join(rel['to_columns'])}."
            )
            chunks.append({
                "text": rel_text,
                "type": "relationship",
                "metadata": {"from_table": rel["from_table"], "to_table": rel["to_table"],
                           "database": metadata['database_name']}
            })
        
        # View chunks
        for view in metadata["views"]:
            view_text = f"View '{view['name']}' with columns: {', '.join([c['name'] for c in view['columns']])}."
            if view.get("definition"):
                view_text += f" Definition: {view['definition']}"
            
            chunks.append({
                "text": view_text,
                "type": "view",
                "metadata": {"view": view["name"], "database": metadata['database_name']}
            })
        
        return chunks
    def store_in_chromadb1(self,chunks,collection_name = "sql_examples",persist_directory= "./chroma_db"):
        client= chromadb.PersistentClient(path=persist_directory)
        try:
            collection = client.get_collection(name=collection_name)
            client.delete_collection(name=collection_name)
        except:
            pass
        
        collection = client.create_collection(
            name=collection_name,
            metadata={"description": "Sql query examples for correct sy"}
        )
        
        # Prepare data for insertion
        
        
        
        # Add to collection
        ids = [f"chunk_{i}" for i in range(len(chunks))]
        collection.add(
            ids=ids,
            documents=chunks,  
        )
        
        
        print(f" Stored {len(chunks)} metadata chunks in ChromaDB collection '{collection_name}'")
        return collection


    def store_in_chromadb(self, chunks: List[Dict[str, str]], 
                         collection_name: str = "sql_metadata",
                         persist_directory: str = "./chroma_db"):
        """Store metadata chunks in ChromaDB for RAG"""
        
        # Initialize ChromaDB client
        client = chromadb.PersistentClient(path=persist_directory)
        
        # Create or get collection
        try:
            collection = client.get_collection(name=collection_name)
            client.delete_collection(name=collection_name)
        except:
            pass
        
        collection = client.create_collection(
            name=collection_name,
            metadata={"description": "SQL database metadata for RAG"}
        )
        
        # Prepare data for insertion
        texts = [chunk["text"] for chunk in chunks]
        metadatas = [chunk["metadata"] for chunk in chunks]
        ids = [f"chunk_{i}" for i in range(len(chunks))]
        
        # Add to collection
        collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f" Stored {len(chunks)} metadata chunks in ChromaDB collection '{collection_name}'")
        return collection
    def get_examples(self,type:str="sql_train"):
        
        pass
    def query_metadata(self, query: str, collection_name: str = "sql_metadata",
                      persist_directory: str = "./chroma_db", n_results: int = 5):
       
        client = chromadb.PersistentClient(path=persist_directory)
        collection = client.get_collection(name=collection_name)
        
        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        return results
    def query_metadata1(self, query: str, collection_name: str = "sql_examples",
                      persist_directory: str = "./chroma_db", n_results: int = 5):
       
        client = chromadb.PersistentClient(path=persist_directory)
        collection = client.get_collection(name=collection_name)
        
        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        return results
    def generate_response(self, query: str) -> str:
       
       context= self.query_metadata(query=query,collection_name=self.userId)
       example=self.query_metadata1(query=query)
       """Generate response using Gemini with context"""
       client = genai.Client(api_key=os.getenv("API_KEY"))
       prompt = f"""Based on the following context, answer the question.

Context:
{context}

Question: sql query for {query}
Example:{example}
Answer:"""
       response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
)
        
        
       
        
       return response.text
   



# Example usage
def createString(type,link,password,username,database):
    type=type.strip()
    type=type.lower()
    if  type=="mysql":
        return f"mysql+pymysql://{username}:{password}@{link}/{database}"
    
    return "mysql+pymysql://root:root@localhost:3308/llm"
if __name__ == "__main__":
  
   
    

    extractor = SQLMetadataExtractor(createString("","","","",""),"jifsef")

    metadata = extractor.extract_all_metadata()
    with open("database_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2, default=str)
    with open("sql_train.json", "r") as f:
        data = json.load(f)
    chunks1 = extractor.generate_text_chunks(metadata)
    chunks2 = extractor.generate_examples(data)
    collection1 = extractor.store_in_chromadb(chunks1)
    collection2 = extractor.store_in_chromadb1(chunks2)
    print("\nExample query:")
   

    # results1 = extractor.query_metadata(query)
    # examples = extractor.query_metadata("provide example sql queries")
    # response= extractor.generate_response(query,results1,examples)
    # print(f"Query: {query}")
    # print(f"Results: {results1['documents'][0][:3]}") 
    # print(f"response: {extract_sql(response)}")

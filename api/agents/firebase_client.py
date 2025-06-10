#from google.adk.sessions import MemoryService
from google.cloud import firestore
from typing import Dict
import asyncio
import os
import firebase_admin
from firebase_admin import credentials, firestore as admin_firestore
from google.cloud.firestore_v1 import ArrayUnion
import datetime
from google.cloud import firestore
from google.adk.sessions.session import Session
from google.adk.sessions import BaseSessionService
from typing import List, Optional
from vertexai.language_models import TextEmbeddingModel
from google import genai
from google.genai import types


_table_users = 'vendo_users'
_table_organizations = 'vendo_organizations'
_table_ai_memory = 'vendo_ai_memory'

class FirebaseClient:
    def __init__(self, firebase_db_url):
        self._client = firestore.client(firebase_admin.initialize_app(options={
            'databaseURL': firebase_db_url
        }))



class FirestoreSessionService(BaseSessionService):
    def __init__(self, collection_name="vendo_ai_memory"):
        super().__init__()
        # Load service_key.json from the project root
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        service_key_path = os.path.join(project_root, 'service_key.json')
        self.db = admin_firestore.client(firebase_admin.initialize_app(options={
            'credential': firebase_admin.credentials.Certificate(service_key_path)
        }))
        self.collection = self.db.collection(collection_name)

    def create_session(self, app_name: str, connection_id: str, session_id: str = None) -> Session:
        session_data = {
            "app_name": app_name,
            "connection_id": connection_id,
        }

        if connection_id is None:
            session_ref = self.collection.document()
            session_id = session_ref.id
        else:
            session_ref = self.collection.document(connection_id)

        session_ref.set(session_data, merge=True)

        # Create Session with required fields
        return Session(
            id=session_id,  # Required field
            app_name=app_name,
            user_id=connection_id
        )

    def get_session(self, connection_id: str, **kwargs) -> Optional[Session]:
        doc = self.collection.document(connection_id).get()
        if doc.exists:
            data = doc.to_dict()
            return Session(
                id=connection_id,
                app_name=data.get("app_name", ""),
                user_id=data.get("connection_id", "")
            )
        return None

    def list_sessions(self, app_name: str, connection_id: str) -> List[Session]:
        sessions = []
        docs = self.collection.where("app_name", "==", app_name).where("connection_id", "==", connection_id).stream()
        for doc in docs:
            data = doc.to_dict()
            sessions.append(Session(
                id=doc.id,
                app_name=data.get("app_name", ""),
                user_id=data.get("connection_id", "")
            ))
        return sessions

    def delete_session(self, connection_id: str) -> None:
        self.collection.document(connection_id).delete()

    def list_events(self, connection_id: str) -> List[dict]:
        doc = self.collection.document(connection_id).get()
        if doc.exists:
            data = doc.to_dict()
            return data.get("events", [])
        return []

    def get_memory(self, connection_id: str):
        doc = self.collection.document(connection_id).get()  # Use session.id instead of session_id
        if doc.exists:
            memory_dict = doc.to_dict().get("memory", {})
            return memory_dict
        return {}

    def save_memory(self, connection_id: str, memory):
        self.collection.document(connection_id).update({  # Use session.id instead of session_id
            "memory": memory
        })

    def append_message(self, connection_id: str, role: str, content: str, message_type: str = "messages", include_embedding: bool = False, title: str = None, author: str = None, created_at: str = None, updated_at: str = None):

        if include_embedding:
            embedding = embed_text(content)
            embedding_list = embedding.tolist() if hasattr(embedding, 'tolist') else list(embedding)
        else:
            embedding_list = None
        
        message = {
            "role": role,
            "content": content,
            "title": title,
            "author": author,
            "created_at": created_at,
            "updated_at": updated_at,
            "timestamp": datetime.datetime.utcnow(),
            "embedding": embedding_list
        }
        self.collection.document(connection_id).set({
            message_type: firestore.ArrayUnion([message])
        }, merge=True)

    def store_chat_message(
        self, 
        connection_id: str, 
        session_id: str, 
        role: str,
        content: str,
        include_embedding: bool = False
    ) -> None:
        """
        Store a chat message directly in chat_history
        """
        if include_embedding:
            embedding = embed_text(content)
            embedding_list = embedding.tolist() if hasattr(embedding, 'tolist') else list(embedding)
        else:
            embedding_list = None

        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.datetime.utcnow(),
            "embedding": embedding_list
        }

        # Get the chat_history document
        chat_ref = self.collection.document(connection_id).collection("chat_history").document("messages")
        
        # Get current messages or initialize empty dict
        doc = chat_ref.get()
        current_data = doc.to_dict() if doc.exists else {}
        
        # Get current session messages or initialize empty list
        session_messages = current_data.get(session_id, [])
        
        # Append new message
        session_messages.append(message)
        
        # Update the document with the new message
        chat_ref.set({
            session_id: session_messages
        }, merge=True)

    def get_chat_messages(
        self, 
        connection_id: str, 
        session_id: str,
        limit: int = None
    ) -> List[dict]:
        """
        Retrieve chat messages for a specific session
        """
        print(f"[DEBUG] Getting chat messages for connection_id: {connection_id}, session_id: {session_id}", flush=True)
        chat_ref = self.collection.document(connection_id)\
            .collection("chat_history")\
            .document("messages")
        
        doc = chat_ref.get()
        if not doc.exists:
            return []
            
        data = doc.to_dict()
        messages = data.get(session_id, [])
        
        # Sort by timestamp
        messages.sort(key=lambda x: x['timestamp'])
        
        if limit:
            messages = messages[:limit]
            
        return messages

    
    def get_general_context(self, connection_id: str, message_type: str = "general_context"):
        doc = self.collection.document(connection_id).get()
        if not doc.exists:
            return []

        messages = doc.to_dict().get(message_type, [])
        result = []

        for msg in messages:
            if "embedding" in msg and "content" in msg:
                result.append({
                    "content": msg["content"],
                    "embedding": msg["embedding"]
                })
        
        return result
    
    def get_mixpanel_details(self, organization_id: str, app_id: str):
        doc = self.db.collection(_table_organizations).document(organization_id).get()
        if not doc.exists:
            return []
        
        return doc.to_dict().get("apps", []).get(app_id)
    
    def get_all_general_context(self, connection_id: str, message_type: str = "general_context"):
        doc = self.collection.document(connection_id).get()
        if not doc.exists:
            return []

        messages = doc.to_dict().get(message_type, [])
        result = []

        for index, msg in enumerate(messages):
            if "content" in msg:
                # Return full document object with all metadata
                result.append({
                    "id": f"{connection_id}_{index}",
                    "title": msg.get("title", ""),
                    "content": msg["content"],
                    "author": msg.get("author", ""),
                    "created_at": msg.get("created_at", ""),
                    "updated_at": msg.get("updated_at", ""),
                    "timestamp": msg.get("timestamp"),
                    "index": index
                })
        
        return result

    def get_history(self, connection_id):
        result = self._client.collection(_table_ai_memory).document(connection_id).get('general_context')
        if result.exists:
            return result.to_dict()
        return None
    
    def update_general_context_by_index(self, connection_id: str, index: int, new_content: str, message_type: str = "general_context", new_title: str = None):
        """Update a specific requirement by index"""
        doc_ref = self.collection.document(connection_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return False
            
        data = doc.to_dict()
        general_context = data.get(message_type, [])
        
        # Check if index is valid
        if index < 0 or index >= len(general_context):
            return False
        
        # Update the requirement at the specified index
        general_context[index]["content"] = new_content
        general_context[index]["timestamp"] = datetime.datetime.utcnow()
        general_context[index]["updated_at"] = datetime.datetime.utcnow().isoformat()
        
        # Update title if provided
        if new_title is not None:
            general_context[index]["title"] = new_title
        
        # Update embedding for new content
        if "embedding" in general_context[index]:
            embedding = embed_text(new_content)
            general_context[index]["embedding"] = embedding.tolist() if hasattr(embedding, 'tolist') else list(embedding)
        
        doc_ref.update({message_type: general_context})
        return True
    
    def delete_general_context_by_index(self, connection_id: str, index: int, message_type: str = "general_context"):
        """Delete a specific requirement by index"""
        doc_ref = self.collection.document(connection_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return False
            
        data = doc.to_dict()
        general_context = data.get(message_type, [])
        
        # Check if index is valid
        if index < 0 or index >= len(general_context):
            return False
        
        # Remove the requirement at the specified index
        general_context.pop(index)
        
        doc_ref.update({message_type: general_context})
        return True

    def get_mixpanel_dataset_id(self, connection_id: str):
        """Get the mixpanel_dataset_id from the user object"""
        try:
            user_doc = self.collection.document(connection_id).get()
            if user_doc.exists:
                user_data = user_doc.to_dict()
                dataset_id = user_data.get("dataset_id")
                if dataset_id:
                    print(f"[DEBUG] User {connection_id} mixpanel_dataset_id: {dataset_id}", flush=True)
                    return dataset_id
                else:
                    print(f"[DEBUG] No dataset_id found for user {connection_id}", flush=True)
                    return None
            else:
                print(f"[DEBUG] User {connection_id} not found in {_table_ai_memory}", flush=True)
                return None
        except Exception as e:
            print(f"[ERROR] Failed to get mixpanel_dataset_id for user {connection_id}: {str(e)}", flush=True)
            return None
    

    def get_business_context_from_firebase(self, connection_id: str = "001"):
        """
        Get client information from Firebase business_context object.
        
        Args:
            connection_id (str): The user ID to fetch business context for
            
        Returns:
            Optional[Dict[str, Any]]: Client information from Firebase or None if not found
        """
        try:
            
            
            # Get user document
            user_doc = self.collection.document(connection_id).get()
            
            if user_doc.exists:
                user_data = user_doc.to_dict()
                business_context = user_data.get("business_context")
                print(f"[DEBUG] Business context: {business_context}", flush=True)
                
                if business_context and isinstance(business_context, dict):
                    print(f"[DEBUG] Successfully loaded business_context for user {connection_id}", flush=True)
                    return business_context
                else:
                    print(f"[DEBUG] No business_context found for user {connection_id}", flush=True)
                    return None
            else:
                print(f"[DEBUG] User {connection_id} not found in Firebase", flush=True)
                return None
                
        except Exception as e:
            print(f"[ERROR] Failed to get business_context from Firebase for user {connection_id}: {str(e)}", flush=True)
            return None

    def get_connection_info(self, connection_id: str = "001"):
        """
        Get connection information from Firebase connection_info object.
        
        Args:
            connection_id (str): The user ID to fetch connection information for
        
        Returns:
            Optional[Dict[str, Any]]: Connection information from Firebase or None if not found
        """
        try:
            # Get user document
            connection_info = self.collection.document(connection_id).get()

            if connection_info.exists:
                connection_info = connection_info.to_dict()
                return connection_info
            else:
                print(f"[DEBUG] Connection info not found for user {connection_id}", flush=True)
                return None
        except Exception as e:
            print(f"[ERROR] Failed to get connection info from Firebase for user {connection_id}: {str(e)}", flush=True)
            return None
        
def embed_text(content: str) -> List[float]:
    client = genai.Client()

    result = client.models.embed_content(
            model="gemini-embedding-exp-03-07",
            contents=content,
            config=types.EmbedContentConfig(task_type="SEMANTIC_SIMILARITY")
    )
    # Get the values and ensure they're in the right format
    embedding_values = result.embeddings[0].values
    # Convert to a regular list to ensure Firestore compatibility
    return list(embedding_values)

#session_service = FirestoreSessionService()
#session_service.append_message("001", "user", "My name is Suraj", message_type="requirements", include_embedding=True)


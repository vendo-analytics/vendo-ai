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
        self.db = admin_firestore.client(firebase_admin.initialize_app(options={
            'databaseURL': os.getenv("FIREBASE_DB_URL")
        }))
        self.collection = self.db.collection(collection_name)

    def create_session(self, app_name: str, user_id: str, session_id: str = None) -> Session:
        session_data = {
            "app_name": app_name,
            "user_id": user_id,
        }

        if session_id is None:
            session_ref = self.collection.document()
            session_id = session_ref.id
        else:
            session_ref = self.collection.document(session_id)

        session_ref.set(session_data, merge=True)

        # Create Session with required fields
        return Session(
            id=session_id,  # Required field
            app_name=app_name,
            user_id=user_id
        )

    def get_session(self, session_id: str, **kwargs) -> Optional[Session]:
        doc = self.collection.document(session_id).get()
        if doc.exists:
            data = doc.to_dict()
            return Session(
                id=session_id,
                app_name=data.get("app_name", ""),
                user_id=data.get("user_id", "")
            )
        return None

    def list_sessions(self, app_name: str, user_id: str) -> List[Session]:
        sessions = []
        docs = self.collection.where("app_name", "==", app_name).where("user_id", "==", user_id).stream()
        for doc in docs:
            data = doc.to_dict()
            sessions.append(Session(
                id=doc.id,
                app_name=data.get("app_name", ""),
                user_id=data.get("user_id", "")
            ))
        return sessions

    def delete_session(self, session_id: str) -> None:
        self.collection.document(session_id).delete()

    def list_events(self, session_id: str) -> List[dict]:
        doc = self.collection.document(session_id).get()
        if doc.exists:
            data = doc.to_dict()
            return data.get("events", [])
        return []

    def get_memory(self, session: Session):
        doc = self.collection.document(session.id).get()  # Use session.id instead of session_id
        if doc.exists:
            memory_dict = doc.to_dict().get("memory", {})
            return memory_dict
        return {}

    def save_memory(self, session: Session, memory):
        self.collection.document(session.id).update({  # Use session.id instead of session_id
            "memory": memory
        })

    def append_message(self, user_id: str, role: str, content: str, message_type: str = "messages", include_embedding: bool = False):

        if include_embedding:
            embedding = embed_text(content)
            # Convert embedding to a list of floats that Firestore can store
            embedding_list = embedding.tolist() if hasattr(embedding, 'tolist') else list(embedding)
        else:
            embedding_list = None
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.datetime.utcnow(),
            "embedding": embedding_list  # Store as regular list
        }
        # Use user_id directly as the document ID
        self.collection.document(user_id).set({
            message_type: firestore.ArrayUnion([message])
        }, merge=True)

    

    def get_messages(self, user_id: str):
        # Use user_id directly as the document ID
        doc = self.collection.document(user_id).get()
        if doc.exists:
            return doc.to_dict().get("messages", [])
        return []
    
    def get_all_messages(self, user_id: str, message_type: str = "requirements"):
        doc = self.collection.document(user_id).get()
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
    
    def get_all_requirements(self, user_id: str, message_type: str = "requirements"):
        doc = self.collection.document(user_id).get()
        if not doc.exists:
            return []

        messages = doc.to_dict().get(message_type, [])
        result = []

        for msg in messages:
            if "content" in msg:
                result.append(msg["content"])
        
        return result

    def get_history(self, user_id):
        result = self._client.collection(_table_ai_memory).document(user_id).get('requirements')
        if result.exists:
            return result.to_dict()
        return None
    
    def update_requirement_by_index(self, user_id: str, index: int, new_content: str, message_type: str = "requirements"):
        """Update a specific requirement by index"""
        doc_ref = self.collection.document(user_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return False
            
        data = doc.to_dict()
        requirements = data.get(message_type, [])
        
        # Check if index is valid
        if index < 0 or index >= len(requirements):
            return False
        
        # Update the requirement at the specified index
        requirements[index]["content"] = new_content
        requirements[index]["timestamp"] = datetime.datetime.utcnow()
        
        # Update embedding for new content
        if "embedding" in requirements[index]:
            embedding = embed_text(new_content)
            requirements[index]["embedding"] = embedding.tolist() if hasattr(embedding, 'tolist') else list(embedding)
        
        doc_ref.update({message_type: requirements})
        return True
    
    def delete_requirement_by_index(self, user_id: str, index: int, message_type: str = "requirements"):
        """Delete a specific requirement by index"""
        doc_ref = self.collection.document(user_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return False
            
        data = doc.to_dict()
        requirements = data.get(message_type, [])
        
        # Check if index is valid
        if index < 0 or index >= len(requirements):
            return False
        
        # Remove the requirement at the specified index
        requirements.pop(index)
        
        doc_ref.update({message_type: requirements})
        return True

    def get_user_mixpanel_dataset_id(self, user_id: str):
        """Get the mixpanel_dataset_id from the user object"""
        try:
            user_doc = self.collection.document(user_id).get()
            if user_doc.exists:
                user_data = user_doc.to_dict()
                dataset_id = user_data.get("dataset_id")
                if dataset_id:
                    print(f"[DEBUG] User {user_id} mixpanel_dataset_id: {dataset_id}", flush=True)
                    return dataset_id
                else:
                    print(f"[DEBUG] No dataset_id found for user {user_id}", flush=True)
                    return None
            else:
                print(f"[DEBUG] User {user_id} not found in {_table_ai_memory}", flush=True)
                return None
        except Exception as e:
            print(f"[ERROR] Failed to get mixpanel_dataset_id for user {user_id}: {str(e)}", flush=True)
            return None
    

    def get_client_info_from_firebase(self, user_id: str = "001"):
        """
        Get client information from Firebase business_context object.
        
        Args:
            user_id (str): The user ID to fetch business context for
            
        Returns:
            Optional[Dict[str, Any]]: Client information from Firebase or None if not found
        """
        try:
            
            
            # Get user document
            user_doc = self.collection.document(user_id).get()
            
            if user_doc.exists:
                user_data = user_doc.to_dict()
                business_context = user_data.get("business_context")
                print(f"[DEBUG] Business context: {business_context}", flush=True)
                
                if business_context and isinstance(business_context, dict):
                    print(f"[DEBUG] Successfully loaded business_context for user {user_id}", flush=True)
                    return business_context
                else:
                    print(f"[DEBUG] No business_context found for user {user_id}", flush=True)
                    return None
            else:
                print(f"[DEBUG] User {user_id} not found in Firebase", flush=True)
                return None
                
        except Exception as e:
            print(f"[ERROR] Failed to get business_context from Firebase for user {user_id}: {str(e)}", flush=True)
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


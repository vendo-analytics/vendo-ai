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

    def get_session(self, session_id: str) -> Optional[Session]:
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


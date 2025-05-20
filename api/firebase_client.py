#from google.adk.sessions import MemoryService
from google.cloud import firestore
from typing import Dict
import asyncio
import os
import firebase_admin
from firebase_admin import credentials, firestore as admin_firestore
from google.cloud.firestore_v1 import ArrayUnion
import datetime



class FirestoreMemoryService():
    def __init__(self, collection_name="vendo_ai_memory"):
        self.client = firestore.client(firebase_admin.initialize_app(options={
            'databaseURL': os.getenv("FIREBASE_DB_URL")
        }))
        self.collection = self.client.collection(collection_name)


    def _doc_ref(self, app_name: str, user_id: str, session_id: str):
        return self.collection.document(f"{app_name}:{user_id}:{session_id}")

    async def get_memory(self, app_name: str, user_id: str, session_id: str) -> Dict:
        doc = await asyncio.to_thread(self._doc_ref(app_name, user_id, session_id).get)
        if doc.exists:
            return doc.to_dict()
        return {}

    async def set_memory(self, app_name: str, user_id: str, session_id: str, memory: Dict) -> None:
        await asyncio.to_thread(self._doc_ref(app_name, user_id, session_id).set, memory)

# --- Custom Firestore Session Service ---
from google.cloud import firestore
from google.adk.sessions.session import Session
from google.adk.sessions import BaseSessionService
from typing import List, Optional


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

    def append_message(self, session_id: str, role: str, content: str):
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.datetime.utcnow()
        }
        self.collection.document(session_id).set({
            "messages": firestore.ArrayUnion([message])
        }, merge=True)

    def get_messages(self, session_id: str):
        doc = self.collection.document(session_id).get()
        if doc.exists:
            return doc.to_dict().get("messages", [])
        return []
from google.adk.sessions import MemoryService
from google.cloud import firestore
from typing import Dict
import asyncio
import os
import firebase_admin

class FirestoreMemoryService(MemoryService):
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

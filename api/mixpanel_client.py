import requests
import base64
import pandas as pd
from datetime import datetime
import pytz
import json
import logging
from .firestore_instance import firestore_session_service

logger = logging.getLogger(__name__)
lexicon_api_url = 'https://mixpanel.com/api/app/projects'
lexicon_api_url_eu = 'https://eu.mixpanel.com/api/app/projects'
lexicon_api_url_in = 'https://in.mixpanel.com/api/app/projects'

class MixpanelClient:
    def __init__(self, connection_id):
        organization_id = firestore_session_service.get_connection_info(connection_id).get("organization_id")
        source_id = firestore_session_service.get_connection_info(connection_id).get("source_id")
        mixpanel_details = firestore_session_service.get_mixpanel_details(organization_id, source_id)
        self._project_id = mixpanel_details.get("project_id")
        self._username = mixpanel_details.get("service_account_user_name")
        self._secret = mixpanel_details.get("service_account_secret")  
        self.lexicon_api_url = (
                    lexicon_api_url if mixpanel_details.get("region") in ['standard', 'US']
                    else lexicon_api_url_in if mixpanel_details.get("region") == 'IN'
                    else lexicon_api_url_eu
                )

    def get_mixpanel_annotations_data(self):
        """
        Get annotations data from Mixpanel project for a specific date range.
        Args:
            from_date (str): Start date in format "YYYY-MM-DD"
            to_date (str): End date in format "YYYY-MM-DD"
        Returns:
            pd.DataFrame: DataFrame containing annotations data
        """
        project_id = self._project_id
        username = self._username
        secret = self._secret

        auth_header = base64.b64encode(f"{username}:{secret}".encode('ascii')).decode('ascii')
        url = f"{self.lexicon_api_url}/{project_id}/annotations"

        headers = {
            "accept": "application/json",
            "authorization": f"Basic {auth_header}"
        }
        response = requests.get(url, headers=headers)
        print(response)
        if response.status_code == 200:
            try:
                annotations_data = response.json()
                if annotations_data and annotations_data.get('status') == 'ok' and 'results' in annotations_data:
                    results = annotations_data['results']
                    if results and len(results) > 0:
                        annotations_df = pd.json_normalize(results)
                        annotations_df.columns = annotations_df.columns.str.replace('$', '', regex=False)
                        annotations_df.columns = [col.replace('.', '_') for col in annotations_df.columns]
                        annotations_df['extracted_at'] = datetime.now().astimezone(pytz.utc)
                        return annotations_df
                    else:
                        return pd.DataFrame({
                            'extracted_at': [datetime.now().astimezone(pytz.utc)],
                            'status': ['no_results']
                        })
                else:
                    return pd.DataFrame({
                        'extracted_at': [datetime.now().astimezone(pytz.utc)],
                        'status': ['no_data']
                    })
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON response: {response.text}")
                return pd.DataFrame({
                    'extracted_at': [datetime.now().astimezone(pytz.utc)],
                    'status': ['json_decode_error']
                })
        else:
            logger.error(f"Error getting annotations: {response.status_code} - {response.text}")
            return pd.DataFrame({
                'extracted_at': [datetime.now().astimezone(pytz.utc)],
                'status': [f'error_{response.status_code}']
            })

    def update_annotation(self, annotation_id, data):
        """
        Update an annotation in Mixpanel.
        Args:
            annotation_id (str): The annotation's ID.
            data (dict): The fields to update (e.g., {"description": "...", "date": "..."}).
        Returns:
            dict: The API response.
        """
        url = f"{self.lexicon_api_url}/{self._project_id}/annotations/{annotation_id}"
        auth_header = base64.b64encode(f"{self._username}:{self._secret}".encode('ascii')).decode('ascii')
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Basic {auth_header}"
        }
        response = requests.patch(url, headers=headers, data=json.dumps(data))
        if response.status_code in (200, 204):
            return {"success": True}
        else:
            logger.error(f"Failed to update annotation: {response.status_code} - {response.text}")
            return {"success": False, "error": response.text, "status_code": response.status_code}

    def delete_annotation(self, annotation_id):
        """
        Delete an annotation in Mixpanel.
        Args:
            annotation_id (str): The annotation's ID.
        Returns:
            dict: The API response.
        """
        url = f"{self.lexicon_api_url}/{self._project_id}/annotations/{annotation_id}"
        auth_header = base64.b64encode(f"{self._username}:{self._secret}".encode('ascii')).decode('ascii')
        headers = {
            "accept": "application/json",
            "authorization": f"Basic {auth_header}"
        }
        response = requests.delete(url, headers=headers)
        if response.status_code in (200, 204):
            return {"success": True}
        else:
            logger.error(f"Failed to delete annotation: {response.status_code} - {response.text}")
            return {"success": False, "error": response.text, "status_code": response.status_code}

    def create_annotation(self, description, date):
        """
        Create a new annotation in Mixpanel.
        Args:
            description (str): The annotation text.
            date (str): Date in 'YYYY-MM-DD HH:mm:ss' format.
        Returns:
            dict: The API response.
        """
        url = f"{self.lexicon_api_url}/{self._project_id}/annotations"
        auth_header = base64.b64encode(f"{self._username}:{self._secret}".encode('ascii')).decode('ascii')
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Basic {auth_header}"
        }
        payload = {"description": description, "date": date}
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code in (200, 201):
            return {"success": True, "data": response.json()}
        else:
            logger.error(f"Failed to create annotation: {response.status_code} - {response.text}")
            return {"success": False, "error": response.text, "status_code": response.status_code} 
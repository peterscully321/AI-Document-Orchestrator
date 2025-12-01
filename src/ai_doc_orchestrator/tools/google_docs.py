"""Google Docs API tool."""

import os
from typing import Any, Dict, Optional

try:
    from google.oauth2.credentials import Credentials
    from google.oauth2.service_account import Credentials as ServiceAccountCredentials
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    build = None
    HttpError = None


class GoogleDocsTool:
    """Tool for creating and updating Google Docs."""

    def __init__(
        self,
        credentials_path: Optional[str] = None,
        credentials: Optional[Any] = None,
    ):
        """Initialize the Google Docs tool.

        Args:
            credentials_path: Path to service account JSON file
            credentials: Pre-configured credentials object
        """
        if build is None:
            raise ImportError(
                "google-api-python-client is required. "
                "Install with: pip install google-api-python-client google-auth"
            )

        if credentials:
            self.credentials = credentials
        elif credentials_path:
            self.credentials = ServiceAccountCredentials.from_service_account_file(
                credentials_path,
                scopes=["https://www.googleapis.com/auth/documents"],
            )
        else:
            # Try to get from environment
            creds_path = os.getenv("GOOGLE_CREDENTIALS_PATH")
            if creds_path:
                self.credentials = ServiceAccountCredentials.from_service_account_file(
                    creds_path,
                    scopes=["https://www.googleapis.com/auth/documents"],
                )
            else:
                raise ValueError(
                    "Either credentials_path, credentials, or GOOGLE_CREDENTIALS_PATH "
                    "environment variable must be provided"
                )

        self.service = build("docs", "v1", credentials=self.credentials)

    def create_document(self, title: str, content: str) -> Dict[str, Any]:
        """Create a new Google Doc.

        Args:
            title: Document title
            content: Document content

        Returns:
            Dictionary with document ID and URL
        """
        try:
            # Create the document
            doc = self.service.documents().create(body={"title": title}).execute()
            document_id = doc.get("documentId")

            # Insert content
            requests = [
                {
                    "insertText": {
                        "location": {"index": 1},
                        "text": content,
                    }
                }
            ]
            self.service.documents().batchUpdate(
                documentId=document_id, body={"requests": requests}
            ).execute()

            return {
                "document_id": document_id,
                "url": f"https://docs.google.com/document/d/{document_id}",
                "title": title,
            }
        except HttpError as e:
            raise RuntimeError(f"Failed to create Google Doc: {e}")

    def update_document(self, document_id: str, content: str) -> Dict[str, Any]:
        """Update an existing Google Doc.

        Args:
            document_id: Google Docs document ID
            content: New content to insert

        Returns:
            Dictionary with update status
        """
        try:
            # Get current document to find end index
            doc = self.service.documents().get(documentId=document_id).execute()
            end_index = doc.get("body", {}).get("content", [{}])[-1].get("endIndex", 1)

            # Clear existing content and insert new
            requests = [
                {
                    "deleteContentRange": {
                        "range": {
                            "startIndex": 1,
                            "endIndex": end_index - 1,
                        }
                    }
                },
                {
                    "insertText": {
                        "location": {"index": 1},
                        "text": content,
                    }
                },
            ]

            self.service.documents().batchUpdate(
                documentId=document_id, body={"requests": requests}
            ).execute()

            return {
                "document_id": document_id,
                "url": f"https://docs.google.com/document/d/{document_id}",
                "status": "updated",
            }
        except HttpError as e:
            raise RuntimeError(f"Failed to update Google Doc: {e}")


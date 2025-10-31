from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, List
import requests
import json

class FacebookPublishingRequest(BaseModel):
    """Input schema for Facebook Publishing Tool."""
    message: str = Field(..., description="The main post text content to publish on Facebook")
    page_access_token: str = Field(default="", description="Facebook page access token (optional, will use environment variable if not provided)")
    page_id: str = Field(default="", description="Facebook page ID (optional, will use environment variable if not provided)")

class FacebookPublishingTool(BaseTool):
    """Tool for posting content to Facebook pages using the Facebook Graph API."""

    name: str = "publish_to_facebook"
    description: str = (
        "Posts content to Facebook pages using the Facebook Graph API. "
        "Requires Facebook page access token and page ID for authentication. "
        "Returns success confirmation with post ID or detailed error message."
    )
    args_schema: Type[BaseModel] = FacebookPublishingRequest

    def _run(self, message: str, page_access_token: str = "", page_id: str = "") -> str:
        """
        Publish content to a Facebook page using the Graph API.
        
        Args:
            message: The text content to post
            page_access_token: Facebook page access token (optional)
            page_id: Facebook page ID (optional)
            
        Returns:
            Success message with post ID or error description
        """
        try:
            # Use provided parameters or fall back to environment variables
            import os
            
            access_token = page_access_token or os.getenv('FACEBOOK_PAGE_ACCESS_TKN', '')
            fb_page_id = page_id or os.getenv('FACEBOOK_PAGE_ID', '')
            
            # Validate required parameters
            if not access_token:
                return "Error: Facebook page access token is required. Please provide it as parameter or set FACEBOOK_PAGE_ACCESS_TKN environment variable."
            
            if not fb_page_id:
                return "Error: Facebook page ID is required. Please provide it as parameter or set FACEBOOK_PAGE_ID environment variable."
            
            if not message or not message.strip():
                return "Error: Message content cannot be empty."
            
            # Construct the Facebook Graph API URL
            api_url = f"https://graph.facebook.com/v18.0/{fb_page_id}/feed"
            
            # Prepare the payload
            payload = {
                'message': message.strip(),
                'access_token': access_token
            }
            
            # Make the POST request to Facebook Graph API
            response = requests.post(
                api_url,
                data=payload,
                timeout=30,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            
            # Check if the request was successful
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    post_id = response_data.get('id', 'Unknown')
                    return f"✅ Successfully published to Facebook! Post ID: {post_id}"
                except json.JSONDecodeError:
                    return "✅ Successfully published to Facebook! (Post ID unavailable)"
            
            # Handle different types of errors
            elif response.status_code == 400:
                try:
                    error_data = response.json()
                    error_message = error_data.get('error', {}).get('message', 'Bad request')
                    return f"❌ Facebook API Error (400): {error_message}"
                except json.JSONDecodeError:
                    return "❌ Facebook API Error (400): Invalid request parameters"
            
            elif response.status_code == 401:
                return "❌ Facebook API Error (401): Invalid or expired access token. Please check your Facebook page access token."
            
            elif response.status_code == 403:
                return "❌ Facebook API Error (403): Insufficient permissions. Make sure your access token has 'pages_manage_posts' permission."
            
            elif response.status_code == 404:
                return f"❌ Facebook API Error (404): Page not found. Please verify the page ID: {fb_page_id}"
            
            elif response.status_code == 429:
                return "❌ Facebook API Error (429): Rate limit exceeded. Please wait before making another request."
            
            else:
                try:
                    error_data = response.json()
                    error_message = error_data.get('error', {}).get('message', f'HTTP {response.status_code}')
                    return f"❌ Facebook API Error ({response.status_code}): {error_message}"
                except json.JSONDecodeError:
                    return f"❌ Facebook API Error: HTTP {response.status_code} - {response.reason}"
        
        except requests.exceptions.Timeout:
            return "❌ Error: Request timed out. Facebook API may be temporarily unavailable."
        
        except requests.exceptions.ConnectionError:
            return "❌ Error: Failed to connect to Facebook API. Please check your internet connection."
        
        except requests.exceptions.RequestException as e:
            return f"❌ Network Error: {str(e)}"
        
        except Exception as e:
            return f"❌ Unexpected Error: {str(e)}"
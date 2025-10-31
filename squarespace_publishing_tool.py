from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, List, Optional
import requests
import json


class SquarespacePublishingRequest(BaseModel):
    """Input schema for Squarespace Publishing Tool."""
    title: str = Field(..., description="The title of the blog post")
    body: str = Field(..., description="The body content of the blog post in HTML format")
    excerpt: Optional[str] = Field(None, description="Optional excerpt/summary of the blog post")
    tags: Optional[List[str]] = Field(None, description="Optional list of tags for the blog post")


class SquarespacePublishingTool(BaseTool):
    """Tool for publishing blog posts to Squarespace using their API v1.0."""

    name: str = "publish_to_squarespace"
    description: str = (
        "Publishes a blog post to Squarespace using their API. "
        "Takes a title, HTML body content, optional excerpt, and optional tags. "
        "Returns success confirmation with blog post URL or error message."
    )
    args_schema: Type[BaseModel] = SquarespacePublishingRequest

    def _run(self, title: str, body: str, excerpt: Optional[str] = None, tags: Optional[List[str]] = None) -> str:
        """
        Publish a blog post to Squarespace.
        
        Args:
            title: The title of the blog post
            body: The body content in HTML format
            excerpt: Optional excerpt/summary
            tags: Optional list of tags
            
        Returns:
            Success message with URL or error message
        """
        try:
            # Get environment variables
            import os
            api_key = os.getenv('SQUARESPACE_API_KEY')
            site_id = os.getenv('SQUARESPACE_SITE_ID')
            
            if not api_key:
                return "Error: SQUARESPACE_API_KEY environment variable is required"
            
            if not site_id:
                return "Error: SQUARESPACE_SITE_ID environment variable is required"
            
            # Prepare the API endpoint
            url = f"https://api.squarespace.com/1.0/sites/{site_id}/blog/posts"
            
            # Prepare headers
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
                'User-Agent': 'CrewAI-SquarespacePublishingTool/1.0'
            }
            
            # Prepare the blog post data
            post_data = {
                'title': title,
                'body': body,
                'publishOn': 'now',  # Publish immediately
                'type': 'text'  # Text-based blog post
            }
            
            # Add optional fields if provided
            if excerpt:
                post_data['excerpt'] = excerpt
            
            if tags:
                post_data['tags'] = tags
            
            # Make the API request
            response = requests.post(
                url,
                headers=headers,
                json=post_data,
                timeout=30
            )
            
            # Handle the response
            if response.status_code == 200 or response.status_code == 201:
                try:
                    response_data = response.json()
                    post_id = response_data.get('id', '')
                    post_url = response_data.get('fullUrl', '')
                    
                    if post_url:
                        return f"✅ Blog post published successfully!\n" \
                               f"Title: {title}\n" \
                               f"Post ID: {post_id}\n" \
                               f"Public URL: {post_url}"
                    else:
                        return f"✅ Blog post created successfully with ID: {post_id}, but URL not available in response."
                        
                except json.JSONDecodeError:
                    return f"✅ Blog post appears to have been created (HTTP {response.status_code}), but response format was unexpected."
            
            elif response.status_code == 400:
                try:
                    error_data = response.json()
                    error_message = error_data.get('message', 'Bad request')
                    return f"❌ Error creating blog post: {error_message} (HTTP 400)"
                except json.JSONDecodeError:
                    return f"❌ Error creating blog post: Bad request (HTTP 400)"
            
            elif response.status_code == 401:
                return "❌ Error: Unauthorized. Please check your SQUARESPACE_API_KEY."
            
            elif response.status_code == 403:
                return "❌ Error: Forbidden. Your API key may not have permission to create blog posts."
            
            elif response.status_code == 404:
                return "❌ Error: Site not found. Please check your SQUARESPACE_SITE_ID."
            
            elif response.status_code == 429:
                return "❌ Error: Rate limit exceeded. Please try again later."
            
            else:
                try:
                    error_data = response.json()
                    error_message = error_data.get('message', f'HTTP {response.status_code}')
                    return f"❌ Error creating blog post: {error_message}"
                except json.JSONDecodeError:
                    return f"❌ Error creating blog post: HTTP {response.status_code} - {response.text[:200]}"
        
        except requests.exceptions.Timeout:
            return "❌ Error: Request timed out. Please try again."
        
        except requests.exceptions.ConnectionError:
            return "❌ Error: Could not connect to Squarespace API. Please check your internet connection."
        
        except requests.exceptions.RequestException as e:
            return f"❌ Error making API request: {str(e)}"
        
        except Exception as e:
            return f"❌ Unexpected error: {str(e)}"
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Dict, Any, List
import requests
import json
import hashlib
import math

class StorePerformanceDataInput(BaseModel):
    """Input schema for PineconeStorageTool."""
    content_id: str = Field(..., description="Unique identifier for the content")
    content_text: str = Field(..., description="The actual content text")
    performance_metrics: Dict[str, Any] = Field(..., description="Engagement data like likes, shares, comments")
    content_type: str = Field(..., description="Type of content: facebook_post or blog_post")
    story_characteristics: Dict[str, Any] = Field(..., description="Story themes, target audience, etc.")

class PineconeStorageTool(BaseTool):
    """Tool for storing performance data in Pinecone vector database."""

    name: str = "store_performance_data"
    description: str = (
        "Stores performance data in Pinecone vector database. "
        "Creates embeddings from content text and stores with metadata for similarity searches. "
        "Supports both facebook_post and blog_post content types."
    )
    args_schema: Type[BaseModel] = StorePerformanceDataInput

    def _create_simple_embedding(self, text: str, dimension: int = 384) -> List[float]:
        """
        Creates a simple text-based embedding using character frequency and basic text features.
        This is a simplified approach for demonstration purposes.
        """
        try:
            # Normalize text
            text = text.lower().strip()
            
            # Create character frequency vector
            char_freq = {}
            for char in text:
                if char.isalnum() or char.isspace():
                    char_freq[char] = char_freq.get(char, 0) + 1
            
            # Create basic text features
            features = [
                len(text),  # Text length
                len(text.split()),  # Word count
                text.count('.'),  # Sentence count approximation
                text.count('!'),  # Exclamation marks
                text.count('?'),  # Question marks
                sum(1 for c in text if c.isupper()),  # Uppercase letters
                text.count(' '),  # Space count
            ]
            
            # Add character frequencies (normalized)
            total_chars = len(text) if len(text) > 0 else 1
            for i in range(26):  # a-z
                char = chr(ord('a') + i)
                features.append(char_freq.get(char, 0) / total_chars)
            
            # Add digit frequencies
            for i in range(10):  # 0-9
                char = str(i)
                features.append(char_freq.get(char, 0) / total_chars)
            
            # Pad or truncate to desired dimension
            while len(features) < dimension:
                features.append(0.0)
            features = features[:dimension]
            
            # Normalize vector
            magnitude = math.sqrt(sum(x * x for x in features))
            if magnitude > 0:
                features = [x / magnitude for x in features]
            
            return features
            
        except Exception as e:
            # Return a default vector if embedding creation fails
            return [0.1] * dimension

    def _get_pinecone_host(self, environment: str, index_name: str) -> str:
        """Construct Pinecone host URL."""
        return f"https://{index_name}-{environment}.svc.pinecone.io"

    def _run(self, content_id: str, content_text: str, performance_metrics: Dict[str, Any], 
             content_type: str, story_characteristics: Dict[str, Any]) -> str:
        """
        Store performance data in Pinecone vector database.
        """
        try:
            # Get environment variables
            import os
            api_key = os.getenv('PINECONE_API_KEY')
            environment = os.getenv('PINECONE_ENVIRONMENT')
            index_name = os.getenv('PINECONE_INDEX_NAME')
            
            if not all([api_key, environment, index_name]):
                return "Error: Missing required environment variables (PINECONE_API_KEY, PINECONE_ENVIRONMENT, PINECONE_INDEX_NAME)"
            
            # Validate content type
            if content_type not in ['facebook_post', 'blog_post']:
                return "Error: content_type must be either 'facebook_post' or 'blog_post'"
            
            # Create embedding from content text
            embedding = self._create_simple_embedding(content_text)
            
            # Prepare metadata
            metadata = {
                'content_type': content_type,
                'content_text': content_text[:1000],  # Truncate for storage efficiency
                'performance_metrics': performance_metrics,
                'story_characteristics': story_characteristics,
                'text_length': len(content_text),
                'word_count': len(content_text.split())
            }
            
            # Prepare vector data for Pinecone
            vector_data = {
                'vectors': [{
                    'id': content_id,
                    'values': embedding,
                    'metadata': metadata
                }]
            }
            
            # Pinecone API endpoint
            host = self._get_pinecone_host(environment, index_name)
            upsert_url = f"{host}/vectors/upsert"
            
            # Headers for Pinecone API
            headers = {
                'Api-Key': api_key,
                'Content-Type': 'application/json'
            }
            
            # Make API request to store vector
            response = requests.post(
                upsert_url,
                headers=headers,
                json=vector_data,
                timeout=30
            )
            
            # Check response
            if response.status_code == 200:
                result = response.json()
                upserted_count = result.get('upsertedCount', 0)
                return f"Success: Stored performance data for content_id '{content_id}'. Upserted {upserted_count} vector(s) in Pinecone index '{index_name}'."
            else:
                error_msg = f"Pinecone API error (status {response.status_code})"
                try:
                    error_detail = response.json()
                    error_msg += f": {error_detail}"
                except:
                    error_msg += f": {response.text}"
                return f"Error: {error_msg}"
                
        except requests.exceptions.Timeout:
            return "Error: Request to Pinecone API timed out. Please try again."
        
        except requests.exceptions.ConnectionError:
            return "Error: Could not connect to Pinecone API. Please check your internet connection and Pinecone configuration."
        
        except requests.exceptions.RequestException as e:
            return f"Error: Request failed - {str(e)}"
        
        except Exception as e:
            return f"Error: An unexpected error occurred - {str(e)}"
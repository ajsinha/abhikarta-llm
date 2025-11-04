"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
Version: 3.1.4

Multimodal Support - Images, Audio, Video, Documents
"""

import os
import base64
import mimetypes
from typing import Union, BinaryIO, Optional, Dict, Any, List
from dataclasses import dataclass
from pathlib import Path
from enum import Enum


class MediaType(Enum):
    """Supported media types"""
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    TEXT = "text"


@dataclass
class MediaContent:
    """
    Represents multimodal content.
    
    Attributes:
        data: The media data (bytes, base64 string, or file path)
        media_type: Type of media
        mime_type: MIME type (e.g., 'image/jpeg', 'audio/mp3')
        filename: Optional filename
        metadata: Additional metadata
    """
    data: Union[bytes, str]
    media_type: MediaType
    mime_type: str
    filename: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def to_base64(self) -> str:
        """Convert data to base64 string"""
        if isinstance(self.data, bytes):
            return base64.b64encode(self.data).decode('utf-8')
        elif isinstance(self.data, str) and os.path.exists(self.data):
            with open(self.data, 'rb') as f:
                return base64.b64encode(f.read()).decode('utf-8')
        return self.data
    
    def to_bytes(self) -> bytes:
        """Convert data to bytes"""
        if isinstance(self.data, bytes):
            return self.data
        elif isinstance(self.data, str) and os.path.exists(self.data):
            with open(self.data, 'rb') as f:
                return f.read()
        elif isinstance(self.data, str):
            # Assume base64 encoded
            return base64.b64decode(self.data)
        return b''
    
    def to_data_url(self) -> str:
        """Convert to data URL format"""
        b64_data = self.to_base64()
        return f"data:{self.mime_type};base64,{b64_data}"


class MultimodalProcessor:
    """
    Process and prepare multimodal content for LLM consumption.
    
    Example:
        processor = MultimodalProcessor()
        
        # Load image
        image = processor.load_image("photo.jpg")
        
        # Load audio
        audio = processor.load_audio("speech.mp3")
        
        # Create multimodal prompt
        prompt = processor.create_prompt(
            text="What's in this image?",
            media=[image]
        )
    """
    
    SUPPORTED_IMAGE_FORMATS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
    SUPPORTED_AUDIO_FORMATS = {'.mp3', '.wav', '.ogg', '.m4a', '.flac'}
    SUPPORTED_VIDEO_FORMATS = {'.mp4', '.avi', '.mov', '.mkv', '.webm'}
    
    def __init__(self):
        self.media_cache: Dict[str, MediaContent] = {}
    
    def load_image(
        self,
        source: Union[str, bytes, BinaryIO],
        filename: Optional[str] = None
    ) -> MediaContent:
        """
        Load an image from file path, bytes, or file object.
        
        Args:
            source: Image source (path, bytes, or file object)
            filename: Optional filename
        
        Returns:
            MediaContent object
        """
        if isinstance(source, str):
            if not os.path.exists(source):
                raise FileNotFoundError(f"Image file not found: {source}")
            
            mime_type = mimetypes.guess_type(source)[0] or 'image/jpeg'
            filename = filename or os.path.basename(source)
            
            with open(source, 'rb') as f:
                data = f.read()
        
        elif isinstance(source, bytes):
            data = source
            mime_type = 'image/jpeg'  # Default
            filename = filename or 'image.jpg'
        
        else:  # File object
            data = source.read()
            mime_type = 'image/jpeg'
            filename = filename or 'image.jpg'
        
        return MediaContent(
            data=data,
            media_type=MediaType.IMAGE,
            mime_type=mime_type,
            filename=filename
        )
    
    def load_audio(
        self,
        source: Union[str, bytes, BinaryIO],
        filename: Optional[str] = None
    ) -> MediaContent:
        """Load audio file"""
        if isinstance(source, str):
            if not os.path.exists(source):
                raise FileNotFoundError(f"Audio file not found: {source}")
            
            mime_type = mimetypes.guess_type(source)[0] or 'audio/mpeg'
            filename = filename or os.path.basename(source)
            
            with open(source, 'rb') as f:
                data = f.read()
        
        elif isinstance(source, bytes):
            data = source
            mime_type = 'audio/mpeg'
            filename = filename or 'audio.mp3'
        
        else:
            data = source.read()
            mime_type = 'audio/mpeg'
            filename = filename or 'audio.mp3'
        
        return MediaContent(
            data=data,
            media_type=MediaType.AUDIO,
            mime_type=mime_type,
            filename=filename
        )
    
    def load_video(
        self,
        source: Union[str, bytes, BinaryIO],
        filename: Optional[str] = None
    ) -> MediaContent:
        """Load video file"""
        if isinstance(source, str):
            if not os.path.exists(source):
                raise FileNotFoundError(f"Video file not found: {source}")
            
            mime_type = mimetypes.guess_type(source)[0] or 'video/mp4'
            filename = filename or os.path.basename(source)
            
            with open(source, 'rb') as f:
                data = f.read()
        
        elif isinstance(source, bytes):
            data = source
            mime_type = 'video/mp4'
            filename = filename or 'video.mp4'
        
        else:
            data = source.read()
            mime_type = 'video/mp4'
            filename = filename or 'video.mp4'
        
        return MediaContent(
            data=data,
            media_type=MediaType.VIDEO,
            mime_type=mime_type,
            filename=filename
        )
    
    def create_prompt(
        self,
        text: str,
        media: List[MediaContent],
        template: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a multimodal prompt combining text and media.
        
        Args:
            text: Text prompt
            media: List of MediaContent objects
            template: Optional template for formatting
        
        Returns:
            Dictionary with prompt data
        """
        prompt = {
            'text': text,
            'media': []
        }
        
        for item in media:
            prompt['media'].append({
                'type': item.media_type.value,
                'mime_type': item.mime_type,
                'data': item.to_base64(),
                'filename': item.filename
            })
        
        if template:
            prompt['template'] = template
        
        return prompt
    
    def validate_media(self, filepath: str) -> tuple[bool, str]:
        """
        Validate if a file is supported.
        
        Returns:
            (is_valid, media_type)
        """
        ext = Path(filepath).suffix.lower()
        
        if ext in self.SUPPORTED_IMAGE_FORMATS:
            return True, 'image'
        elif ext in self.SUPPORTED_AUDIO_FORMATS:
            return True, 'audio'
        elif ext in self.SUPPORTED_VIDEO_FORMATS:
            return True, 'video'
        else:
            return False, 'unknown'


def load_image_from_url(url: str) -> MediaContent:
    """
    Load image from URL.
    
    Args:
        url: Image URL
    
    Returns:
        MediaContent object
    """
    import urllib.request
    
    with urllib.request.urlopen(url) as response:
        data = response.read()
        mime_type = response.headers.get('Content-Type', 'image/jpeg')
    
    return MediaContent(
        data=data,
        media_type=MediaType.IMAGE,
        mime_type=mime_type,
        filename=url.split('/')[-1]
    )


__all__ = [
    'MediaType',
    'MediaContent',
    'MultimodalProcessor',
    'load_image_from_url',
]


"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha | ajsinha@gmail.com | Version: 3.1.4
"""

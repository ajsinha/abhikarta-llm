"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
Version: 3.1.6

Comprehensive Multimodal Support - Images, Audio, Video, Documents
"""

import base64
import os
import mimetypes
from typing import Union, Optional, Dict, Any, List
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod


class MediaType(Enum):
    """Media type enumeration"""
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    TEXT = "text"


# ============================================================================
# BASE CLASSES
# ============================================================================

@dataclass
class MediaInput:
    """
    Base class for multimodal input.
    
    Attributes:
        data: Base64-encoded data or file path
        media_type: Type of media
        mime_type: MIME type (e.g., 'image/jpeg', 'audio/mp3')
        filename: Original filename (optional)
    """
    data: str
    media_type: MediaType
    mime_type: str
    filename: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        return {
            'type': self.media_type.value,
            'mime_type': self.mime_type,
            'data': self.data,
            'filename': self.filename
        }


# ============================================================================
# IMAGE SUPPORT
# ============================================================================

@dataclass
class ImageInput(MediaInput):
    """
    Image input with vision-specific properties.
    
    Attributes:
        data: Base64-encoded image data
        mime_type: Image MIME type
        width: Image width (optional)
        height: Image height (optional)
        detail: Detail level for vision models ('low', 'high', 'auto')
    """
    width: Optional[int] = None
    height: Optional[int] = None
    detail: str = 'auto'
    
    def __post_init__(self):
        self.media_type = MediaType.IMAGE


class VisionCapability(ABC):
    """Abstract base class for vision capabilities"""
    
    @abstractmethod
    def analyze_image(self, image: ImageInput, prompt: str) -> str:
        """Analyze image with prompt"""
        pass
    
    @abstractmethod
    def supports_vision(self) -> bool:
        """Check if provider supports vision"""
        pass


class VisionProcessor:
    """
    Processor for vision/image tasks.
    
    Example:
        processor = VisionProcessor()
        image = processor.load_image('photo.jpg')
        result = processor.describe_image(image, "What's in this image?")
    """
    
    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg'}
    
    @staticmethod
    def encode_image(filepath: Union[str, Path]) -> str:
        """Encode image to base64"""
        with open(filepath, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    
    @staticmethod
    def get_mime_type(filepath: Union[str, Path]) -> str:
        """Get MIME type from file path"""
        mime_type, _ = mimetypes.guess_type(str(filepath))
        return mime_type or 'image/jpeg'
    
    def load_image(
        self,
        source: Union[str, Path, bytes],
        mime_type: Optional[str] = None,
        detail: str = 'auto'
    ) -> ImageInput:
        """
        Load an image.
        
        Args:
            source: File path or bytes
            mime_type: MIME type (auto-detected if not provided)
            detail: Detail level ('low', 'high', 'auto')
        
        Returns:
            ImageInput object
        """
        if isinstance(source, bytes):
            data = base64.b64encode(source).decode('utf-8')
            mime_type = mime_type or 'image/jpeg'
            filename = None
        else:
            filepath = Path(source)
            if not filepath.exists():
                raise FileNotFoundError(f"Image file not found: {filepath}")
            
            ext = filepath.suffix.lower()
            if ext not in self.SUPPORTED_FORMATS:
                raise ValueError(f"Unsupported image format: {ext}")
            
            data = self.encode_image(filepath)
            mime_type = mime_type or self.get_mime_type(filepath)
            filename = filepath.name
        
        return ImageInput(
            data=data,
            mime_type=mime_type,
            filename=filename,
            detail=detail
        )
    
    def describe_image(self, image: ImageInput, prompt: str = "Describe this image") -> Dict[str, Any]:
        """
        Describe an image (placeholder - requires LLM provider).
        
        Args:
            image: ImageInput object
            prompt: Description prompt
        
        Returns:
            Dictionary with description
        """
        return {
            'image': image.filename or 'image',
            'prompt': prompt,
            'note': 'Use with vision-capable LLM provider'
        }


# ============================================================================
# AUDIO SUPPORT
# ============================================================================

@dataclass
class AudioInput(MediaInput):
    """
    Audio input with voice-specific properties.
    
    Attributes:
        data: Base64-encoded audio data
        mime_type: Audio MIME type
        duration: Audio duration in seconds (optional)
        language: Audio language code (optional)
        format: Audio format (e.g., 'mp3', 'wav')
    """
    duration: Optional[float] = None
    language: Optional[str] = None
    format: Optional[str] = None
    
    def __post_init__(self):
        self.media_type = MediaType.AUDIO


class VoiceCapability(ABC):
    """Abstract base class for voice/audio capabilities"""
    
    @abstractmethod
    def transcribe_audio(self, audio: AudioInput) -> str:
        """Transcribe audio to text"""
        pass
    
    @abstractmethod
    def supports_audio(self) -> bool:
        """Check if provider supports audio"""
        pass


class VoiceProcessor:
    """
    Processor for audio/voice tasks.
    
    Example:
        processor = VoiceProcessor()
        audio = processor.load_audio('speech.mp3')
        transcript = processor.transcribe(audio)
    """
    
    SUPPORTED_FORMATS = {'.mp3', '.wav', '.m4a', '.flac', '.aac', '.ogg', '.opus'}
    
    @staticmethod
    def encode_audio(filepath: Union[str, Path]) -> str:
        """Encode audio to base64"""
        with open(filepath, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    
    @staticmethod
    def get_mime_type(filepath: Union[str, Path]) -> str:
        """Get MIME type from file path"""
        mime_type, _ = mimetypes.guess_type(str(filepath))
        return mime_type or 'audio/mpeg'
    
    def load_audio(
        self,
        source: Union[str, Path, bytes],
        mime_type: Optional[str] = None,
        language: Optional[str] = None
    ) -> AudioInput:
        """
        Load audio file.
        
        Args:
            source: File path or bytes
            mime_type: MIME type (auto-detected if not provided)
            language: Language code (e.g., 'en', 'es')
        
        Returns:
            AudioInput object
        """
        if isinstance(source, bytes):
            data = base64.b64encode(source).decode('utf-8')
            mime_type = mime_type or 'audio/mpeg'
            filename = None
            audio_format = None
        else:
            filepath = Path(source)
            if not filepath.exists():
                raise FileNotFoundError(f"Audio file not found: {filepath}")
            
            ext = filepath.suffix.lower()
            if ext not in self.SUPPORTED_FORMATS:
                raise ValueError(f"Unsupported audio format: {ext}")
            
            data = self.encode_audio(filepath)
            mime_type = mime_type or self.get_mime_type(filepath)
            filename = filepath.name
            audio_format = ext[1:]  # Remove the dot
        
        return AudioInput(
            data=data,
            mime_type=mime_type,
            filename=filename,
            language=language,
            format=audio_format
        )
    
    def transcribe(self, audio: AudioInput) -> Dict[str, Any]:
        """
        Transcribe audio (placeholder - requires speech-to-text provider).
        
        Args:
            audio: AudioInput object
        
        Returns:
            Dictionary with transcription info
        """
        return {
            'audio': audio.filename or 'audio',
            'format': audio.format,
            'note': 'Use with speech-to-text provider (e.g., OpenAI Whisper)'
        }


# ============================================================================
# MULTIMODAL MESSAGE
# ============================================================================

@dataclass
class MultimodalMessage:
    """
    Message that can contain text and multiple media types.
    
    Example:
        message = MultimodalMessage(
            text="Describe this image and transcribe this audio",
            images=[image1, image2],
            audio=[audio1]
        )
    """
    text: str
    images: List[ImageInput] = field(default_factory=list)
    audio: List[AudioInput] = field(default_factory=list)
    videos: List[MediaInput] = field(default_factory=list)
    documents: List[MediaInput] = field(default_factory=list)
    role: str = "user"  # 'user', 'assistant', 'system'
    
    def add_image(self, image: ImageInput):
        """Add an image to the message"""
        self.images.append(image)
    
    def add_audio(self, audio: AudioInput):
        """Add audio to the message"""
        self.audio.append(audio)
    
    def has_media(self) -> bool:
        """Check if message contains any media"""
        return bool(self.images or self.audio or self.videos or self.documents)
    
    def media_count(self) -> int:
        """Get total media count"""
        return len(self.images) + len(self.audio) + len(self.videos) + len(self.documents)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        return {
            'role': self.role,
            'text': self.text,
            'images': [img.to_dict() for img in self.images],
            'audio': [aud.to_dict() for aud in self.audio],
            'videos': [vid.to_dict() for vid in self.videos],
            'documents': [doc.to_dict() for doc in self.documents],
            'has_media': self.has_media(),
            'media_count': self.media_count()
        }


# ============================================================================
# MULTIMODAL HANDLER (Original)
# ============================================================================

class MultimodalHandler:
    """
    Main handler for all multimodal inputs.
    
    Example:
        handler = MultimodalHandler()
        image = handler.load_image('photo.jpg')
        audio = handler.load_audio('speech.mp3')
        video = handler.load_video('clip.mp4')
    """
    
    # Supported file types
    SUPPORTED_IMAGES = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg'}
    SUPPORTED_AUDIO = {'.mp3', '.wav', '.m4a', '.flac', '.aac', '.ogg', '.opus'}
    SUPPORTED_VIDEO = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv'}
    SUPPORTED_DOCUMENTS = {'.pdf', '.doc', '.docx', '.txt', '.md', '.html', '.csv', '.xlsx'}
    
    def __init__(self):
        self.vision_processor = VisionProcessor()
        self.voice_processor = VoiceProcessor()
    
    @staticmethod
    def encode_file(filepath: Union[str, Path]) -> str:
        """Encode file to base64"""
        with open(filepath, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    
    @staticmethod
    def encode_bytes(data: bytes) -> str:
        """Encode bytes to base64"""
        return base64.b64encode(data).decode('utf-8')
    
    @staticmethod
    def get_mime_type(filepath: Union[str, Path]) -> str:
        """Get MIME type from file path"""
        mime_type, _ = mimetypes.guess_type(str(filepath))
        return mime_type or 'application/octet-stream'
    
    def load_image(
        self,
        source: Union[str, Path, bytes],
        mime_type: Optional[str] = None,
        detail: str = 'auto'
    ) -> ImageInput:
        """Load an image - delegates to VisionProcessor"""
        return self.vision_processor.load_image(source, mime_type, detail)
    
    def load_audio(
        self,
        source: Union[str, Path, bytes],
        mime_type: Optional[str] = None,
        language: Optional[str] = None
    ) -> AudioInput:
        """Load audio - delegates to VoiceProcessor"""
        return self.voice_processor.load_audio(source, mime_type, language)
    
    def load_video(
        self,
        source: Union[str, Path, bytes],
        mime_type: Optional[str] = None
    ) -> MediaInput:
        """Load video file"""
        if isinstance(source, bytes):
            data = self.encode_bytes(source)
            mime_type = mime_type or 'video/mp4'
            filename = None
        else:
            filepath = Path(source)
            if not filepath.exists():
                raise FileNotFoundError(f"Video file not found: {filepath}")
            
            ext = filepath.suffix.lower()
            if ext not in self.SUPPORTED_VIDEO:
                raise ValueError(f"Unsupported video format: {ext}")
            
            data = self.encode_file(filepath)
            mime_type = mime_type or self.get_mime_type(filepath)
            filename = filepath.name
        
        return MediaInput(
            data=data,
            media_type=MediaType.VIDEO,
            mime_type=mime_type,
            filename=filename
        )
    
    def load_document(
        self,
        source: Union[str, Path, bytes],
        mime_type: Optional[str] = None
    ) -> MediaInput:
        """Load document file"""
        if isinstance(source, bytes):
            data = self.encode_bytes(source)
            mime_type = mime_type or 'application/pdf'
            filename = None
        else:
            filepath = Path(source)
            if not filepath.exists():
                raise FileNotFoundError(f"Document file not found: {filepath}")
            
            ext = filepath.suffix.lower()
            if ext not in self.SUPPORTED_DOCUMENTS:
                raise ValueError(f"Unsupported document format: {ext}")
            
            data = self.encode_file(filepath)
            mime_type = mime_type or self.get_mime_type(filepath)
            filename = filepath.name
        
        return MediaInput(
            data=data,
            media_type=MediaType.DOCUMENT,
            mime_type=mime_type,
            filename=filename
        )
    
    def create_multimodal_message(
        self,
        text: str,
        images: Optional[List[ImageInput]] = None,
        audio: Optional[List[AudioInput]] = None,
        role: str = "user"
    ) -> MultimodalMessage:
        """
        Create a multimodal message.
        
        Args:
            text: Text content
            images: List of images
            audio: List of audio files
            role: Message role
        
        Returns:
            MultimodalMessage object
        """
        return MultimodalMessage(
            text=text,
            images=images or [],
            audio=audio or [],
            role=role
        )


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Enums
    'MediaType',
    
    # Base classes
    'MediaInput',
    
    # Image support
    'ImageInput',
    'VisionCapability',
    'VisionProcessor',
    
    # Audio support
    'AudioInput',
    'VoiceCapability',
    'VoiceProcessor',
    
    # Multimodal
    'MultimodalMessage',
    'MultimodalHandler',
]


"""
Copyright 2025-2030 all rights reserved
Ashutosh Sinha | ajsinha@gmail.com | Version: 3.1.6
"""

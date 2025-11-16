"""
Abhikarta LLM Platform
Copyright © 2025-2030, Ashutosh Sinha (ajsinha@gmail.com)
"""


import json
import pickle
import base64
from typing import Any
from datetime import datetime, date
from pathlib import Path

class JSONEncoder(json.JSONEncoder):
    """Extended JSON encoder for custom types"""
    
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif isinstance(obj, Path):
            return str(obj)
        elif isinstance(obj, set):
            return list(obj)
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        return super().default(obj)

def serialize_to_json(obj: Any, pretty: bool = False) -> str:
    """Serialize object to JSON"""
    kwargs = {"cls": JSONEncoder}
    if pretty:
        kwargs.update({"indent": 2, "sort_keys": True})
    
    return json.dumps(obj, **kwargs)

def deserialize_from_json(json_str: str) -> Any:
    """Deserialize from JSON"""
    return json.loads(json_str)

def serialize_to_base64(obj: Any) -> str:
    """Serialize object to base64 (using pickle)"""
    pickled = pickle.dumps(obj)
    return base64.b64encode(pickled).decode('utf-8')

def deserialize_from_base64(b64_str: str) -> Any:
    """Deserialize from base64"""
    pickled = base64.b64decode(b64_str.encode('utf-8'))
    return pickle.loads(pickled)

def safe_serialize_state(state: dict) -> str:
    """Safely serialize state dictionary"""
    serializable_state = {}
    
    for key, value in state.items():
        try:
            # Try JSON serialization first
            json.dumps(value, cls=JSONEncoder)
            serializable_state[key] = value
        except (TypeError, ValueError):
            # Fall back to base64 for complex objects
            serializable_state[key] = {
                "_type": "base64",
                "data": serialize_to_base64(value)
            }
    
    return json.dumps(serializable_state, cls=JSONEncoder)

def safe_deserialize_state(state_str: str) -> dict:
    """Safely deserialize state dictionary"""
    state = json.loads(state_str)
    
    deserialized_state = {}
    for key, value in state.items():
        if isinstance(value, dict) and value.get("_type") == "base64":
            deserialized_state[key] = deserialize_from_base64(value["data"])
        else:
            deserialized_state[key] = value
    
    return deserialized_state

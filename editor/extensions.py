from dataclasses import dataclass
from typing import List, Dict, Any
import json

@dataclass
class EditorExtension:
    name: str
    version: str
    components: List[Dict[str, Any]]
    scripts: List[str]

class ExtensionManager:
    def __init__(self):
        self.loaded_extensions = {}
        self.extension_path = "extensions"
    
    def load_extension(self, ext_name: str) -> EditorExtension:
        with open(f"{self.extension_path}/{ext_name}/manifest.json") as f:
            data = json.load(f)
            ext = EditorExtension(**data)
            self.loaded_extensions[ext_name] = ext
            return ext
    
    def get_components(self) -> List[Dict[str, Any]]:
        components = []
        for ext in self.loaded_extensions.values():
            components.extend(ext.components)
        return components

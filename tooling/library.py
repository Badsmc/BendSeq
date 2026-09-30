# tooling/library.py
import json
import os
from typing import Dict, Any, Optional
import FreeCAD

try:
    import Part
    _FC_OK = True
except ImportError:
    _FC_OK = False

class ToolLibrary:
    """
    Loads JSON configuration and BREP shapes from the ToolLibrary directory.
    """
    def __init__(self, library_dir: str):
        self.library_dir = library_dir
        self.json_path = os.path.join(library_dir, "library.json")
        self.data = {}
        self.tools_brep = {}
        self.load()

    def load(self):
        if not os.path.exists(self.json_path):
            FreeCAD.Console.PrintWarning(f"BendSeq: ToolLibrary JSON not found at {self.json_path}\n")
            return
            
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except Exception as e:
            FreeCAD.Console.PrintError(f"BendSeq: Failed to load ToolLibrary JSON: {e}\n")
            
    def get_tool_shape(self, tool_type: str, tool_id: str) -> Optional[Any]:
        """
        Loads and caches a BREP shape for a given tool type (punches, dies, presses, gauges) and ID.
        """
        if not _FC_OK:
            return None
            
        key = f"{tool_type}_{tool_id}"
        if key in self.tools_brep:
            return self.tools_brep[key]
            
        items = self.data.get(tool_type, [])
        for item in items:
            if item.get("id") == tool_id:
                brep_file = item.get("file")
                if brep_file:
                    brep_path = os.path.join(self.library_dir, tool_type, brep_file)
                    if os.path.exists(brep_path):
                        shape = Part.Shape()
                        shape.read(brep_path)
                        self.tools_brep[key] = shape
                        return shape
        return None

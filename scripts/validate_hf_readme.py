#!/usr/bin/env python3
"""
Validate README.md for Hugging Face Space compatibility.

This script checks that the README.md file has:
- Valid YAML frontmatter
- Required fields for HF Spaces (sdk, app_port for docker)
- Correct format and values
"""

import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple

# Required fields for Docker SDK
REQUIRED_DOCKER_FIELDS = {
    "sdk": ["docker"],
    "app_port": lambda x: isinstance(x, int) and 1 <= x <= 65535,
}

# Optional but recommended fields
RECOMMENDED_FIELDS = ["title", "emoji", "colorFrom", "colorTo"]

# Valid color values
VALID_COLORS = {"red", "yellow", "green", "blue", "indigo", "purple", "pink", "gray"}

# Valid SDK values
VALID_SDKS = {"gradio", "docker", "static"}

# Valid hardware flavors (from HF docs)
VALID_HARDWARE = {
    "cpu-basic", "cpu-upgrade",
    "t4-small", "t4-medium", "l4x1", "l4x4",
    "a10g-small", "a10g-large", "a10g-largex2", "a10g-largex4", "a100-large",
    "v5e-1x1", "v5e-2x2", "v5e-2x4"
}


def extract_yaml_frontmatter(content: str) -> Tuple[Dict, int, int]:
    """Extract YAML frontmatter from README.md content."""
    # Check for YAML frontmatter pattern
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not match:
        return {}, -1, -1
    
    yaml_content = match.group(1)
    start_pos = 0
    end_pos = match.end()
    
    # Simple YAML parsing (basic key: value pairs)
    yaml_dict = {}
    for line in yaml_content.split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip().strip('"\'')
            
            # Convert boolean strings
            if value.lower() == 'true':
                value = True
            elif value.lower() == 'false':
                value = False
            # Convert integers
            elif value.isdigit():
                value = int(value)
            
            yaml_dict[key] = value
    
    return yaml_dict, start_pos, end_pos


def validate_readme(readme_path: Path) -> List[str]:
    """Validate README.md file and return list of errors."""
    errors = []
    
    if not readme_path.exists():
        return [f"README.md not found at {readme_path}"]
    
    content = readme_path.read_text(encoding='utf-8')
    
    # Extract YAML frontmatter
    yaml_data, start, end = extract_yaml_frontmatter(content)
    
    if start == -1:
        errors.append("README.md must start with YAML frontmatter (--- ... ---)")
        return errors
    
    # Check SDK
    sdk = yaml_data.get("sdk")
    if not sdk:
        errors.append("Missing required field: 'sdk'")
    elif sdk not in VALID_SDKS:
        errors.append(f"Invalid 'sdk' value: {sdk}. Must be one of: {', '.join(VALID_SDKS)}")
    
    # For Docker SDK, check app_port
    if sdk == "docker":
        app_port = yaml_data.get("app_port")
        if app_port is None:
            errors.append("Missing required field for Docker SDK: 'app_port'")
        elif not isinstance(app_port, int) or not (1 <= app_port <= 65535):
            errors.append(f"Invalid 'app_port' value: {app_port}. Must be an integer between 1 and 65535")
    
    # Check colors if present
    color_from = yaml_data.get("colorFrom")
    color_to = yaml_data.get("colorTo")
    if color_from and color_from not in VALID_COLORS:
        errors.append(f"Invalid 'colorFrom' value: {color_from}. Must be one of: {', '.join(VALID_COLORS)}")
    if color_to and color_to not in VALID_COLORS:
        errors.append(f"Invalid 'colorTo' value: {color_to}. Must be one of: {', '.join(VALID_COLORS)}")
    
    # Check suggested_hardware if present
    hardware = yaml_data.get("suggested_hardware")
    if hardware and hardware not in VALID_HARDWARE:
        errors.append(f"Invalid 'suggested_hardware' value: {hardware}. Must be one of: {', '.join(sorted(VALID_HARDWARE))}")
    
    # Warn about deprecated 'hardware' field
    if "hardware" in yaml_data:
        errors.append("Deprecated field 'hardware' found. Use 'suggested_hardware' instead (per HF Spaces docs)")
    
    # Check for emoji (recommended)
    if "emoji" not in yaml_data:
        errors.append("Warning: 'emoji' field is recommended for better Space appearance")
    
    # Check for title (recommended)
    if "title" not in yaml_data:
        errors.append("Warning: 'title' field is recommended")
    
    # Check that pinned is boolean if present
    if "pinned" in yaml_data and not isinstance(yaml_data["pinned"], bool):
        errors.append(f"Invalid 'pinned' value: {yaml_data['pinned']}. Must be boolean (true/false)")
    
    return errors


def main():
    """Main entry point."""
    repo_root = Path(__file__).parent.parent
    readme_path = repo_root / "README.md"
    
    errors = validate_readme(readme_path)
    
    if errors:
        print("❌ README.md validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        sys.exit(1)
    else:
        print("✅ README.md is valid for Hugging Face Spaces")
        sys.exit(0)


if __name__ == "__main__":
    main()


"""
Dependency Parser Module
Parses requirements.txt and library lists into structured dependencies.
"""

import re
from typing import List, Dict
from packaging.requirements import Requirement


class DependencyParser:
    """Parse requirements.txt and library lists into structured dependencies."""
    
    @staticmethod
    def parse_requirements_text(text: str) -> List[Dict]:
        """Parse requirements.txt content into structured format."""
        dependencies = []
        seen_packages = {}
        
        for line in text.strip().split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Remove comments
            if '#' in line:
                line = line[:line.index('#')].strip()
            
            try:
                req = Requirement(line)
                package_name = req.name.lower()
                
                # Handle duplicate packages
                if package_name in seen_packages:
                    existing = seen_packages[package_name]
                    if existing['specifier'] != str(req.specifier):
                        dependencies.append({
                            'package': package_name,
                            'specifier': str(req.specifier) if req.specifier else '',
                            'extras': list(req.extras) if req.extras else [],
                            'marker': str(req.marker) if req.marker else '',
                            'original': line,
                            'conflict': f"Duplicate: {existing['original']} vs {line}"
                        })
                    continue
                
                dep = {
                    'package': package_name,
                    'specifier': str(req.specifier) if req.specifier else '',
                    'extras': list(req.extras) if req.extras else [],
                    'marker': str(req.marker) if req.marker else '',
                    'original': line,
                    'conflict': None
                }
                dependencies.append(dep)
                seen_packages[package_name] = dep
            except Exception as e:
                # Handle malformed lines
                dependencies.append({
                    'package': line.split('==')[0].split('>=')[0].split('<=')[0].split('[')[0].strip(),
                    'specifier': '',
                    'extras': [],
                    'marker': '',
                    'original': line,
                    'conflict': f"Parse error: {str(e)}"
                })
        
        return dependencies
    
    @staticmethod
    def parse_library_list(text: str) -> List[Dict]:
        """Parse a simple list of library names."""
        dependencies = []
        for line in text.strip().split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Extract package name (remove version specifiers if present)
            package_name = re.split(r'[<>=!]', line)[0].strip()
            package_name = re.split(r'\[', package_name)[0].strip()
            
            if package_name:
                dependencies.append({
                    'package': package_name.lower(),
                    'specifier': '',
                    'extras': [],
                    'marker': '',
                    'original': package_name,
                    'conflict': None
                })
        
        return dependencies


"""
Conflict Detector Module
Detects version conflicts and compatibility issues in dependencies.
"""

from typing import List, Dict, Tuple


class ConflictDetector:
    """Detect conflicts and compatibility issues in dependencies."""
    
    @staticmethod
    def build_dependency_graph(dependencies: List[Dict]) -> Dict:
        """Build dependency graph from parsed dependencies."""
        graph = {
            'nodes': {},
            'edges': [],
            'conflicts': []
        }
        
        for dep in dependencies:
            package = dep['package']
            graph['nodes'][package] = {
                'specifier': dep['specifier'],
                'extras': dep['extras'],
                'marker': dep['marker'],
                'conflict': dep.get('conflict')
            }
            
            if dep.get('conflict'):
                graph['conflicts'].append({
                    'package': package,
                    'reason': dep['conflict']
                })
        
        return graph
    
    @staticmethod
    def check_compatibility(graph: Dict) -> Tuple[bool, List[Dict]]:
        """Check version compatibility across the graph."""
        issues = []
        
        # Check for duplicate package conflicts
        for conflict in graph['conflicts']:
            issues.append({
                'type': 'duplicate',
                'package': conflict['package'],
                'message': f"Conflict in {conflict['package']}: {conflict['reason']}",
                'severity': 'high'
            })
        
        # Check known compatibility issues
        nodes = graph['nodes']
        
        # PyTorch Lightning + PyTorch compatibility
        if 'pytorch-lightning' in nodes and 'torch' in nodes:
            pl_spec = nodes['pytorch-lightning']['specifier']
            torch_spec = nodes['torch']['specifier']
            
            if '==2.' in pl_spec or '>=2.' in pl_spec:
                if '==1.' in torch_spec or ('<2.' in torch_spec and '==1.' in torch_spec):
                    issues.append({
                        'type': 'version_incompatibility',
                        'packages': ['pytorch-lightning', 'torch'],
                        'message': "pytorch-lightning>=2.0 requires torch>=2.0, but torch<2.0 is specified",
                        'severity': 'high',
                        'details': {
                            'pytorch-lightning': pl_spec,
                            'torch': torch_spec
                        }
                    })
        
        # FastAPI + Pydantic compatibility
        if 'fastapi' in nodes and 'pydantic' in nodes:
            fastapi_spec = nodes['fastapi']['specifier']
            pydantic_spec = nodes['pydantic']['specifier']
            
            if '==0.78' in fastapi_spec or '==0.7' in fastapi_spec:
                if '==2.' in pydantic_spec or '>=2.' in pydantic_spec:
                    issues.append({
                        'type': 'version_incompatibility',
                        'packages': ['fastapi', 'pydantic'],
                        'message': "fastapi==0.78.x requires pydantic v1, but pydantic v2 is specified",
                        'severity': 'high',
                        'details': {
                            'fastapi': fastapi_spec,
                            'pydantic': pydantic_spec
                        }
                    })
        
        # TensorFlow + Keras compatibility
        if 'tensorflow' in nodes and 'keras' in nodes:
            tf_spec = nodes['tensorflow']['specifier']
            keras_spec = nodes['keras']['specifier']
            
            if '==1.' in tf_spec:
                if '==3.' in keras_spec or '>=3.' in keras_spec:
                    issues.append({
                        'type': 'version_incompatibility',
                        'packages': ['tensorflow', 'keras'],
                        'message': "keras>=3.0 requires TensorFlow 2.x, but TensorFlow 1.x is specified",
                        'severity': 'high',
                        'details': {
                            'tensorflow': tf_spec,
                            'keras': keras_spec
                        }
                    })
        
        return len(issues) == 0, issues


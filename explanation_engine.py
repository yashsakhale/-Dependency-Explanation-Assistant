"""
Explanation Engine Module
Uses LLM to generate natural language explanations for dependency conflicts.
"""

from typing import List, Dict
import requests
import json


class ExplanationEngine:
    """Generate intelligent explanations for dependency conflicts using LLM."""
    
    def __init__(self, use_local_llm: bool = True):
        """
        Initialize explanation engine.
        
        Args:
            use_local_llm: If True, uses Hugging Face Inference API (free tier)
                          If False, can be configured for other LLM services
        """
        self.use_local_llm = use_local_llm
        # Using Hugging Face Inference API (free tier)
        # Options:
        # 1. GPT-2 (basic, fast, but limited quality)
        # 2. microsoft/DialoGPT-medium (better for conversations)
        # 3. meta-llama/Llama-2-7b-chat-hf (requires API token, better quality)
        # For free tier without token, using GPT-2 with fallback to rule-based
        self.api_url = "https://api-inference.huggingface.co/models/gpt2"
        # Alternative: "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
        self.headers = {"Content-Type": "application/json"}
    
    def generate_explanation(self, conflict: Dict, dependencies: List[Dict]) -> Dict:
        """
        Generate a detailed explanation for a conflict.
        
        Args:
            conflict: Conflict dictionary with type, packages, message, etc.
            dependencies: Full list of dependencies for context
            
        Returns:
            Dictionary with explanation, why_it_happens, how_to_fix
        """
        # Build context about the conflict
        conflict_type = conflict.get('type', 'unknown')
        packages = conflict.get('packages', [conflict.get('package', 'unknown')])
        message = conflict.get('message', '')
        details = conflict.get('details', {})
        
        # Create prompt for LLM
        prompt = self._create_prompt(conflict, dependencies)
        
        # Get LLM explanation
        explanation_text = self._call_llm(prompt)
        
        # Parse and structure the explanation
        return {
            'summary': message,
            'explanation': explanation_text,
            'why_it_happens': self._extract_why(explanation_text, conflict),
            'how_to_fix': self._extract_fix(explanation_text, conflict),
            'packages_involved': packages,
            'severity': conflict.get('severity', 'medium')
        }
    
    def _create_prompt(self, conflict: Dict, dependencies: List[Dict]) -> str:
        """Create a prompt for the LLM."""
        conflict_type = conflict.get('type', 'unknown')
        packages = conflict.get('packages', [conflict.get('package', 'unknown')])
        message = conflict.get('message', '')
        details = conflict.get('details', {})
        
        # Get relevant dependency info
        relevant_deps = [d for d in dependencies if d['package'] in packages]
        
        prompt = f"""You are a Python dependency expert. Explain this dependency conflict clearly:

Conflict: {message}
Type: {conflict_type}
Packages involved: {', '.join(packages)}

Dependency details:
"""
        for dep in relevant_deps:
            prompt += f"- {dep['package']}: {dep['specifier'] or 'no version specified'}\n"
        
        if details:
            prompt += f"\nVersion constraints: {json.dumps(details)}\n"
        
        prompt += """
Provide a clear, concise explanation that:
1. Explains what the conflict is in simple terms
2. Explains why this conflict happens (technical reason)
3. Suggests how to fix it (specific version recommendations)

Keep it under 150 words and use plain language.
"""
        return prompt
    
    def _call_llm(self, prompt: str) -> str:
        """
        Call LLM API to generate explanation.
        Falls back to rule-based explanation if API fails.
        """
        try:
            # Try Hugging Face Inference API (free tier)
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 200,
                    "temperature": 0.7,
                    "return_full_text": False
                }
            }
            
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get('generated_text', '')
                    if generated_text:
                        return generated_text.strip()
            
            # If API fails, fall back to rule-based
            return self._fallback_explanation(prompt)
        
        except Exception as e:
            # Fall back to rule-based explanation
            return self._fallback_explanation(prompt)
    
    def _fallback_explanation(self, prompt: str) -> str:
        """Generate rule-based explanation when LLM is unavailable."""
        # Extract key info from prompt
        if "pytorch-lightning" in prompt.lower() and "torch" in prompt.lower():
            return """PyTorch Lightning 2.0+ requires PyTorch 2.0 or higher because it uses new PyTorch APIs and features that don't exist in version 1.x. The conflict happens because you're trying to use a newer version of PyTorch Lightning with an older version of PyTorch. To fix this, either upgrade PyTorch to 2.0+ or downgrade PyTorch Lightning to 1.x."""
        
        elif "fastapi" in prompt.lower() and "pydantic" in prompt.lower():
            return """FastAPI 0.78.x was built for Pydantic v1, which has a different API than Pydantic v2. The conflict occurs because Pydantic v2 introduced breaking changes that FastAPI 0.78 doesn't support. To fix this, either upgrade FastAPI to 0.99+ (which supports Pydantic v2) or downgrade Pydantic to v1.x."""
        
        elif "tensorflow" in prompt.lower() and "keras" in prompt.lower():
            return """Keras 3.0+ requires TensorFlow 2.x because it was redesigned to work with TensorFlow 2's eager execution and new features. TensorFlow 1.x uses a different execution model that Keras 3.0 doesn't support. To fix this, upgrade TensorFlow to 2.x or downgrade Keras to 2.x."""
        
        elif "duplicate" in prompt.lower():
            return """You have the same package specified multiple times with different versions. This creates ambiguity about which version should be installed. To fix this, remove duplicate entries and keep only one version specification per package."""
        
        else:
            return """This dependency conflict occurs due to incompatible version requirements between packages. Review the version constraints and ensure all packages are compatible with each other. Consider updating to compatible versions or using a dependency resolver."""
    
    def _extract_why(self, explanation: str, conflict: Dict) -> str:
        """Extract the 'why it happens' part from explanation."""
        # Simple extraction - look for sentences explaining the reason
        sentences = explanation.split('.')
        why_sentences = [s.strip() for s in sentences if any(word in s.lower() for word in ['because', 'due to', 'requires', 'needs', 'since'])]
        return '. '.join(why_sentences[:2]) + '.' if why_sentences else "Version constraints are incompatible."
    
    def _extract_fix(self, explanation: str, conflict: Dict) -> str:
        """Extract the 'how to fix' part from explanation."""
        # Simple extraction - look for fix suggestions
        sentences = explanation.split('.')
        fix_sentences = [s.strip() for s in sentences if any(word in s.lower() for word in ['upgrade', 'downgrade', 'fix', 'change', 'update', 'remove'])]
        return '. '.join(fix_sentences[:2]) + '.' if fix_sentences else "Adjust version constraints to compatible versions."


"""
Dependency Explanation Assistant
A Streamlit app that provides intelligent explanations for Python dependency conflicts.
"""

import streamlit as st
from dependency_parser import DependencyParser
from conflict_detector import ConflictDetector
from explanation_engine import ExplanationEngine


def main():
    st.set_page_config(
        page_title="Dependency Explanation Assistant",
        page_icon="🐍",
        layout="wide"
    )
    
    st.title("🐍 Dependency Explanation Assistant")
    st.markdown("""
    **Intelligent explanations for Python dependency conflicts**
    
    Upload a requirements.txt file or paste its contents to get detailed, natural language 
    explanations of any dependency conflicts, including why they happen and how to fix them.
    """)
    
    # Initialize components
    parser = DependencyParser()
    detector = ConflictDetector()
    
    # Sidebar for settings
    with st.sidebar:
        st.header("⚙️ Settings")
        use_llm = st.checkbox("Use AI Explanations", value=True, 
                              help="Uses LLM for intelligent explanations. Falls back to rule-based if unavailable.")
        st.markdown("---")
        st.markdown("### 📖 How to Use")
        st.markdown("""
        1. Upload a requirements.txt file, OR
        2. Paste requirements.txt content
        3. Click "Analyze Dependencies"
        4. Review detailed explanations for any conflicts
        """)
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📥 Input")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Upload requirements.txt",
            type=['txt'],
            help="Upload your requirements.txt file"
        )
        
        # Text input
        requirements_text = st.text_area(
            "Or paste requirements.txt content",
            height=300,
            placeholder="pandas==2.0.3\ntorch==1.8.0\npytorch-lightning==2.2.0\n...",
            help="Paste your requirements.txt content here"
        )
        
        analyze_button = st.button("🔍 Analyze Dependencies", type="primary", use_container_width=True)
    
    with col2:
        st.header("📊 Results")
        
        if analyze_button or (uploaded_file is not None and 'dependencies' not in st.session_state):
            # Get input
            input_text = ""
            
            if uploaded_file is not None:
                input_text = uploaded_file.read().decode('utf-8')
                st.session_state['uploaded_file_name'] = uploaded_file.name
            elif requirements_text:
                input_text = requirements_text
            else:
                st.warning("Please upload a file or paste requirements.txt content.")
                st.stop()
            
            # Parse dependencies
            with st.spinner("Parsing dependencies..."):
                dependencies = parser.parse_requirements_text(input_text)
                st.session_state['dependencies'] = dependencies
                st.session_state['input_text'] = input_text
            
            # Detect conflicts
            with st.spinner("Detecting conflicts..."):
                graph = detector.build_dependency_graph(dependencies)
                is_compatible, issues = detector.check_compatibility(graph)
                st.session_state['issues'] = issues
                st.session_state['is_compatible'] = is_compatible
                st.session_state['graph'] = graph
        
        # Display results
        if 'issues' in st.session_state:
            issues = st.session_state['issues']
            is_compatible = st.session_state['is_compatible']
            dependencies = st.session_state['dependencies']
            
            # Summary
            st.subheader("📋 Summary")
            if is_compatible:
                st.success(f"✅ No conflicts detected! ({len(dependencies)} packages analyzed)")
            else:
                st.error(f"⚠️ {len(issues)} conflict(s) found in {len(dependencies)} packages")
            
            # Detailed explanations
            if issues:
                st.subheader("🔍 Detailed Explanations")
                
                # Initialize explanation engine
                engine = ExplanationEngine(use_local_llm=use_llm)
                
                for i, issue in enumerate(issues, 1):
                    with st.expander(f"Conflict #{i}: {issue.get('packages', [issue.get('package', 'Unknown')])[0] if issue.get('packages') else issue.get('package', 'Unknown')}", expanded=True):
                        # Generate explanation
                        with st.spinner("Generating explanation..."):
                            explanation = engine.generate_explanation(issue, dependencies)
                        
                        # Display explanation
                        st.markdown(f"**Conflict:** {explanation['summary']}")
                        
                        st.markdown("**📖 Explanation:**")
                        st.info(explanation['explanation'])
                        
                        col_why, col_fix = st.columns(2)
                        
                        with col_why:
                            st.markdown("**❓ Why this happens:**")
                            st.warning(explanation['why_it_happens'])
                        
                        with col_fix:
                            st.markdown("**🔧 How to fix:**")
                            st.success(explanation['how_to_fix'])
                        
                        # Severity badge
                        severity = explanation['severity']
                        if severity == 'high':
                            st.error(f"Severity: {severity.upper()}")
                        elif severity == 'medium':
                            st.warning(f"Severity: {severity.upper()}")
                        else:
                            st.info(f"Severity: {severity.upper()}")
            
            # Show all dependencies
            with st.expander("📦 All Dependencies"):
                for dep in dependencies:
                    status = "❌" if dep.get('conflict') else "✅"
                    st.text(f"{status} {dep['original']}")
        
        else:
            st.info("👈 Upload a requirements.txt file or paste content to get started.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray;'>
        <small>Dependency Explanation Assistant | Built with Streamlit</small>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()


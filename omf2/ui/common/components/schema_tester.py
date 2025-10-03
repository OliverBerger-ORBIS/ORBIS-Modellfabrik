"""
Schema Tester Component
Handles systematic schema testing and validation
"""

import json
import streamlit as st
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Tuple
from omf2.registry.manager.registry_manager import get_registry_manager
from omf2.common.logger import get_logger

logger = get_logger(__name__)


class SchemaTester:
    def __init__(self, registry_manager):
        self.registry_manager = registry_manager
    
    def run_schema_test(self) -> Dict[str, Any]:
        """Runs comprehensive schema test on all topics"""
        all_topics = self.registry_manager.get_topics()
        test_results = []
        
        valid_count = 0
        invalid_count = 0
        no_schema_count = 0
        
        for topic in all_topics:
            result = self._test_single_topic(topic)
            test_results.append(result)
            
            if result['status'] == 'VALID':
                valid_count += 1
            elif result['status'] == 'NO_SCHEMA':
                no_schema_count += 1
            else:
                invalid_count += 1
        
        total = len(all_topics)
        return {
            'total_topics': total,
            'valid_count': valid_count,
            'invalid_count': invalid_count,
            'no_schema_count': no_schema_count,
            'valid_percentage': (valid_count / total) * 100 if total > 0 else 0,
            'invalid_percentage': (invalid_count / total) * 100 if total > 0 else 0,
            'no_schema_percentage': (no_schema_count / total) * 100 if total > 0 else 0,
            'results': test_results
        }
    
    def _test_single_topic(self, topic: str) -> Dict[str, Any]:
        """Tests a single topic for schema compliance"""
        try:
            # Get schema for topic
            topic_schema = self.registry_manager.get_topic_schema(topic)
            
            if not topic_schema:
                return {
                    'topic': topic,
                    'status': 'NO_SCHEMA',
                    'error': 'No schema found',
                    'schema_file': None
                }
            
            # Generate test payload
            from omf2.ui.common.components.payload_generator import PayloadGenerator
            generator = PayloadGenerator(self.registry_manager)
            payload = generator.generate_example_payload(topic)
            
            if not payload:
                return {
                    'topic': topic,
                    'status': 'ERROR',
                    'error': 'Failed to generate payload',
                    'schema_file': topic_schema.get('$id', 'unknown') if isinstance(topic_schema, dict) else str(topic_schema)
                }
            
            # Validate payload
            validation_result = self.registry_manager.validate_topic_payload(topic, payload)
            
            # Get schema file info from validation result
            schema_file = validation_result.get('schema_file', 'unknown')
            if not schema_file or schema_file == 'unknown':
                # Fallback to schema info
                if isinstance(topic_schema, dict):
                    schema_file = topic_schema.get('$id', topic_schema.get('title', 'unknown'))
                else:
                    schema_file = str(topic_schema)
            
            if validation_result.get('valid', False):
                return {
                    'topic': topic,
                    'status': 'VALID',
                    'error': None,
                    'schema_file': schema_file,
                    'payload': payload
                }
            else:
                return {
                    'topic': topic,
                    'status': 'INVALID',
                    'error': validation_result.get('error', 'Validation failed'),
                    'schema_file': schema_file,
                    'payload': payload,
                    'validation_errors': validation_result.get('errors', [])
                }
                
        except Exception as e:
            return {
                'topic': topic,
                'status': 'ERROR',
                'error': str(e),
                'schema_file': None
            }
    
    def render_test_ui(self):
        """Renders the schema test UI"""
        st.markdown("#### 🧪 Schema Test Mode")
        st.markdown("Systematically test all topics for payload generation and schema validation")
        
        if st.button("🚀 Run Schema Test", key="run_schema_test"):
            with st.spinner("Running comprehensive schema test..."):
                test_results = self.run_schema_test()
                st.session_state.schema_test_results = test_results
        
        if 'schema_test_results' in st.session_state:
            self._render_test_results(st.session_state.schema_test_results)
    
    def _render_test_results(self, test_results: Dict[str, Any]):
        """Renders the test results"""
        # Summary metrics
        st.markdown("#### 📊 Test Summary")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Topics", test_results['total_topics'])
        with col2:
            st.metric("✅ Valid", test_results['valid_count'], delta=f"{test_results['valid_percentage']:.1f}%")
        with col3:
            st.metric("❌ Invalid", test_results['invalid_count'], delta=f"{test_results['invalid_percentage']:.1f}%")
        with col4:
            st.metric("⚠️ No Schema", test_results['no_schema_count'], delta=f"{test_results['no_schema_percentage']:.1f}%")
        
        # Detailed results
        st.markdown("#### 📋 Detailed Results")
        
        # Filter options
        filter_option = st.radio(
            "Filter Results:",
            ["All", "Valid Only", "Invalid Only", "No Schema", "Errors Only"],
            key="test_filter_radio",
            horizontal=True
        )
        
        # Filter results
        filtered_results = test_results['results']
        if filter_option == "Valid Only":
            filtered_results = [r for r in test_results['results'] if r['status'] == 'VALID']
        elif filter_option == "Invalid Only":
            filtered_results = [r for r in test_results['results'] if r['status'] == 'INVALID']
        elif filter_option == "No Schema":
            filtered_results = [r for r in test_results['results'] if r['status'] == 'NO_SCHEMA']
        elif filter_option == "Errors Only":
            filtered_results = [r for r in test_results['results'] if r['status'] == 'ERROR']
        
        # Display results
        for result in filtered_results:
            with st.expander(f"{'✅' if result['status'] == 'VALID' else '❌' if result['status'] == 'INVALID' else '⚠️'} {result['topic']}"):
                st.write(f"**Status:** {result['status']}")
                if result['error']:
                    st.write(f"**Error:** {result['error']}")
                if result['schema_file']:
                    st.write(f"**Schema:** {result['schema_file']}")
                if result['status'] == 'INVALID' and 'validation_errors' in result:
                    st.write("**Validation Errors:**")
                    for error in result['validation_errors']:
                        st.text(f"  - {error}")
        
        # Export results
        st.markdown("#### 💾 Export Test Results")
        
        # Directory selection
        export_dir = st.text_input(
            "Export Directory:",
            value="data/omf-data/schema_test_results",
            help="Directory where test results will be saved (default: data/omf-data/schema_test_results)",
            key="export_dir_input"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📁 Export Test Results", key="export_test_results"):
                self._export_test_results(test_results, export_dir)
        
        with col2:
            if st.button("📥 Download Test Results", key="download_test_results"):
                import io
                json_str = json.dumps(test_results, indent=2)
                st.download_button(
                    label="Download Test Results",
                    data=json_str,
                    file_name="schema_test_results.json",
                    mime="application/json"
                )
    
    def _export_test_results(self, test_results: Dict[str, Any], export_dir: str):
        """Export test results to specified directory with timestamp"""
        try:
            # Create timestamp for filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"schema_test_results_{timestamp}.json"
            
            # Ensure export directory exists
            export_path = Path(export_dir)
            export_path.mkdir(parents=True, exist_ok=True)
            
            # Full file path
            file_path = export_path / filename
            
            # Add metadata to test results
            export_data = {
                'metadata': {
                    'export_timestamp': datetime.now().isoformat(),
                    'export_directory': str(export_path),
                    'filename': filename,
                    'total_topics': test_results['total_topics'],
                    'valid_count': test_results['valid_count'],
                    'invalid_count': test_results['invalid_count'],
                    'no_schema_count': test_results['no_schema_count']
                },
                'test_results': test_results
            }
            
            # Write JSON file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            # Success message
            st.success(f"✅ Test results exported successfully!")
            st.info(f"📁 File saved: {file_path}")
            st.info(f"📊 Summary: {test_results['valid_count']}/{test_results['total_topics']} topics valid ({test_results['valid_percentage']:.1f}%)")
            
            # Show file info
            file_size = file_path.stat().st_size
            st.info(f"📏 File size: {file_size:,} bytes")
            
            logger.info(f"📁 Schema test results exported to: {file_path}")
            
        except Exception as e:
            st.error(f"❌ Failed to export test results: {e}")
            logger.error(f"❌ Export failed: {e}")

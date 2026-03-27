"""
debug_mobile_table.py
Debug why mobile and table are not working
"""
import sys
import os

# Add Backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dual_pipeline_analyzer import DualPipelineAnalyzer

def debug_specific_cases():
    """Debug specific problematic cases."""
    analyzer = DualPipelineAnalyzer()
    
    # Debug mobile
    print("DEBUG: mobile")
    query = "mobile"
    print(f"Query: '{query}'")
    
    # Check special mappings
    special_mappings = {
        "mobile": "smartphone",
        "cell": "smartphone", 
        "cellphone": "smartphone",
        "table": "furniture"
    }
    
    print(f"Special mappings for mobile: {special_mappings.get('mobile')}")
    print(f"Mobile in special_mappings: {'mobile' in special_mappings}")
    print(f"Query contains 'mobile': {'mobile' in query}")
    
    # Check if mapping should trigger
    should_trigger = special_mappings.get('mobile') in query or query in special_mappings.get('mobile', '')
    print(f"Should trigger mapping: {should_trigger}")
    
    # Test actual generation
    components = analyzer.generate_components(query)
    print(f"Actual result: {components}")
    print()
    
    # Debug table
    print("DEBUG: table")
    query = "table"
    print(f"Query: '{query}'")
    
    print(f"Special mappings for table: {special_mappings.get('table')}")
    print(f"Table in special_mappings: {'table' in special_mappings}")
    print(f"Query contains 'table': {'table' in query}")
    
    # Check if mapping should trigger
    should_trigger = special_mappings.get('table') in query or query in special_mappings.get('table', '')
    print(f"Should trigger mapping: {should_trigger}")
    
    # Test actual generation
    components = analyzer.generate_components(query)
    print(f"Actual result: {components}")

if __name__ == "__main__":
    debug_specific_cases()

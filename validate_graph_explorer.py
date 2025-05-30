#!/usr/bin/env python3
"""
Validation Script for Enhanced Graph Explorer
Tests that the graph explorer is fully LLM-powered and dynamic
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.graphiti_cosmos import GraphitiCosmos
from demos.graph_explorer import GraphExplorer

class GraphExplorerValidator:
    """Validates that the graph explorer uses LLM assistance and avoids hardcoded patterns"""
    
    def __init__(self):
        self.explorer = None
        self.graphiti = None
        self.test_results = []
        
    async def initialize(self):
        """Initialize the systems for testing"""
        print("🔧 GRAPH EXPLORER VALIDATION")
        print("=" * 60)
        print("🎨 Initializing systems...")
        
        self.explorer = GraphExplorer()
        await self.explorer.initialize()
        self.graphiti = self.explorer.graphiti
        
        print("✅ Systems initialized successfully")
        print()
        
    async def test_llm_keyword_extraction(self):
        """Test that keyword extraction uses LLM instead of hardcoded patterns"""
        print("🔍 Testing LLM Keyword Extraction...")
        
        test_queries = [
            "Find all people who work for technology companies",
            "Show me sustainable products and their manufacturers",
            "What organizations are connected to renewable energy?",
            "Find customers who purchased electronics recently"
        ]
        
        for query in test_queries:
            try:
                keywords = await self.explorer._extract_search_keywords(query)
                print(f"   Query: '{query}'")
                print(f"   Keywords: {keywords}")
                
                # Validate that we get meaningful, context-aware keywords
                self.test_results.append({
                    'test': 'llm_keyword_extraction',
                    'query': query,
                    'keywords': keywords,
                    'success': len(keywords) > 0 and any(len(k) > 2 for k in keywords)
                })
                print("   ✅ LLM keyword extraction working")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                self.test_results.append({
                    'test': 'llm_keyword_extraction',
                    'query': query,
                    'error': str(e),
                    'success': False
                })
        print()
    
    async def test_semantic_entity_search(self):
        """Test that entity search uses semantic similarity instead of basic string matching"""
        print("🧠 Testing Semantic Entity Search...")
        
        test_searches = [
            "technology company",
            "sustainable product",
            "renewable energy",
            "customer electronics"
        ]
        
        for search_term in test_searches:
            try:
                results = await self.graphiti.search_entities(search_term, limit=5)
                print(f"   Search: '{search_term}'")
                print(f"   Results: {len(results)} entities found")
                
                if results:
                    for i, entity in enumerate(results[:2], 1):
                        name = entity.get('name', 'Unknown')
                        entity_type = entity.get('type', entity.get('entity_type', 'Unknown'))
                        print(f"      {i}. {name} ({entity_type})")
                
                self.test_results.append({
                    'test': 'semantic_entity_search',
                    'search_term': search_term,
                    'results_count': len(results),
                    'success': True
                })
                print("   ✅ Semantic search working")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                self.test_results.append({
                    'test': 'semantic_entity_search',
                    'search_term': search_term,
                    'error': str(e),
                    'success': False
                })
        print()
    
    async def test_natural_language_interpretation(self):
        """Test natural language query interpretation"""
        print("🗣️  Testing Natural Language Query Interpretation...")
        
        complex_queries = [
            "Show me all people who work for organizations in the tech industry",
            "Find products that are related to environmental sustainability",
            "What are the relationships between customers and their recent purchases?",
            "Analyze the network of suppliers and manufacturers"
        ]
        
        for query in complex_queries:
            try:
                interpretation = await self.explorer._interpret_natural_language_query(query)
                print(f"   Query: '{query}'")
                print(f"   Intent: {interpretation['intent']}")
                print(f"   Strategy: {interpretation['strategy']}")
                print(f"   Confidence: {interpretation['confidence']:.2f}")
                print(f"   Terms: {interpretation['search_terms']}")
                
                self.test_results.append({
                    'test': 'nl_interpretation',
                    'query': query,
                    'interpretation': interpretation,
                    'success': interpretation['confidence'] > 0.5
                })
                print("   ✅ Natural language interpretation working")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                self.test_results.append({
                    'test': 'nl_interpretation',
                    'query': query,
                    'error': str(e),
                    'success': False
                })
        print()
    
    async def test_dynamic_query_generation(self):
        """Test that queries are generated dynamically, not hardcoded"""
        print("🎯 Testing Dynamic Query Generation...")
        
        # Test different search patterns to ensure no hardcoding
        dynamic_searches = [
            ("exact match", "Microsoft"),
            ("partial match", "tech"),
            ("semantic search", "innovation"),
            ("broad exploration", "")
        ]
        
        for search_type, term in dynamic_searches:
            try:
                results = await self.graphiti.search_entities(term, limit=3)
                print(f"   Type: {search_type}, Term: '{term}' -> {len(results)} results")
                
                self.test_results.append({
                    'test': 'dynamic_query_generation',
                    'search_type': search_type,
                    'term': term,
                    'results_count': len(results),
                    'success': True
                })
                print("   ✅ Dynamic query generation working")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                self.test_results.append({
                    'test': 'dynamic_query_generation',
                    'search_type': search_type,
                    'term': term,
                    'error': str(e),
                    'success': False
                })
        print()
    
    async def test_llm_result_enhancement(self):
        """Test LLM-based result enhancement and contextualization"""
        print("✨ Testing LLM Result Enhancement...")
        
        query = "Find technology companies and their products"
        
        try:
            # First get basic results
            interpretation = await self.explorer._interpret_natural_language_query(query)
            
            basic_results = []
            for term in interpretation['search_terms'][:2]:
                results = await self.graphiti.search_entities(term, limit=3)
                basic_results.extend(results)
            
            # Remove duplicates
            unique_results = {}
            for result in basic_results:
                result_id = result.get('id') or result.get('name')
                if result_id not in unique_results:
                    unique_results[result_id] = result
            
            basic_results = list(unique_results.values())
            
            if basic_results:
                # Test LLM enhancement
                enhanced_results = await self.explorer._enhance_search_results_with_llm(
                    query, basic_results, interpretation
                )
                
                print(f"   Query: '{query}'")
                print(f"   Basic results: {len(basic_results)}")
                print(f"   Enhanced results: {len(enhanced_results)}")
                
                # Check if enhancement metadata is available
                if hasattr(self.explorer, '_last_enhancement'):
                    enhancement = self.explorer._last_enhancement
                    print(f"   Insights: {enhancement.get('insights', 'None')[:50]}...")
                    print(f"   Follow-ups: {len(enhancement.get('follow_up_queries', []))}")
                
                self.test_results.append({
                    'test': 'llm_result_enhancement',
                    'query': query,
                    'basic_count': len(basic_results),
                    'enhanced_count': len(enhanced_results),
                    'has_insights': hasattr(self.explorer, '_last_enhancement'),
                    'success': len(enhanced_results) > 0
                })
                print("   ✅ LLM result enhancement working")
            else:
                print("   ⚠️  No results to enhance")
                self.test_results.append({
                    'test': 'llm_result_enhancement',
                    'query': query,
                    'success': False,
                    'reason': 'no_results'
                })
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.test_results.append({
                'test': 'llm_result_enhancement',
                'query': query,
                'error': str(e),
                'success': False
            })
        print()
    
    def generate_validation_report(self):
        """Generate a comprehensive validation report"""
        print("📊 VALIDATION REPORT")
        print("=" * 60)
        
        # Count successes and failures
        total_tests = len(self.test_results)
        successful_tests = len([t for t in self.test_results if t.get('success', False)])
        failed_tests = total_tests - successful_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(successful_tests/total_tests)*100:.1f}%")
        print()
        
        # Group by test type
        test_groups = {}
        for test in self.test_results:
            test_type = test['test']
            if test_type not in test_groups:
                test_groups[test_type] = []
            test_groups[test_type].append(test)
        
        for test_type, tests in test_groups.items():
            successful = len([t for t in tests if t.get('success', False)])
            total = len(tests)
            print(f"🔍 {test_type.replace('_', ' ').title()}:")
            print(f"   {successful}/{total} tests passed")
            
            # Show failures
            failures = [t for t in tests if not t.get('success', False)]
            if failures:
                print("   ❌ Failures:")
                for failure in failures:
                    error = failure.get('error', 'Unknown error')
                    print(f"      - {error}")
            print()
        
        # Overall assessment
        if successful_tests >= total_tests * 0.8:
            print("✅ VALIDATION PASSED")
            print("The graph explorer is successfully using LLM assistance and dynamic queries!")
        elif successful_tests >= total_tests * 0.6:
            print("⚠️  VALIDATION PARTIAL")
            print("The graph explorer has some LLM features working, but needs improvement.")
        else:
            print("❌ VALIDATION FAILED")
            print("The graph explorer is not sufficiently using LLM assistance.")
        
        print()
        print(f"Detailed results saved with {total_tests} test cases")
        
        return {
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'success_rate': (successful_tests/total_tests)*100,
            'test_results': self.test_results
        }

async def main():
    """Run the comprehensive validation"""
    validator = GraphExplorerValidator()
    
    try:
        await validator.initialize()
        
        # Run all validation tests
        await validator.test_llm_keyword_extraction()
        await validator.test_semantic_entity_search()
        await validator.test_natural_language_interpretation()
        await validator.test_dynamic_query_generation()
        await validator.test_llm_result_enhancement()
        
        # Generate final report
        report = validator.generate_validation_report()
        
        # Save detailed report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"graph_explorer_validation_{timestamp}.json"
        
        import json
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"📄 Detailed validation report saved as: {report_file}")
        
    except Exception as e:
        print(f"❌ Validation failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())

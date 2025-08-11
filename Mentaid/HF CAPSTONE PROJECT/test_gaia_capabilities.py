"""
GAIA Enhanced Agent - Comprehensive Capability Testing
Tests all multimodal capabilities for GAIA benchmark performance
"""

import sys
import os
import time
import traceback
from gaia_enhanced_agent import GAIAEnhancedAgent

def test_video_processing():
    """Test YouTube video processing capabilities"""
    print("\n" + "="*50)
    print("TESTING VIDEO PROCESSING")
    print("="*50)
    
    test_cases = [
        {
            "name": "Bird Species Counting",
            "question": "In the video https://www.youtube.com/watch?v=L1vXCYZAYYM, what is the highest number of bird species to be on camera simultaneously?",
            "expected_tools": ["extract_youtube_transcript", "analyze_youtube_video_metadata"]
        },
        {
            "name": "Video Quote Extraction", 
            "question": "Examine the video at https://www.youtube.com/watch?v=1htKBjuUWec. What does Teal'c say in response to the question 'Isn't that hot?'",
            "expected_tools": ["extract_youtube_transcript"]
        }
    ]
    
    return run_test_cases("Video Processing", test_cases)

def test_file_processing():
    """Test file processing capabilities"""
    print("\n" + "="*50)
    print("TESTING FILE PROCESSING")
    print("="*50)
    
    test_cases = [
        {
            "name": "PDB Protein Analysis",
            "question": "Using the Biopython library in Python, parse the PDB file of the protein identified by the PDB ID 5wb7 from the RCSB Protein Data Bank. Calculate the distance between the first and second atoms as they are listed in the PDB file.",
            "expected_tools": ["process_pdb_protein_file"]
        },
        {
            "name": "Excel File Analysis",
            "question": "The attached spreadsheet shows the inventory for a movie and video game rental store. What is the title of the oldest Blu-Ray recorded in this spreadsheet?",
            "expected_tools": ["process_excel_file_advanced"]
        }
    ]
    
    return run_test_cases("File Processing", test_cases)

def test_text_processing():
    """Test text processing and manipulation"""
    print("\n" + "="*50)
    print("TESTING TEXT PROCESSING")
    print("="*50)
    
    test_cases = [
        {
            "name": "Reversed Text Analysis",
            "question": ".rewsna eht sa \"tfel\" drow eht fo etisoppo eht etirw ,ecnetnes siht dnatsrednu uoy fI",
            "expected_tools": ["reverse_text_analysis"]
        },
        {
            "name": "Pattern Extraction",
            "question": "Extract all numbers and dates from this text: 'The study was conducted from 2020-01-15 to 2020-12-31 with 1,234 participants aged 25-65 years.'",
            "expected_tools": ["extract_numbers_and_patterns"]
        }
    ]
    
    return run_test_cases("Text Processing", test_cases)

def test_mathematical_computation():
    """Test mathematical and computational capabilities"""
    print("\n" + "="*50)
    print("TESTING MATHEMATICAL COMPUTATION")
    print("="*50)
    
    test_cases = [
        {
            "name": "Complex Calculation",
            "question": "If Eliud Kipchoge could maintain his record-making marathon pace indefinitely, how many thousand hours would it take him to run the distance between the Earth and the Moon at its closest approach?",
            "expected_tools": ["advanced_calculator", "enhanced_web_search"]
        },
        {
            "name": "Statistical Analysis",
            "question": "Calculate the mean, median, and standard deviation of the following numbers: [24, 74, 28, 54, 73, 33, 64, 73, 60, 53]",
            "expected_tools": ["advanced_calculator", "execute_python_code"]
        }
    ]
    
    return run_test_cases("Mathematical Computation", test_cases)

def test_research_capabilities():
    """Test research and web scraping capabilities"""
    print("\n" + "="*50)
    print("TESTING RESEARCH CAPABILITIES")
    print("="*50)
    
    test_cases = [
        {
            "name": "Wikipedia Research",
            "question": "How many studio albums were published by Mercedes Sosa between 2000 and 2009 (included)?",
            "expected_tools": ["wiki_search", "enhanced_web_search"]
        },
        {
            "name": "ArXiv Paper Search",
            "question": "Find papers about AI regulation submitted to arXiv in June 2022 that show figures with three axes.",
            "expected_tools": ["search_arxiv_papers"]
        },
        {
            "name": "GitHub Repository Search",
            "question": "Search for NumPy polynomial issues with regression labels on GitHub.",
            "expected_tools": ["search_github_repositories", "search_github_issues"]
        }
    ]
    
    return run_test_cases("Research Capabilities", test_cases)

def test_web_scraping():
    """Test web scraping capabilities"""
    print("\n" + "="*50)
    print("TESTING WEB SCRAPING")
    print("="*50)
    
    test_cases = [
        {
            "name": "Webpage Content Extraction",
            "question": "Scrape the content from https://en.wikipedia.org/wiki/Artificial_intelligence and extract the main topics discussed.",
            "expected_tools": ["scrape_webpage_content"]
        }
    ]
    
    return run_test_cases("Web Scraping", test_cases)

def run_test_cases(category, test_cases):
    """Run a set of test cases"""
    results = []
    
    try:
        agent = GAIAEnhancedAgent()
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\nTest {i}: {test_case['name']}")
            print(f"Question: {test_case['question'][:100]}...")
            print("-" * 50)
            
            try:
                start_time = time.time()
                response = agent.process_question(test_case['question'])
                end_time = time.time()
                
                duration = end_time - start_time
                
                print(f"✅ Response received in {duration:.1f}s")
                print(f"Response length: {len(response)} characters")
                print(f"Response preview: {response[:200]}...")
                
                # Check if response contains expected information
                success = len(response) > 50 and "error" not in response.lower()
                results.append({
                    'test': test_case['name'],
                    'success': success,
                    'duration': duration,
                    'response_length': len(response)
                })
                
                if success:
                    print("✅ Test PASSED")
                else:
                    print("❌ Test FAILED")
                
            except Exception as e:
                print(f"❌ Test FAILED with error: {e}")
                results.append({
                    'test': test_case['name'],
                    'success': False,
                    'duration': 0,
                    'error': str(e)
                })
            
            # Add delay between tests
            if i < len(test_cases):
                print("Waiting 3 seconds before next test...")
                time.sleep(3)
    
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        return []
    
    return results

def run_comprehensive_test():
    """Run comprehensive test of all capabilities"""
    print("🚀 GAIA Enhanced Agent - Comprehensive Capability Testing")
    print("="*70)
    
    all_results = []
    
    # Run all test categories
    test_functions = [
        test_mathematical_computation,  # Start with simpler tests
        test_text_processing,
        test_research_capabilities,
        test_web_scraping,
        test_file_processing,
        test_video_processing,  # Most complex tests last
    ]
    
    for test_func in test_functions:
        try:
            results = test_func()
            all_results.extend(results)
        except Exception as e:
            print(f"❌ Test category failed: {e}")
            traceback.print_exc()
        
        # Add delay between test categories
        print("\nWaiting 5 seconds before next test category...")
        time.sleep(5)
    
    # Generate summary report
    print("\n" + "="*70)
    print("COMPREHENSIVE TEST SUMMARY")
    print("="*70)
    
    if all_results:
        total_tests = len(all_results)
        successful_tests = sum(1 for r in all_results if r['success'])
        success_rate = (successful_tests / total_tests) * 100
        
        print(f"Total tests run: {total_tests}")
        print(f"Successful tests: {successful_tests}")
        print(f"Success rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 EXCELLENT! Agent is ready for GAIA benchmark.")
        elif success_rate >= 60:
            print("✅ GOOD! Agent should perform well on GAIA benchmark.")
        elif success_rate >= 40:
            print("⚠️  FAIR! Agent may need some improvements.")
        else:
            print("❌ POOR! Agent needs significant improvements.")
        
        # Detailed results
        print("\nDetailed Results:")
        for result in all_results:
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            duration = result.get('duration', 0)
            print(f"{status} {result['test']} ({duration:.1f}s)")
            if 'error' in result:
                print(f"    Error: {result['error']}")
    
    else:
        print("❌ No tests completed successfully.")
    
    return all_results

def quick_functionality_test():
    """Quick test of basic functionality"""
    print("🔧 Quick Functionality Test")
    print("="*30)
    
    try:
        agent = GAIAEnhancedAgent()
        
        # Simple test question
        test_question = "What is 2 + 2?"
        print(f"Test question: {test_question}")
        
        response = agent.process_question(test_question)
        print(f"Response: {response}")
        
        if "4" in response:
            print("✅ Basic functionality working!")
            return True
        else:
            print("❌ Basic functionality not working properly.")
            return False
            
    except Exception as e:
        print(f"❌ Quick test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Main testing function"""
    print("Choose testing mode:")
    print("1. Quick functionality test (30 seconds)")
    print("2. Comprehensive capability test (10-15 minutes)")
    print("3. Both")
    
    choice = input("Enter choice (1/2/3): ").strip()
    
    if choice in ['1', '3']:
        print("\n" + "="*50)
        print("RUNNING QUICK TEST")
        print("="*50)
        quick_success = quick_functionality_test()
        
        if not quick_success and choice == '3':
            print("❌ Quick test failed. Skipping comprehensive test.")
            return
    
    if choice in ['2', '3']:
        print("\n" + "="*50)
        print("RUNNING COMPREHENSIVE TEST")
        print("="*50)
        run_comprehensive_test()

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Test Suite for Simplified Tech Stack Audit Tool
Tests the complete end-to-end workflow
"""

import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

load_dotenv()

from simple_audit import TechStackAudit
from core.csv_loader import load_input, convert_df_to_tool_inventory


def test_csv_loading():
    """Test 1: CSV Loading"""
    print("\n" + "="*60)
    print("TEST 1: CSV Loading")
    print("="*60)
    
    # Check for test CSV files
    csv_files = [
        "data/cga_real_tools.csv",
        "data/tech_stack_list-CGA-Test.csv"
    ]
    
    found_files = []
    for csv_path in csv_files:
        if Path(csv_path).exists():
            found_files.append(csv_path)
            print(f"✅ Found: {csv_path}")
    
    if not found_files:
        print("❌ No test CSV files found!")
        return False, None
    
    # Test loading first file
    test_csv = found_files[0]
    print(f"\n📂 Testing load: {test_csv}")
    
    try:
        df = load_input(test_csv)
        print(f"✅ Loaded DataFrame: {len(df)} rows")
        
        tool_inventory = convert_df_to_tool_inventory(df)
        print(f"✅ Converted to inventory: {len(tool_inventory)} tools")
        
        # Show first 3 tools
        print("\n📋 Sample tools:")
        for i, (tool_name, tool_data) in enumerate(list(tool_inventory.items())[:3]):
            print(f"   {i+1}. {tool_name}")
            print(f"      Category: {tool_data['category']}")
            print(f"      Criticality: {tool_data['criticality']}")
        
        print("\n✅ TEST 1 PASSED\n")
        return True, test_csv
        
    except Exception as e:
        print(f"❌ TEST 1 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False, None


async def test_quick_research():
    """Test 2: Quick research on 2 tools"""
    print("\n" + "="*60)
    print("TEST 2: Quick Research (2 tools)")
    print("="*60)
    
    # Find CSV
    csv_path = "data/cga_real_tools.csv"
    if not Path(csv_path).exists():
        csv_path = "data/tech_stack_list-CGA-Test.csv"
    
    if not Path(csv_path).exists():
        print("⚠️  No CSV file found, skipping research test")
        return True
    
    print(f"📂 Using: {csv_path}")
    
    try:
        audit = TechStackAudit(research_window_years=2)
        
        # Load just first 2 tools for quick test
        df = load_input(csv_path)
        df_small = df.head(2)
        
        # Save temporary CSV
        temp_csv = Path("data/temp_test.csv")
        df_small.to_csv(temp_csv, index=False)
        
        print(f"\n🔬 Testing research on 2 tools...")
        print(f"   Tools: {', '.join(df_small['Tool Name'].tolist())}")
        
        # Run research phase only (not full audit)
        enriched_tools = await audit._research_phase(
            str(temp_csv), 
            research_depth="quick"
        )
        
        print(f"\n✅ Research complete: {len(enriched_tools)} tools")
        
        for tool in enriched_tools:
            print(f"\n   📦 {tool['name']}")
            print(f"      Type: {tool['type']}")
            print(f"      Updates: {tool['update_count']}")
            if tool.get('research_result', {}).get('success'):
                print(f"      Status: ✅ Success")
            else:
                print(f"      Status: ⚠️  {tool.get('research_result', {}).get('error', 'Unknown')}")
        
        # Cleanup
        temp_csv.unlink()
        
        print("\n✅ TEST 2 PASSED\n")
        return True
        
    except Exception as e:
        print(f"❌ TEST 2 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_integration_analysis():
    """Test 3: Integration analysis"""
    print("\n" + "="*60)
    print("TEST 3: Integration Analysis")
    print("="*60)
    
    from core.integration_analyzer import IntegrationAnalyzer
    
    # Create mock enriched tools
    mock_tools = [
        {
            'name': 'Redtail CRM',
            'type': 'crm',
            'category': 'CRM',
            'users': ['Advisors'],
            'criticality': 'High',
            'research_result': {'success': True, 'has_api': True},
            'analyzed_updates': [
                {
                    'feature_name': 'API v2.0',
                    'automation_potential': 'high',
                    'automation_value': 'Enable real-time data sync'
                }
            ],
            'update_count': 1
        },
        {
            'name': 'Microsoft 365',
            'type': 'productivity_suite',
            'category': 'Productivity',
            'users': ['All'],
            'criticality': 'High',
            'research_result': {'success': True, 'has_api': True},
            'analyzed_updates': [
                {
                    'feature_name': 'Power Automate',
                    'automation_potential': 'high',
                    'automation_value': 'Workflow automation'
                }
            ],
            'update_count': 1
        }
    ]
    
    try:
        print("🤖 Running integration analysis...")
        
        analyzer = IntegrationAnalyzer()
        opportunities = await analyzer.analyze_stack(
            enriched_tools=mock_tools,
            client_name="Test Client"
        )
        
        print(f"\n✅ Analysis complete: {len(opportunities)} opportunity set(s) found")
        
        print("\n✅ TEST 3 PASSED\n")
        return True
        
    except Exception as e:
        print(f"❌ TEST 3 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_report_generation():
    """Test 4: Report generation"""
    print("\n" + "="*60)
    print("TEST 4: Report Generation")
    print("="*60)
    
    from core.report_writer import ReportWriter
    
    # Create mock data
    mock_tools = [
        {
            'name': 'Test Tool 1',
            'type': 'crm',
            'category': 'CRM',
            'users': ['Sales'],
            'criticality': 'High',
            'research_result': {'success': True},
            'analyzed_updates': [
                {
                    'feature_name': 'API Enhancement',
                    'automation_potential': 'high',
                    'business_impact': 'Faster data sync'
                }
            ],
            'update_count': 1
        }
    ]
    
    mock_opportunities = [
        {
            'raw_analysis': 'Test opportunity: Automate data sync between systems using n8n HTTP nodes.'
        }
    ]
    
    try:
        print("📝 Generating test report...")
        
        writer = ReportWriter()
        report_path = await writer.generate_report(
            enriched_tools=mock_tools,
            opportunities=mock_opportunities,
            client_name="Test Client"
        )
        
        print(f"\n✅ Report generated: {report_path}")
        
        # Verify file exists
        if Path(report_path).exists():
            file_size = Path(report_path).stat().st_size
            print(f"   File size: {file_size} bytes")
            print("   ✅ Report file created successfully")
        else:
            print("   ❌ Report file not found!")
            return False
        
        print("\n✅ TEST 4 PASSED\n")
        return True
        
    except Exception as e:
        print(f"❌ TEST 4 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_complete_workflow():
    """Test 5: Complete end-to-end workflow"""
    print("\n" + "="*60)
    print("TEST 5: Complete Workflow (3 tools)")
    print("="*60)
    
    # Find CSV
    csv_path = "data/cga_real_tools.csv"
    if not Path(csv_path).exists():
        csv_path = "data/tech_stack_list-CGA-Test.csv"
    
    if not Path(csv_path).exists():
        print("⚠️  No CSV file found, skipping complete workflow test")
        return True
    
    try:
        # Create small test CSV (3 tools)
        df = load_input(csv_path)
        df_small = df.head(3)
        
        temp_csv = Path("data/temp_complete_test.csv")
        df_small.to_csv(temp_csv, index=False)
        
        print(f"📂 Running complete audit on 3 tools:")
        for tool_name in df_small['Tool Name'].tolist():
            print(f"   - {tool_name}")
        
        # Run complete audit
        audit = TechStackAudit(research_window_years=2)
        report_path = await audit.run_audit(
            csv_path=str(temp_csv),
            client_name="Complete Test Client",
            research_depth="quick"
        )
        
        print(f"\n✅ Complete workflow finished!")
        print(f"   Report: {report_path}")
        
        # Verify report
        if Path(report_path).exists():
            print("   ✅ Report file created")
        else:
            print("   ❌ Report file missing!")
            return False
        
        # Cleanup
        temp_csv.unlink()
        
        print("\n✅ TEST 5 PASSED\n")
        return True
        
    except Exception as e:
        print(f"❌ TEST 5 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def run_all_tests():
    """Run complete test suite"""
    print("\n" + "="*60)
    print("🧪 SIMPLIFIED AUDIT TOOL - TEST SUITE")
    print("="*60)
    print("\nThis will test:")
    print("  1. CSV Loading")
    print("  2. Quick Research (2 tools)")
    print("  3. Integration Analysis")
    print("  4. Report Generation")
    print("  5. Complete Workflow (3 tools)")
    print("\n" + "="*60)
    
    results = {}
    
    try:
        # Test 1: CSV Loading (sync)
        results['csv_loading'], test_csv = test_csv_loading()
        
        # Test 2: Quick Research
        results['quick_research'] = await test_quick_research()
        
        # Test 3: Integration Analysis
        results['integration_analysis'] = await test_integration_analysis()
        
        # Test 4: Report Generation
        results['report_generation'] = await test_report_generation()
        
        # Test 5: Complete Workflow
        results['complete_workflow'] = await test_complete_workflow()
        
        # Summary
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        
        all_passed = True
        for test_name, passed in results.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"   {test_name}: {status}")
            if not passed:
                all_passed = False
        
        print("="*60)
        
        if all_passed:
            print("\n🎉 ALL TESTS PASSED!")
            print("✅ System ready for production use")
            return 0
        else:
            print("\n⚠️  SOME TESTS FAILED")
            print("Review errors above")
            return 1
        
    except Exception as e:
        print(f"\n❌ TEST SUITE ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code)

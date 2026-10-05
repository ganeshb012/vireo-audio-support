"""
Root test runner for Vireo Audio Support Desk Assessment.
Run via: python test_pipeline.py
"""

import sys
from src.validation import run_all_validations

def main():
    print("\n" + "=" * 70)
    print("RUNNING VIREO AUDIO DETERMINISTIC PIPELINE & POLICY VALIDATION")
    print("=" * 70 + "\n")
    
    report = run_all_validations(".")
    
    for idx, r in enumerate(report["results"], 1):
        status = "PASSED" if r["passed"] else "FAILED"
        symbol = "[PASS]" if r["passed"] else "[FAIL]"
        print(f"{symbol} Test {idx:02d}: {r['check']}")
        print(f"       Status: {status} | {r['detail']}\n")
        
    print("=" * 70)
    print(f"SUMMARY: {report['passed_count']} / {report['total_count']} Tests Passed successfully.")
    print("=" * 70 + "\n")
    
    if not report["all_passed"]:
        sys.exit(1)

if __name__ == "__main__":
    main()

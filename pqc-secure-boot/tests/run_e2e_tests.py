#!/usr/bin/env python3
"""
PQC Secure Boot E2E Test Suite Runner
Executes Tier 1 (Feature Coverage), Tier 2 (Boundary & Corner Cases),
Tier 3 (Cross-Feature Combinations), and Tier 4 (Real-World Scenarios).
"""

import os
import sys
import time
import unittest
from pathlib import Path

# Ensure tests directory is in Python path
tests_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(tests_dir))

import tier1_feature_coverage
import tier2_boundary_corner
import tier3_cross_feature
import tier4_real_world

def run_all_e2e_tests():
    print("=" * 80)
    print("      POST-QUANTUM FIRMWARE AUTHENTICATION (PQC-BOOT) E2E TEST SUITE")
    print("=" * 80)
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}")
    print(f"Test Directory: {tests_dir}")
    print("=" * 80)
    print()

    suite = unittest.TestSuite()
    loader = unittest.TestLoader()

    suite.addTest(loader.loadTestsFromModule(tier1_feature_coverage))
    suite.addTest(loader.loadTestsFromModule(tier2_boundary_corner))
    suite.addTest(loader.loadTestsFromModule(tier3_cross_feature))
    suite.addTest(loader.loadTestsFromModule(tier4_real_world))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print()
    print("=" * 80)
    print("                         SUMMARY OF E2E TEST RESULTS")
    print("=" * 80)
    print(f"Total Tests Executed: {result.testsRun}")
    print(f"Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 80)

    if result.wasSuccessful():
        print("ALL E2E TEST HARNESSES VERIFIED SUCCESSFULLY [SUCCESS]")
        return 0
    else:
        print("E2E TEST HARNESS ENCOUNTERED FAILURES/ERRORS [FAILURE]")
        return 1

if __name__ == '__main__':
    sys.exit(run_all_e2e_tests())

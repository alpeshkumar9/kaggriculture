"""
Official Kaggle Submission Package Generator & Validator for Kaggriculture.
Bundles submission files into submission.tar.gz and verifies submission constraints (< 100 MiB).
"""

import os
import tarfile
import tempfile
import sys

def package_submission():
    print("=" * 65)
    print("📦 KAGGRICULTURE SUBMISSION PACKAGE GENERATOR")
    print("=" * 65)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    main_file = os.path.join(base_dir, 'main.py')
    agent_file = os.path.join(base_dir, 'agent.py')
    tar_file = os.path.join(base_dir, 'submission.tar.gz')

    # 1. Ensure main.py entry point exists
    main_code = '''"""
Official Kaggle Environments Entrypoint for Kaggriculture
"""
import sys
import os

dir_path = os.path.dirname(os.path.abspath(__file__))
if dir_path not in sys.path:
    sys.path.insert(0, dir_path)

from agent import agent

def my_agent(observation, configuration=None):
    return agent(observation, configuration)
'''
    with open(main_file, 'w') as f:
        f.write(main_code)
    print(f"✅ Created main.py entry point: {main_file}")

    # 2. Package files into submission.tar.gz
    files_to_pack = [
        ('main.py', main_file),
        ('agent.py', agent_file),
    ]

    with tarfile.open(tar_file, 'w:gz') as tar:
        for arcname, filepath in files_to_pack:
            if os.path.exists(filepath):
                tar.add(filepath, arcname=arcname)
                print(f"  • Added: {arcname}")

    tar_size_bytes = os.path.getsize(tar_file)
    tar_size_mb = tar_size_bytes / (1024 * 1024)

    print(f"\n📦 Archive Created: {tar_file}")
    print(f"  • File Size: {tar_size_bytes:,} bytes ({tar_size_mb:.4f} MiB)")
    print(f"  • Kaggle Size Limit: 100.00 MiB")

    # 3. Assert size constraint
    assert tar_size_mb <= 100.0, f"Error: Package size {tar_size_mb:.2f} MiB exceeds 100 MiB limit!"
    print("✅ SIZE ASSERTION PASSED (< 100 MiB)")

    # 4. Verify package contents by extraction & import test
    with tempfile.TemporaryDirectory() as tmpdir:
        with tarfile.open(tar_file, 'r:gz') as tar:
            tar.extractall(path=tmpdir)

        sys.path.insert(0, tmpdir)
        try:
            from main import agent as test_agent
            dummy_obs = {'player': 0, 'farms': [{'money': 1000.0, 'tiles': [[None]*10]*10, 'farmer': [0,0], 'hands': [], 'unlocked_quadrants': ['NW']}], 'market': {'prices': {}}, 'private': {'shed': {}, 'seeds': {}}}
            res = test_agent(dummy_obs)
            assert isinstance(res, dict), "Agent output must be dict"
            assert 'farmer' in res and 'market' in res, "Agent output missing required keys"
            print("✅ PACKAGE EXTRACTION & IMPORT VALIDATION PASSED!")
        finally:
            if tmpdir in sys.path:
                sys.path.remove(tmpdir)

    print("=" * 65)
    print("🚀 SUBMISSION PACKAGE IS 100% READY FOR KAGGLE UPLOAD!")
    print(f"   Command: kaggle competitions submit kaggriculture -f python_bot/submission.tar.gz -m 'Crop-first verified v1'")
    print("=" * 65)

if __name__ == '__main__':
    package_submission()

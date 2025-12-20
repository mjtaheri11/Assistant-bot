import os
import sys
import subprocess
import glob
import shutil
import xml.etree.ElementTree as ET

# --- Configuration ---
TEST_DIR = "tests"
SRC_DIR = "src"
COVERAGE_FILE = ".coverage"
COVERAGE_XML = "coverage.xml"
JUNIT_OUTPUT_FILE = "test-results.xml"
TEMP_XML_DIR = "temp_results"


def clean_artifacts():
    """Removes old coverage and result files to ensure a fresh start."""
    print("🧹 Cleaning up old artifacts...")
    if os.path.exists(COVERAGE_FILE):
        os.remove(COVERAGE_FILE)
    if os.path.exists(COVERAGE_XML):
        os.remove(COVERAGE_XML)
    if os.path.exists(JUNIT_OUTPUT_FILE):
        os.remove(JUNIT_OUTPUT_FILE)
    if os.path.exists(TEMP_XML_DIR):
        shutil.rmtree(TEMP_XML_DIR)
    os.makedirs(TEMP_XML_DIR)


def merge_junit_xmls():
    """Merges multiple JUnit XML files into one."""
    print(f"🔗 Merging JUnit reports into {JUNIT_OUTPUT_FILE}...")
    xml_files = glob.glob(os.path.join(TEMP_XML_DIR, "*.xml"))
    if not xml_files:
        print("⚠️ No XML files found to merge.")
        return

    # Create a root <testsuites> element
    merged_root = ET.Element("testsuites")
    for file_path in xml_files:
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            # JUnit XMLs usually have <testsuites> as root or <testsuite>
            if root.tag == "testsuites":
                for suite in root:
                    merged_root.append(suite)
            else:
                merged_root.append(root)
        except ET.ParseError:
            print(f"❌ Error parsing {file_path}, skipping.")

    tree = ET.ElementTree(merged_root)
    tree.write(JUNIT_OUTPUT_FILE, encoding="utf-8", xml_declaration=True)
    print("✅ JUnit merge complete.")


def run_tests():
    # Get all test files in tests/ folder
    test_files = sorted(glob.glob(os.path.join(TEST_DIR, "test_*.py")))

    failed_tests = []

    print(f"🚀 Starting sequential test run for {len(test_files)} files...")

    for i, test_file in enumerate(test_files):
        # Extract filename for the individual XML report
        base_name = os.path.basename(test_file).replace(".py", "")
        xml_report_path = os.path.join(TEMP_XML_DIR, f"{base_name}.xml")

        print(f"[{i + 1}/{len(test_files)}] Running {test_file}...")

        # Construct command
        # --cov-append: IMPORTANT! Adds to the existing .coverage file instead of overwriting
        cmd = [
            sys.executable, "-m", "pytest", test_file,
            f"--cov={SRC_DIR}",
            "--cov-append",
            f"--junitxml={xml_report_path}"
        ]

        # Run the test in a separate subprocess
        result = subprocess.run(cmd, capture_output=False)  # capture_output=False lets you see the output in real time

        if result.returncode != 0:
            print(f"❌ {test_file} FAILED!")
            failed_tests.append(test_file)
        else:
            print(f"✅ {test_file} PASSED")

    return failed_tests


def generate_final_coverage_report():
    print("📊 Generating final coverage XML report...")
    # Convert the .coverage binary file to XML
    subprocess.run([sys.executable, "-m", "coverage", "xml", "-o", COVERAGE_XML])
    # Optional: Print report to console
    subprocess.run([sys.executable, "-m", "coverage", "report"])


def main():
    clean_artifacts()

    failed = run_tests()

    merge_junit_xmls()
    generate_final_coverage_report()

    # Cleanup temp folder
    if os.path.exists(TEMP_XML_DIR):
        shutil.rmtree(TEMP_XML_DIR)

    if failed:
        print("\n🔴 The following test files failed:")
        for f in failed:
            print(f" - {f}")
        sys.exit(1)
    else:
        print("\n🟢 All tests passed successfully!")
        sys.exit(0)


if __name__ == "__main__":
    main()
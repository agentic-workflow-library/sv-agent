#!/bin/bash
# Validation script for Ploidy Estimation CWL workflow

set -euo pipefail

echo "Validating Ploidy Estimation CWL files..."
echo "========================================="

# Check if cwltool is installed
if ! command -v cwltool &> /dev/null; then
    echo "ERROR: cwltool is not installed"
    echo "Install with: pip install cwltool"
    exit 1
fi

# Validate each CWL file
echo -n "Validating RuntimeAttr.yml schema... "
if cwltool --validate-schemas RuntimeAttr.yml 2>/dev/null; then
    echo "✓ PASS"
else
    echo "✗ FAIL"
    exit 1
fi

echo -n "Validating BuildPloidyMatrix.cwl... "
if cwltool --validate BuildPloidyMatrix.cwl 2>/dev/null; then
    echo "✓ PASS"
else
    echo "✗ FAIL"
    exit 1
fi

echo -n "Validating PloidyScore.cwl... "
if cwltool --validate PloidyScore.cwl 2>/dev/null; then
    echo "✓ PASS"
else
    echo "✗ FAIL"
    exit 1
fi

echo -n "Validating PloidyEstimation.cwl... "
if cwltool --validate PloidyEstimation.cwl 2>/dev/null; then
    echo "✓ PASS"
else
    echo "✗ FAIL"
    exit 1
fi

echo ""
echo "All validations passed! ✓"
echo ""
echo "To run the workflow:"
echo "  cwltool PloidyEstimation.cwl test_inputs.yml"
echo ""
echo "To run with specific runtime parameters:"
echo "  Edit test_inputs.yml and uncomment the runtime_attr sections"
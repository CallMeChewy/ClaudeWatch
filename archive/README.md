# File: README.md
# Path: /home/herb/Desktop/ClaudeWatch/archive/README.md
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-01-26
# Last Modified: 2025-01-26 06:45PM

# Archive Directory

This directory contains archived components from the Claude Code Usage Monitor project cleanup.

## Contents

### `/tests/`
- **Original test suite** (`src/tests/`) - Complete original test framework
- **Enhanced validation tests** (`test_enhanced_features.py`) - Validation for enhanced features
- **Pytest cache** (`.pytest_cache/`) - Cached test data

### `/deprecated_components/`
- **`proxy_monitor.py`** - Original basic proxy monitor (replaced by `enhanced_proxy_monitor.py`)
- **`database.py`** - Original basic database manager (replaced by `enhanced_database.py`)
- **`orchestrator.py`** - Original orchestrator (replaced by `intelligent_orchestrator.py`)

### `/coverage_reports/`
- **`htmlcov/`** - HTML coverage reports
- **`coverage.xml`** - XML coverage report
- **`.coverage`** - Coverage data file

## Why These Were Archived

### Tests
- Moved to archive to clean up main project structure
- Tests remain available for reference and validation
- Enhanced functionality has been validated through comprehensive testing

### Deprecated Components
- **Original components** were replaced with enhanced versions that provide:
  - Real MCP log monitoring vs. simulated output
  - Advanced pattern matching vs. basic string matching
  - Statistical learning vs. fixed percentage reductions
  - Multi-terminal coordination vs. single session focus
  - Comprehensive analytics vs. basic usage stats

### Coverage Reports
- Generated during development phase
- Archived to clean up project root
- Can be regenerated if needed with `pytest --cov`

## Notes

- All archived components remain functional
- Enhanced implementations provide full backward compatibility
- Archive can be restored if needed for debugging or reference
- No functionality has been lost - only improved upon

---

**Archived on**: 2025-01-26  
**Reason**: Project cleanup after enhanced implementation completion  
**Status**: Safe to reference, enhanced versions in use
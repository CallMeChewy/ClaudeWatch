# File: ClaudeStandards.md
# Path: /home/herb/Desktop/ClaudeWatch/Documentation/Standards/ClaudeStandards.md
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-26
# Last Modified: 2025-07-26 08:10AM

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is **Claude Code Usage Monitor** - a Python-based real-time terminal monitoring tool for tracking Claude AI token usage with advanced analytics and Rich UI. The project monitors Claude session token consumption, provides burn rate analysis, cost tracking, and intelligent predictions about session limits.

## Architecture

### Enhanced Core Structure (Post-Cleanup)
- **src/claude_monitor/**: Main package with enhanced modular architecture
- **cli/**: Enhanced CLI with intelligent orchestrator integration
  - `enhanced_main.py` - New production CLI entry point
  - `main.py` - Legacy CLI (maintained for compatibility)
- **core/**: Core models, calculations, pricing, and P90 analysis
- **data/**: Enhanced data processing with intelligent database
  - `enhanced_database.py` - Advanced analytics database (primary)
  - `reader.py` - Enhanced data reader with database integration
- **monitoring/**: Enhanced monitoring with real-time learning
  - `enhanced_proxy_monitor.py` - Real MCP log monitoring (primary)
  - `intelligent_orchestrator.py` - Central coordination system (primary)
- **ui/**: Rich terminal UI components (unchanged)
- **utils/**: Utilities for formatting, time, timezone, and notifications

### Enhanced Key Components
- **IntelligentOrchestrator**: Central coordination with background learning
- **EnhancedProxyMonitor**: Real-time MCP log monitoring with pattern matching
- **EnhancedDatabaseManager**: Comprehensive analytics with 6-table schema
- **SessionMetrics**: Detailed session lifecycle tracking
- **RateLimitPatterns**: Advanced regex pattern matching for API messages

### Archived Components
- **archive/deprecated_components/**: Original components replaced by enhanced versions
- **archive/tests/**: Comprehensive test suite (validated, then archived)
- **archive/coverage_reports/**: Development coverage reports

## Development Commands

### Setup
```bash
# Clone and setup development environment
git clone https://github.com/Maciek-roboblog/Claude-Code-Usage-Monitor.git
cd Claude-Code-Usage-Monitor

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install in development mode with all dependencies
pip install -e .[dev]
```

### Enhanced Production Usage
```bash
# Run enhanced monitor (recommended)
python run_enhanced_monitor.py

# Or with specific options
python run_enhanced_monitor.py --plan max20 --debug

# Show system status
python run_enhanced_monitor.py --status

# Export analytics report
python run_enhanced_monitor.py --export-report /path/to/report.json
```

### Testing (Archived)
```bash
# Tests have been archived after validation - all enhanced features are tested and working
# Original test suite: archive/tests/src/tests/
# Enhanced validation: archive/tests/test_enhanced_features.py

# To restore tests for development (if needed):
# cp -r archive/tests/src/tests/ src/
# python archive/tests/test_enhanced_features.py
```

### Code Quality
```bash
# Run ruff linting
ruff check .

# Auto-fix linting issues
ruff check . --fix

# Format code with ruff
ruff format .

# Run type checking
mypy src/claude_monitor/

# Install and run pre-commit hooks
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

### Building and Distribution
```bash
# Build package
python -m build

# Install locally from source
pip install -e .

# Run the monitor
claude-monitor  # or cmonitor, ccmonitor, ccm

# Test installation
python -m claude_monitor --help
```

### Development Mode
```bash
# Run from source without installation
cd src/
python -m claude_monitor

# Run with debug logging
python -m claude_monitor --debug --log-file monitor.log
```

## Code Conventions

### File Organization
- **PascalCase** for Python files (following AIDEV-PascalCase-2.1 standard)
- **snake_case** for package/module names internally
- Type hints mandatory for all functions and classes
- Comprehensive docstrings using Google style

### Architecture Patterns
- **Single Responsibility Principle**: Each module has one clear purpose
- **Dependency Injection**: Components receive dependencies rather than creating them
- **Event-driven**: Callback system for real-time updates
- **Type Safety**: Pydantic models for configuration and data validation

### Testing Strategy
- **80% minimum coverage** requirement
- **Unit tests** for individual components
- **Integration tests** for component interaction
- **Benchmark tests** for performance validation
- **Mock objects** for external dependencies

## Key Features

### Plans and Limits
- **Pro Plan**: 19,000 tokens, $18.00 cost limit
- **Max5 Plan**: 88,000 tokens, $35.00 cost limit  
- **Max20 Plan**: 220,000 tokens, $140.00 cost limit
- **Custom Plan**: P90-based auto-detection with ML analysis

### Monitoring Capabilities
- **Real-time tracking** with configurable refresh rates (0.1-20 Hz)
- **5-hour session windows** with overlap handling
- **Token burn rate analysis** with predictive modeling
- **Cost tracking** with model-specific pricing (Opus, Sonnet, Haiku)
- **Multi-view support**: realtime, daily, monthly aggregations

### UI Features
- **Rich terminal interface** with WCAG-compliant themes
- **Auto-detection** of terminal background (light/dark/classic)
- **Progress bars** with scientific color schemes
- **Responsive layouts** adapting to terminal size
- **Command aliases**: claude-monitor, cmonitor, ccmonitor, ccm

## Configuration

### CLI Parameters
```bash
--plan [pro|max5|max20|custom]     # Plan type (default: custom)
--custom-limit-tokens INT          # Custom token limit
--view [realtime|daily|monthly]    # View type (default: realtime)
--timezone STRING                  # Timezone (auto-detected)
--time-format [12h|24h|auto]       # Time format (auto-detected)
--theme [light|dark|classic|auto]  # Display theme (auto-detected)
--refresh-rate INT                 # Data refresh rate 1-60 seconds (default: 10)
--refresh-per-second FLOAT         # Display refresh rate 0.1-20 Hz (default: 0.75)
--reset-hour INT                   # Daily reset hour 0-23
--log-level STRING                 # Logging level (default: INFO)
--log-file PATH                    # Log file path
--debug                            # Enable debug logging
--clear                            # Clear saved configuration
```

### Configuration Persistence
- Settings saved to `~/.claude-monitor/last_used.json`
- Atomic file operations prevent corruption
- CLI arguments override saved preferences
- Plan parameter never persisted (security)

## Dependencies

### Core Dependencies
- **pytz>=2023.3**: Timezone handling
- **rich>=13.7.0**: Rich terminal UI
- **pydantic>=2.0.0**: Type validation and settings
- **numpy>=1.21.0**: Statistical calculations
- **pyyaml>=6.0**: Configuration files

### Development Dependencies
- **pytest>=8.0.0**: Testing framework with fixtures
- **pytest-cov>=6.0.0**: Coverage reporting
- **pytest-mock>=3.14.0**: Mock objects for testing
- **ruff>=0.12.0**: Modern Python linter and formatter
- **mypy>=1.13.0**: Static type checking
- **pre-commit>=4.0.0**: Code quality automation

## Common Tasks

### Adding New Features
1. Create feature branch from main
2. Implement with comprehensive type hints
3. Add unit tests achieving 80%+ coverage
4. Update documentation and CLI help
5. Run full test suite and quality checks
6. Submit PR with clear description

### Debugging Session Issues
```bash
# Enable debug logging to file
claude-monitor --debug --log-file ~/.claude-monitor/debug.log

# Check configuration directory
ls -la ~/.claude-monitor/

# Verify Claude configuration
ls -la ~/.config/claude/

# Test with custom configuration path
CLAUDE_CONFIG_DIR=~/.config/claude claude-monitor
```

### Performance Optimization
- Use `pytest --benchmark-only` for performance testing
- Monitor memory usage with built-in profiling
- Optimize refresh rates for terminal capabilities
- Cache frequently accessed data in DataManager

## Troubleshooting

### Common Issues
- **No active session found**: Ensure Claude Code has been used recently and session files exist
- **Permission errors**: Check ~/.config/claude and ~/.claude-monitor directory permissions
- **Import errors**: Ensure all dependencies installed with `pip install -e .[dev]`
- **Type errors**: Run `mypy src/claude_monitor/` to identify type issues

### Environment Variables
- **CLAUDE_CONFIG_DIR**: Override default Claude configuration directory
- **COLORTERM**: Ensure terminal color support is detected
- **TZ**: System timezone for accurate session tracking

This codebase represents a mature, production-ready Python application with comprehensive testing, modern toolchain, and professional architecture following 2025 best practices.
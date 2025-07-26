# File: README.md
# Path: /home/herb/Desktop/ClaudeWatch/README.md
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-26
# Last Modified: 2025-07-26 08:05AM

# 🚀 Enhanced Claude Code Usage Monitor

**Advanced multi-session monitoring with intelligent analytics, beautiful gauge displays, and real-time coordination**

![Enhanced Claude Monitor](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## ✨ **Key Features**

### 🎯 **Multi-Session Monitoring**
- **Advanced Session Detection** - IP/TTY/SSH recognition for independent monitoring
- **Complete Session Isolation** - Separate databases and analytics per terminal
- **Cross-Session Coordination** - Intelligent rate limit sharing and optimization
- **Environment Awareness** - Detects local, SSH, VS Code, Docker, and container contexts

### 📊 **Beautiful Gauge Displays**
- **Color Zone Gauges** - Green (0-70%), Yellow (70-90%), Red (90-100%), Critical (>100%)
- **Real-time Updates** - Live monitoring with 2-second refresh intervals
- **>100% Support** - Gauges can display values exceeding limits
- **Rich UI Components** - Professional panels with comprehensive metrics

### 🧠 **Intelligent Analysis**
- **Startup Analysis** - Historical usage pattern examination with optimization suggestions
- **Machine Learning** - Statistical confidence-based limit refinement
- **Efficiency Scoring** - Comprehensive performance metrics and recommendations
- **Predictive Analytics** - Rate limit prediction and usage optimization

### 🔄 **Real-time Monitoring**
- **MCP Log Interception** - Direct Claude CLI communication monitoring
- **Advanced Pattern Matching** - 15+ regex patterns for rate limit detection
- **Background Processing** - Continuous monitoring with minimal overhead
- **Comprehensive Analytics** - 6-table database with export capabilities

---

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.9+ 
- Claude Code CLI installed and active

### **Installation & Usage**
```bash
# Navigate to project directory
cd /home/herb/Desktop/ClaudeWatch

# Start enhanced monitoring (traditional interface)
python run_enhanced_monitor.py

# Start with beautiful gauge displays (new!)
python run_gauge_monitor.py

# View system status
python run_enhanced_monitor.py --status

# Export analytics
python run_enhanced_monitor.py --export-report analytics.json
```

---

## 🎨 **Display Options**

### **1. Enhanced Traditional Monitor**
```bash
python run_enhanced_monitor.py
```
- Intelligent startup analysis with user consent
- Multi-session detection and coordination
- Real-time rate limit monitoring
- Comprehensive analytics and reporting

### **2. Beautiful Gauge Monitor (New!)**
```bash
# Real-time gauge display
python run_gauge_monitor.py

# Demo mode with sample data
python run_gauge_monitor.py --demo

# Single large gauge
python run_gauge_monitor.py --single-gauge tokens
```

**Gauge Features:**
- **Usage Metrics**: Token usage, message count, rate limit rate
- **Performance**: Efficiency score, session time, response time  
- **System Health**: CPU usage, memory usage, connection health
- **Color Zones**: Visual indication of usage levels with >100% support

---

## 🌐 **Multi-Session Capabilities**

### **Session Detection**
The system automatically detects and monitors:
- **Local Terminals** - Different terminal windows/tabs
- **SSH Connections** - Remote server sessions
- **VS Code Terminals** - Integrated development environment
- **Docker Containers** - Containerized development
- **Jupyter Notebooks** - Interactive development sessions

### **Independent Monitoring**
Each session gets:
- **Separate Database** - Isolated data storage
- **Individual Analytics** - Session-specific metrics
- **Independent Recommendations** - Context-aware optimization
- **Cross-Session Awareness** - Coordinated rate limit management

### **Example Multi-Session Setup**
```bash
# Terminal 1 - Frontend development
cd /project/frontend
python run_enhanced_monitor.py

# Terminal 2 - Backend development  
cd /project/backend
python run_enhanced_monitor.py

# Terminal 3 - SSH to production
ssh server.com
cd /production
python run_enhanced_monitor.py

# All sessions are automatically detected and monitored independently!
```

---

## 📊 **Intelligent Startup Analysis**

### **What It Does**
- **Analyzes** your past 30 days of Claude usage
- **Identifies** optimization opportunities
- **Suggests** improvements with confidence scores
- **Applies** optimizations with your consent
- **Learns** from your patterns over time

### **Example Analysis Results**
```
🔍 Historical Usage Analysis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Usage Summary:
   • Sessions Analyzed: 15
   • Overall Efficiency: 78.5%
   • Improvement Potential: Moderate (15-30%)

🤖 Automatic Optimizations:
   ✅ Enable Intelligent Learning (85% confidence)
   ✅ Optimize Monitoring Rate (70% confidence)

👤 Manual Recommendations:
   💡 Consider Higher Plan Tier (Rate limits in 25% of sessions)
```

---

## 🔧 **Configuration Options**

### **Enhanced Monitor Options**
```bash
# Skip startup analysis for quick start
python run_enhanced_monitor.py --skip-analysis

# Debug mode
python run_enhanced_monitor.py --debug

# Custom project path
python run_enhanced_monitor.py --project-path /custom/path
```

### **Gauge Monitor Options**
```bash
# Real data mode (uses actual monitoring data)
python run_gauge_monitor.py --real-data

# Demo mode (sample data for testing)
python run_gauge_monitor.py --demo

# Single gauge display
python run_gauge_monitor.py --single-gauge [tokens|messages|efficiency]
```

### **Multi-Session Controls**
```bash
# Force single-session mode
python run_enhanced_monitor.py --single-session

# Enable cross-session notifications
python run_enhanced_monitor.py --cross-session-notify
```

---

## 📈 **Analytics & Reporting**

### **Built-in Analytics**
- **Session Metrics**: Duration, efficiency, token usage
- **Rate Limit Analysis**: Frequency, patterns, predictions
- **Usage Patterns**: Peak times, session overlap, efficiency trends
- **Cost Analysis**: Token costs, efficiency improvements
- **Cross-Session Stats**: Coordination effectiveness, resource sharing

### **Export Capabilities**
```bash
# Export comprehensive report
python run_enhanced_monitor.py --export-report full_analytics.json

# Session-specific export
python run_enhanced_monitor.py --export-session session_id

# Multi-session summary
python run_enhanced_monitor.py --export-multi-session
```

---

## 🧪 **Testing**

### **Quick Tests**
```bash
# System validation
python test_multi_session.py

# Feature test suite
python feature_test_suite.py

# Monitor functionality test
python run_enhanced_monitor.py --status
```

### **Multi-Session Testing**
1. Open multiple terminal windows
2. Run monitor in each: `python run_enhanced_monitor.py`
3. Check status: `python run_enhanced_monitor.py --status`
4. Should show multiple active sessions detected

---

## 📁 **Project Structure**

```
ClaudeWatch/
├── src/claude_monitor/           # Core monitoring system
│   ├── core/                     # Core analysis components
│   ├── data/                     # Database and data management
│   ├── monitoring/               # Multi-session orchestration
│   └── ui/                       # User interface components
├── Documentation/                # All project documentation
│   ├── UserGuides/              # User-facing guides
│   ├── TechnicalSpecs/          # Technical documentation
│   └── Standards/               # Coding and design standards
├── run_enhanced_monitor.py      # Main enhanced monitor
├── run_gauge_monitor.py         # Beautiful gauge display
└── Hold/                        # Deprecated/archived components
```

---

## 🎯 **What Makes This Enhanced**

### **vs. Original Monitor**
- ✅ **Multi-Session Support** - Monitor multiple terminals independently
- ✅ **Intelligent Analytics** - Machine learning-based optimization
- ✅ **Beautiful UI** - Gauge displays with color zones
- ✅ **Real-time Coordination** - Cross-session rate limit awareness
- ✅ **Startup Analysis** - Historical pattern analysis with recommendations
- ✅ **Production Ready** - Comprehensive error handling and recovery

### **Key Innovations**
- **Session Isolation Keys** - Unique identification using IP/TTY/process info
- **Statistical Confidence** - ML-based limit detection with confidence scoring
- **User Consent System** - Always asks before applying optimizations
- **Gauge Visualization** - Beautiful color-coded gauges with >100% support
- **Cross-Session Coordination** - Intelligent resource sharing without interference

---

## 🛠️ **Troubleshooting**

### **Common Issues**
- **Monitor won't start**: Run with `--debug` flag for detailed error info
- **Sessions not detected**: Ensure using different terminal windows
- **No historical data**: Use monitor regularly to build analysis history
- **Permission errors**: Check database file permissions in `~/.claude-monitor/`

### **Getting Help**
- Check `Documentation/UserGuides/` for detailed guides
- Run with `--debug` for verbose logging
- Export system status: `python run_enhanced_monitor.py --status`

---

## 📝 **License**

MIT License - See LICENSE file for details.

---

## 🎉 **Ready to Monitor?**

```bash
# Start with beautiful gauges
python run_gauge_monitor.py --demo

# Or traditional enhanced monitoring
python run_enhanced_monitor.py
```

**Every new terminal automatically gets independent monitoring with intelligent analysis!** 🚀

---

**⭐ Enhanced Claude monitoring with multi-session support and beautiful gauge displays - Production Ready!** ⭐
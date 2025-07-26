# File: TESTING_GUIDE.md
# Path: /home/herb/Desktop/ClaudeWatch/TESTING_GUIDE.md
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-26
# Last Modified: 2025-07-26 05:32AM

# 🧪 Complete Testing Guide

## 🚀 **Quick Start Testing**

### **1. Basic System Test**
```bash
cd /home/herb/Desktop/ClaudeWatch
python run_enhanced_monitor.py --status
```
**Expected**: System status with active sessions displayed

### **2. Single Session Test**
```bash
python run_enhanced_monitor.py
```
**Expected**: 
- Startup analysis (if sufficient data)
- Monitoring starts successfully
- Press Ctrl+C to stop

### **3. Multi-Session Test**
Open 3 different terminals and run:

**Terminal 1:**
```bash
cd /home/herb/Desktop/ClaudeWatch
python run_enhanced_monitor.py
```

**Terminal 2:**
```bash
cd /home/herb/Desktop/ClaudeWatch  
python run_enhanced_monitor.py
```

**Terminal 3:**
```bash
cd /home/herb/Desktop/ClaudeWatch
python run_enhanced_monitor.py --status
```

**Expected**: Terminal 3 shows 2+ active sessions detected

---

## 🔍 **Detailed Testing Procedures**

### **Test 1: System Validation**
```bash
# Run built-in validation
python test_multi_session.py
```
**Should show**: All tests passing with session detection working

### **Test 2: Feature Test Suite**
```bash
# Run comprehensive feature tests
python feature_test_suite.py
```
**Should show**: 4/4 test suites passed (100.0%)

### **Test 3: Export Analytics**
```bash
python run_enhanced_monitor.py --export-report test_report.json
```
**Should create**: test_report.json with usage analytics

### **Test 4: SSH Session Test**
If you have SSH access to another machine:
```bash
ssh other-machine
cd /path/to/ClaudeWatch
python run_enhanced_monitor.py
```
**Expected**: SSH session detected with different isolation key

---

## 🎯 **Expected Results**

### **Successful Startup Shows:**
```
🚀 Enhanced Claude Code Usage Monitor
Intelligent monitoring with real-time learning
==================================================
✅ Enhanced monitoring system started successfully!

📊 Session Info:
  Session ID: pts/1:local:herb:workstation:12345
  Session Type: local
  Project Path: /home/herb/Desktop/ClaudeWatch
  
🔍 Features Active:
  • Real-time MCP log monitoring  
  • Advanced rate limit detection
  • Multi-terminal session tracking
  • Comprehensive analytics
```

### **Status Command Shows:**
```
📊 Enhanced Claude Monitor - System Status
==================================================
🖥️  Current Session: herb@workstation:pts/1:12345
📁  Project Path: /home/herb/Desktop/ClaudeWatch
⏱️  Session Type: local
🔄  Active Sessions: 2

📋 All Active Sessions:
┌─────────────────────────────────┬──────────┬─────────────┬──────────────┐
│ Session ID                      │ Type     │ Project     │ Rate Limits  │
├─────────────────────────────────┼──────────┼─────────────┼──────────────┤
│ pts/1:local:herb:workstation    │ local    │ ClaudeWatch │ 0            │
│ pts/2:local:herb:workstation    │ local    │ ClaudeWatch │ 0            │
└─────────────────────────────────┴──────────┴─────────────┴──────────────┘
```

---

## ⚠️ **Troubleshooting**

### **If startup fails:**
```bash
python run_enhanced_monitor.py --debug
```

### **If no sessions detected:**
- Make sure you're using different terminal windows
- Check if terminals are in different directories

### **If tests fail:**
- Verify Python environment
- Check file permissions
- Run with --debug flag

---

## ✅ **Success Indicators**

1. **No errors** during startup
2. **Session detection** working (different terminals show different session IDs)
3. **Status command** shows active sessions
4. **Export works** and creates JSON files
5. **Clean shutdown** with Ctrl+C

---

**Start with the Quick Start tests above - they'll verify everything is working correctly!**
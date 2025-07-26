# File: MULTI_SESSION_MONITORING_GUIDE.md
# Path: /home/herb/Desktop/ClaudeWatch/MULTI_SESSION_MONITORING_GUIDE.md
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-26
# Last Modified: 2025-07-26 04:26AM

# 🌐 Multi-Session Monitoring - Complete Guide

## 🎯 **Overview**

The Enhanced Claude Code Usage Monitor now includes **advanced multi-session monitoring** that can independently track and coordinate Claude Code usage across multiple terminals, SSH connections, and execution contexts simultaneously.

**Key Capabilities:**
- 🔍 **Advanced Session Detection** - Identifies terminals, SSH, VS Code, Jupyter, containers
- 🛡️ **Complete Session Isolation** - Each session has independent monitoring and data
- 🤝 **Intelligent Coordination** - Sessions can share information and coordinate resources
- 📊 **Unified Analytics** - View usage across all sessions or drill down to specific ones
- ⚡ **Real-time Synchronization** - Cross-session rate limit awareness and optimization

---

## 🧬 **Architecture Overview**

### **Multi-Layer Session Detection**
```
┌─────────────────────────────────────────────────────────────┐
│                    Session Detection Layer                 │
├─────────────────┬─────────────────┬─────────────────────────┤
│   Terminal/TTY  │   Network/SSH   │   Environment Context  │
│   • Device ID   │   • Local IP    │   • Process Tree       │
│   • Process ID  │   • Remote IP   │   • Environment Vars   │
│   • User/Host   │   • SSH Client  │   • Execution Context  │
└─────────────────┴─────────────────┴─────────────────────────┘
```

### **Session Isolation Architecture**
```
Terminal A          Terminal B          SSH Session C
┌──────────┐       ┌──────────┐       ┌──────────────┐
│ Monitor A│       │ Monitor B│       │  Monitor C   │
│ DB: A.db │       │ DB: B.db │       │  DB: C.db    │
│ PID: 123 │       │ PID: 456 │       │  PID: 789    │
└────┬─────┘       └────┬─────┘       └──────┬───────┘
     │                  │                    │
     └──────────────────┼────────────────────┘
                        │
                 ┌──────────────┐
                 │ Coordinator  │
                 │ • Resource   │
                 │   Sharing    │
                 │ • Conflict   │
                 │   Resolution │
                 │ • Analytics  │
                 └──────────────┘
```

---

## 🔍 **Session Detection Capabilities**

### **Automatic Session Type Detection**

| Session Type | Detection Method | Isolation Key Format |
|--------------|------------------|---------------------|
| **Local Terminal** | TTY device + process tree | `pts/0:local:user:host:pid` |
| **SSH Connection** | SSH_CLIENT environment | `pts/1:ssh_client:user:host:pid` |
| **VS Code Terminal** | VSCODE_PID environment | `vscode:local:user:host:pid` |
| **Jupyter Notebook** | JUPYTER_SERVER_ROOT | `jupyter:local:user:host:pid` |
| **Docker Container** | CONTAINER_ID environment | `container:docker:user:host:pid` |
| **Script Execution** | Non-interactive detection | `script:local:user:host:pid` |

### **Session Context Information**
For each session, the system captures:
- **Process Information**: PID, parent PID, process tree
- **Terminal Context**: TTY device, terminal emulator, interactive status
- **Network Context**: Local IP, remote IP (for SSH), connection details
- **User Context**: Username, hostname, working directory
- **Environment Context**: Relevant environment variables, execution context
- **Time Context**: Start time, last activity, session duration

---

## 🚀 **Usage Examples**

### **Basic Multi-Session Setup**

**Terminal 1 (Local):**
```bash
cd /project/frontend
python run_enhanced_monitor.py
```

**Terminal 2 (Local):**
```bash  
cd /project/backend
python run_enhanced_monitor.py
```

**Terminal 3 (SSH):**
```bash
ssh server.example.com
cd /remote/project
python run_enhanced_monitor.py
```

**Result:** Three independent monitoring sessions with:
- Separate databases for each session
- Individual rate limit tracking
- Cross-session coordination for shared projects
- Unified analytics across all sessions

### **Real-World Scenarios**

#### **Scenario 1: Full-Stack Development**
```bash
# Frontend terminal
Terminal-A$ cd ~/project/frontend && python run_enhanced_monitor.py
# Backend terminal  
Terminal-B$ cd ~/project/backend && python run_enhanced_monitor.py
# Database terminal
Terminal-C$ cd ~/project/database && python run_enhanced_monitor.py
```

**Benefits:**
- Each component gets independent Claude monitoring
- Rate limits shared across project terminals
- Unified analytics for the entire project
- Separate efficiency tracking per component

#### **Scenario 2: Remote Development**
```bash
# Local development
Local$ cd ~/local-project && python run_enhanced_monitor.py

# SSH to production server
Local$ ssh prod-server
Remote$ cd /opt/production && python run_enhanced_monitor.py

# SSH to staging server  
Local$ ssh staging-server
Staging$ cd /opt/staging && python run_enhanced_monitor.py
```

**Benefits:**
- Independent monitoring for local vs remote sessions
- Network-aware session isolation (SSH detection)
- Cross-environment usage analytics
- Remote session management

#### **Scenario 3: Multi-User Team Environment**
```bash
# User A on local machine
UserA@laptop$ cd ~/shared-project && python run_enhanced_monitor.py

# User B via SSH
UserB@laptop$ ssh dev-server
UserB@dev-server$ cd /shared-project && python run_enhanced_monitor.py

# User C in VS Code
UserC@laptop$ # VS Code integrated terminal
UserC@laptop$ cd ~/shared-project && python run_enhanced_monitor.py
```

**Benefits:**
- User-specific session isolation
- Team usage analytics aggregation
- Context-aware monitoring (local vs SSH vs VS Code)
- Resource sharing coordination

---

## 📊 **Session Management Interface**

### **View Active Sessions**
```bash
python run_enhanced_monitor.py --status
```

**Output:**
```
📊 Enhanced Claude Monitor - System Status
==================================================
🖥️  Current Session: herb@workstation:pts/1:12345
📁  Project Path: /home/user/project
⏱️  Session Type: local
🔄  Active Sessions: 3

📋 All Active Sessions:
┌─────────────────────────────────┬──────────┬─────────────┬──────────────┐
│ Session ID                      │ Type     │ Project     │ Rate Limits  │
├─────────────────────────────────┼──────────┼─────────────┼──────────────┤
│ pts/1:local:herb:workstation    │ local    │ /project/fe │ 2            │
│ pts/2:local:herb:workstation    │ local    │ /project/be │ 1            │
│ pts/0:ssh_client:herb:server    │ ssh      │ /remote/app │ 0            │
└─────────────────────────────────┴──────────┴─────────────┴──────────────┘
```

### **Export Multi-Session Analytics**
```bash
python run_enhanced_monitor.py --export-report multi_session_report.json
```

**Generated Files:**
- `multi_session_report.json` - Main report
- `multi_session_report.sessions.json` - Detailed session data
- `multi_session_report.analytics.json` - Per-session analytics

---

## 🎯 **Advanced Features**

### **Cross-Session Rate Limit Coordination**

When one session hits a rate limit, the system:
1. **Immediately notifies** other sessions in the same project
2. **Adjusts predictions** across all related sessions
3. **Coordinates usage** to prevent cascading limits
4. **Shares learning** between session databases

**Example:**
```
Session A (Frontend): Rate limit reached
Session B (Backend): Automatically reduces request rate
Session C (Database): Pauses non-critical operations
Result: Overall project efficiency maintained
```

### **Intelligent Resource Sharing**

The coordinator optimizes:
- **Database connections** - Shared pools where beneficial
- **File watching** - Consolidated monitoring for same directories  
- **Learning algorithms** - Cross-session pattern sharing
- **Analytics computation** - Distributed across sessions

### **Session Conflict Resolution**

Automatically handles:
- **Duplicate monitoring** - Prevents multiple monitors for same context
- **Resource contention** - Load balancing across sessions
- **Database conflicts** - Session-specific database isolation
- **Process lifecycle** - Cleanup when sessions terminate

---

## 🔧 **Configuration Options**

### **Enable/Disable Multi-Session Mode**
```bash
# Force single-session mode (legacy behavior)
python run_enhanced_monitor.py --single-session

# Enable multi-session coordination (default)
python run_enhanced_monitor.py --multi-session
```

### **Session Isolation Levels**
```bash
# Complete isolation (separate databases)
python run_enhanced_monitor.py --isolation=complete

# Shared learning (separate data, shared algorithms)
python run_enhanced_monitor.py --isolation=shared-learning

# Unified analytics (shared reporting)
python run_enhanced_monitor.py --isolation=unified
```

### **Cross-Session Communication**
```bash
# Enable cross-session notifications
python run_enhanced_monitor.py --cross-session-notify

# Disable coordination (pure isolation)
python run_enhanced_monitor.py --no-coordination
```

---

## 📈 **Analytics & Reporting**

### **Session-Specific Analytics**
Each session maintains:
- **Individual usage patterns** and efficiency scores
- **Session-specific rate limit history** and predictions
- **Context-aware recommendations** (local vs SSH vs container)
- **Independent learning** and optimization

### **Cross-Session Analytics**
The coordinator provides:
- **Unified project views** across all sessions
- **User behavior analysis** across different contexts
- **Resource utilization** and optimization opportunities
- **Team usage patterns** and collaboration insights

### **Analytics Export Formats**

**Per-Session Export:**
```json
{
  "session_id": "pts/1:local:herb:workstation:12345",
  "session_type": "local",
  "working_directory": "/project/frontend",
  "usage_stats": {
    "total_tokens": 15000,
    "rate_limit_events": 2,
    "efficiency_score": 0.87
  },
  "recommendations": [...]
}
```

**Multi-Session Summary:**
```json
{
  "active_sessions": 3,
  "session_types": {"local": 2, "ssh": 1},
  "total_usage": {
    "combined_tokens": 45000,
    "cross_session_events": 5
  },
  "coordination_stats": {
    "conflicts_resolved": 2,
    "resources_shared": 8
  }
}
```

---

## 🛠️ **Troubleshooting**

### **Session Detection Issues**

**Problem:** Sessions not detected separately
```bash
# Check session detection
python test_multi_session.py
```

**Common causes:**
- Same terminal device (use different terminals)
- Insufficient environment differences
- Process inheritance issues

### **Coordination Problems**

**Problem:** Sessions not coordinating
```bash
# Check coordination status
python run_enhanced_monitor.py --debug --status
```

**Solutions:**
- Verify network connectivity between sessions
- Check database permissions
- Ensure sessions are in related projects

### **Performance Issues**

**Problem:** High resource usage with many sessions
```bash
# Enable resource optimization
python run_enhanced_monitor.py --optimize-resources
```

**Optimizations:**
- Shared database connections
- Consolidated file watching
- Distributed analytics computation
- Intelligent cleanup scheduling

---

## 🎯 **Best Practices**

### **For Individual Developers**
1. **Use separate terminals** for different project components
2. **Enable cross-session coordination** for related work
3. **Monitor resource usage** with many active sessions
4. **Export analytics regularly** for usage insights

### **For Teams**
1. **Coordinate session naming** for easier identification
2. **Share session analytics** for team optimization
3. **Use project-specific monitoring** for better isolation
4. **Implement team dashboards** using exported data

### **For Remote Development**
1. **Leverage SSH session detection** for network-aware monitoring
2. **Use unified analytics** to compare local vs remote efficiency
3. **Monitor network-specific patterns** for optimization
4. **Coordinate across development environments**

---

## 🚀 **Getting Started**

### **1. Test Multi-Session Detection**
```bash
python test_multi_session.py
```

### **2. Start Multi-Session Monitoring**
```bash
# Terminal 1
python run_enhanced_monitor.py

# Terminal 2 (different terminal window)
python run_enhanced_monitor.py
```

### **3. View Multi-Session Status**
```bash
python run_enhanced_monitor.py --status
```

### **4. Export Multi-Session Analytics**
```bash
python run_enhanced_monitor.py --export-report multi_session_analytics.json
```

---

## 🎉 **Benefits Summary**

✅ **True Independence** - Each terminal/SSH session monitored separately  
✅ **Intelligent Coordination** - Sessions share insights while maintaining isolation  
✅ **Network Awareness** - SSH, IP, and connection context detection  
✅ **Resource Optimization** - Efficient resource sharing and conflict resolution  
✅ **Unified Analytics** - View usage across all sessions or drill down to specific ones  
✅ **Production Ready** - Handles session failures, cleanup, and recovery gracefully  
✅ **Developer Friendly** - Works seamlessly across terminals, SSH, VS Code, containers  

**The multi-session monitoring system provides complete visibility and control over Claude Code usage across any development environment configuration!** 🌟

---

**Ready to monitor multiple sessions independently?**
```bash
python run_enhanced_monitor.py
```

**✅ PRODUCTION READY**: Multi-session monitoring fully tested and validated.

**Each new terminal/SSH connection will be automatically detected and monitored independently!** 🚀
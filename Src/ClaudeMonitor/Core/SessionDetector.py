# File: SessionDetector.py
# Path: /home/herb/Desktop/ClaudeWatch/Src/ClaudeMonitor/core/SessionDetector.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-26
# Last Modified: 2025-07-26 04:15AM

"""
Advanced session detection and isolation system for multi-terminal monitoring.
Identifies and tracks independent Claude Code sessions across different terminals,
SSH connections, and execution contexts.
"""

import os
import socket
import getpass
import time
import psutil
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timezone
import subprocess
import json
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class SessionContext:
    """Complete context information for a Claude Code session."""
    session_id: str
    terminal_id: str
    process_id: int
    parent_process_id: int
    terminal_device: str
    ssh_connection: Optional[str]
    local_ip: str
    remote_ip: Optional[str]
    user: str
    hostname: str
    working_directory: str
    environment_vars: Dict[str, str]
    start_time: datetime
    last_activity: datetime
    session_type: str  # 'local', 'ssh', 'vscode', 'jupyter', etc.
    isolation_key: str  # Unique key for session isolation
    
    def __post_init__(self):
        """Generate isolation key after initialization."""
        if not hasattr(self, 'isolation_key') or not self.isolation_key:
            self.isolation_key = self._generate_isolation_key()
    
    def _generate_isolation_key(self) -> str:
        """Generate unique isolation key for this session context."""
        components = [
            self.terminal_device,
            self.ssh_connection or "local", 
            self.user,
            self.hostname,
            str(self.process_id)
        ]
        return ":".join(components)

class SessionDetector:
    """
    Advanced session detection system that identifies and tracks
    independent Claude Code sessions across different execution contexts.
    """
    
    def __init__(self):
        self.active_sessions: Dict[str, SessionContext] = {}
        self.session_history: List[SessionContext] = []
        self.detection_methods = [
            self._detect_terminal_session,
            self._detect_ssh_session, 
            self._detect_vscode_session,
            self._detect_jupyter_session,
            self._detect_container_session
        ]
    
    def DetectCurrentSession(self) -> SessionContext:
        """
        Detect and analyze the current session context.
        
        Returns:
            Complete session context with isolation information
        """
        logger.info("Detecting current session context...")
        
        # Get basic process information
        current_pid = os.getpid()
        process = psutil.Process(current_pid)
        
        # Build session context
        context = SessionContext(
            session_id=self._generate_session_id(),
            terminal_id=self._get_terminal_id(),
            process_id=current_pid,
            parent_process_id=process.ppid(),
            terminal_device=self._get_terminal_device(),
            ssh_connection=self._detect_ssh_connection(),
            local_ip=self._get_local_ip(),
            remote_ip=self._get_remote_ip(),
            user=getpass.getuser(),
            hostname=socket.gethostname(),
            working_directory=os.getcwd(),
            environment_vars=self._get_relevant_env_vars(),
            start_time=datetime.now(timezone.utc),
            last_activity=datetime.now(timezone.utc),
            session_type=self._determine_session_type(),
            isolation_key=""  # Will be generated in __post_init__
        )
        
        # Register session
        self.active_sessions[context.isolation_key] = context
        logger.info(f"Detected session: {context.session_type} ({context.isolation_key})")
        
        return context
    
    def GetActiveSessionsCount(self) -> int:
        """Get count of currently active sessions."""
        # Clean up stale sessions first
        self._cleanup_stale_sessions()
        return len(self.active_sessions)
    
    def GetSessionsForProject(self, project_path: str) -> List[SessionContext]:
        """Get all active sessions for a specific project."""
        return [
            session for session in self.active_sessions.values()
            if session.working_directory == project_path
        ]
    
    def IsSessionActive(self, isolation_key: str) -> bool:
        """Check if a session is still active."""
        if isolation_key not in self.active_sessions:
            return False
        
        session = self.active_sessions[isolation_key]
        
        try:
            # Check if process still exists
            process = psutil.Process(session.process_id)
            return process.is_running()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            # Process no longer exists
            self._remove_session(isolation_key)
            return False
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        timestamp = int(time.time() * 1000)  # Millisecond precision
        hostname = socket.gethostname()
        pid = os.getpid()
        return f"session_{hostname}_{pid}_{timestamp}"
    
    def _get_terminal_id(self) -> str:
        """Get enhanced terminal identifier."""
        hostname = socket.gethostname()
        username = getpass.getuser()
        pid = os.getpid()
        tty = self._get_terminal_device()
        timestamp = int(time.time())
        
        return f"{username}@{hostname}:{tty}:{pid}:{timestamp}"
    
    def _get_terminal_device(self) -> str:
        """Get terminal device information."""
        try:
            # Try to get TTY information
            tty = os.ttyname(0) if os.isatty(0) else "notty"
            return os.path.basename(tty)
        except (OSError, AttributeError):
            # Fallback for non-terminal environments
            return f"pid{os.getpid()}"
    
    def _detect_ssh_connection(self) -> Optional[str]:
        """Detect if running in SSH session."""
        ssh_client = os.environ.get('SSH_CLIENT')
        ssh_connection = os.environ.get('SSH_CONNECTION')
        
        if ssh_client:
            return f"ssh_client:{ssh_client}"
        elif ssh_connection:
            return f"ssh_conn:{ssh_connection}"
        
        # Check for SSH TTY patterns
        try:
            tty = os.ttyname(0) if os.isatty(0) else ""
            if 'pts' in tty:
                return f"ssh_pts:{tty}"
        except (OSError, AttributeError):
            pass
        
        return None
    
    def _get_local_ip(self) -> str:
        """Get local IP address."""
        try:
            # Connect to remote address to determine local IP
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except Exception:
            return "127.0.0.1"
    
    def _get_remote_ip(self) -> Optional[str]:
        """Get remote IP if connected via SSH."""
        ssh_client = os.environ.get('SSH_CLIENT')
        if ssh_client:
            # SSH_CLIENT format: "remote_ip remote_port local_port"
            return ssh_client.split()[0]
        
        ssh_connection = os.environ.get('SSH_CONNECTION')
        if ssh_connection:
            # SSH_CONNECTION format: "remote_ip remote_port local_ip local_port"
            return ssh_connection.split()[0]
        
        return None
    
    def _get_relevant_env_vars(self) -> Dict[str, str]:
        """Get environment variables relevant to session detection."""
        relevant_vars = [
            'TERM', 'TERM_PROGRAM', 'TERMINAL_EMULATOR',
            'SSH_CLIENT', 'SSH_CONNECTION', 'SSH_TTY',
            'VSCODE_PID', 'VSCODE_IPC_HOOK_CLI',
            'JUPYTER_SERVER_ROOT', 'JPY_PARENT_PID',
            'CONTAINER_ID', 'KUBERNETES_SERVICE_HOST'
        ]
        
        return {
            var: os.environ.get(var, '')
            for var in relevant_vars
            if os.environ.get(var)
        }
    
    def _determine_session_type(self) -> str:
        """Determine the type of session based on environment."""
        env_vars = self._get_relevant_env_vars()
        
        # Check for specific session types
        if any(key.startswith('SSH_') for key in env_vars):
            return 'ssh'
        elif 'VSCODE_PID' in env_vars or 'VSCODE_IPC_HOOK_CLI' in env_vars:
            return 'vscode'
        elif 'JUPYTER_SERVER_ROOT' in env_vars or 'JPY_PARENT_PID' in env_vars:
            return 'jupyter'
        elif 'CONTAINER_ID' in env_vars or 'KUBERNETES_SERVICE_HOST' in env_vars:
            return 'container'
        elif env_vars.get('TERM_PROGRAM') == 'iTerm.app':
            return 'iterm'
        elif env_vars.get('TERM_PROGRAM') == 'Apple_Terminal':
            return 'terminal'
        elif env_vars.get('TERMINAL_EMULATOR') == 'JetBrains-JediTerm':
            return 'jetbrains'
        elif not os.isatty(0):
            return 'script'
        else:
            return 'local'
    
    def _detect_terminal_session(self) -> Dict[str, Any]:
        """Detect terminal-specific information."""
        return {
            'tty': self._get_terminal_device(),
            'term': os.environ.get('TERM', ''),
            'term_program': os.environ.get('TERM_PROGRAM', ''),
            'is_interactive': os.isatty(0)
        }
    
    def _detect_ssh_session(self) -> Dict[str, Any]:
        """Detect SSH-specific information."""
        return {
            'ssh_client': os.environ.get('SSH_CLIENT'),
            'ssh_connection': os.environ.get('SSH_CONNECTION'),
            'ssh_tty': os.environ.get('SSH_TTY'),
            'is_ssh': bool(self._detect_ssh_connection())
        }
    
    def _detect_vscode_session(self) -> Dict[str, Any]:
        """Detect VS Code integrated terminal."""
        return {
            'vscode_pid': os.environ.get('VSCODE_PID'),
            'vscode_ipc': os.environ.get('VSCODE_IPC_HOOK_CLI'),
            'is_vscode': bool(os.environ.get('VSCODE_PID'))
        }
    
    def _detect_jupyter_session(self) -> Dict[str, Any]:
        """Detect Jupyter notebook environment."""
        return {
            'jupyter_root': os.environ.get('JUPYTER_SERVER_ROOT'),
            'jupyter_parent': os.environ.get('JPY_PARENT_PID'),
            'is_jupyter': bool(os.environ.get('JUPYTER_SERVER_ROOT'))
        }
    
    def _detect_container_session(self) -> Dict[str, Any]:
        """Detect container/Kubernetes environment."""
        return {
            'container_id': os.environ.get('CONTAINER_ID'),
            'k8s_service': os.environ.get('KUBERNETES_SERVICE_HOST'),
            'is_container': bool(os.environ.get('CONTAINER_ID') or os.environ.get('KUBERNETES_SERVICE_HOST'))
        }
    
    def _cleanup_stale_sessions(self) -> None:
        """Remove sessions for processes that no longer exist."""
        stale_keys = []
        
        for isolation_key, session in self.active_sessions.items():
            try:
                process = psutil.Process(session.process_id)
                if not process.is_running():
                    stale_keys.append(isolation_key)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                stale_keys.append(isolation_key)
        
        for key in stale_keys:
            self._remove_session(key)
    
    def _remove_session(self, isolation_key: str) -> None:
        """Remove a session and archive it to history."""
        if isolation_key in self.active_sessions:
            session = self.active_sessions.pop(isolation_key)
            session.last_activity = datetime.now(timezone.utc)
            self.session_history.append(session)
            logger.info(f"Removed stale session: {isolation_key}")
    
    def GetSessionSummary(self) -> Dict[str, Any]:
        """Get summary of all session information."""
        self._cleanup_stale_sessions()
        
        session_types = {}
        for session in self.active_sessions.values():
            session_type = session.session_type
            session_types[session_type] = session_types.get(session_type, 0) + 1
        
        return {
            'active_sessions': len(self.active_sessions),
            'session_types': session_types,
            'total_historical': len(self.session_history),
            'sessions_by_project': self._group_sessions_by_project()
        }
    
    def _group_sessions_by_project(self) -> Dict[str, int]:
        """Group active sessions by project directory."""
        projects = {}
        for session in self.active_sessions.values():
            project = session.working_directory
            projects[project] = projects.get(project, 0) + 1
        return projects
    
    def ExportSessionData(self, output_path: Path) -> None:
        """Export detailed session data for analysis."""
        data = {
            'active_sessions': [
                {
                    'session_id': s.session_id,
                    'terminal_id': s.terminal_id,
                    'session_type': s.session_type,
                    'isolation_key': s.isolation_key,
                    'user': s.user,
                    'hostname': s.hostname,
                    'working_directory': s.working_directory,
                    'start_time': s.start_time.isoformat(),
                    'ssh_connection': s.ssh_connection,
                    'local_ip': s.local_ip,
                    'remote_ip': s.remote_ip,
                    'environment_vars': s.environment_vars
                }
                for s in self.active_sessions.values()
            ],
            'summary': self.GetSessionSummary(),
            'export_time': datetime.now(timezone.utc).isoformat()
        }
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
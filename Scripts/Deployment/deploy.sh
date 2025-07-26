#!/bin/bash
# File: deploy.sh
# Path: /home/herb/Desktop/AndyLibrary/Scripts/Deployment/deploy.sh
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-26
# Last Modified: 2025-07-26 04:48AM

# AndyLibrary Production Deployment Script
# Automated deployment for Ubuntu 20.04+ servers

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_USER="andylibrary"
APP_DIR="/opt/andylibrary"
DOMAIN=""
EMAIL=""
REPO_URL="https://github.com/yourusername/AndyLibrary.git"

# Logging
LOG_FILE="/var/log/andylibrary-deployment.log"
exec 1> >(tee -a "$LOG_FILE")
exec 2> >(tee -a "$LOG_FILE" >&2)

echo_header() {
    echo -e "\n${BLUE}================================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================================================${NC}\n"
}

echo_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

echo_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

echo_error() {
    echo -e "${RED}❌ $1${NC}"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        echo_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

check_ubuntu() {
    if ! grep -q "Ubuntu" /etc/os-release; then
        echo_warning "This script is optimized for Ubuntu. Continuing anyway..."
    fi
}

get_user_input() {
    echo_header "🔧 ANDYLIBRARY DEPLOYMENT CONFIGURATION"
    
    read -p "Enter your domain name (e.g., bowersworld.com): " DOMAIN
    if [[ -z "$DOMAIN" ]]; then
        echo_error "Domain name is required"
        exit 1
    fi
    
    read -p "Enter your email for SSL certificates: " EMAIL
    if [[ -z "$EMAIL" ]]; then
        echo_error "Email is required for SSL certificates"
        exit 1
    fi
    
    read -p "Enter repository URL (press Enter for default): " REPO_INPUT
    if [[ -n "$REPO_INPUT" ]]; then
        REPO_URL="$REPO_INPUT"
    fi
    
    echo_success "Configuration complete"
    echo "  Domain: $DOMAIN"
    echo "  Email: $EMAIL"
    echo "  Repository: $REPO_URL"
    echo ""
    
    read -p "Continue with deployment? (y/N): " CONFIRM
    if [[ "$CONFIRM" != "y" && "$CONFIRM" != "Y" ]]; then
        echo "Deployment cancelled"
        exit 0
    fi
}

update_system() {
    echo_header "📦 UPDATING SYSTEM PACKAGES"
    
    apt update
    apt upgrade -y
    apt autoremove -y
    
    echo_success "System packages updated"
}

install_dependencies() {
    echo_header "🔧 INSTALLING DEPENDENCIES"
    
    # Python and development tools
    apt install -y python3.11 python3.11-pip python3.11-venv python3.11-dev
    apt install -y build-essential
    
    # Web server and process management
    apt install -y nginx supervisor
    
    # SSL certificates
    apt install -y certbot python3-certbot-nginx
    
    # Database and utilities
    apt install -y sqlite3 git curl wget unzip
    
    # Node.js (optional tooling)
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt install -y nodejs
    
    # Firewall
    apt install -y ufw
    
    echo_success "Dependencies installed"
}

create_app_user() {
    echo_header "👤 CREATING APPLICATION USER"
    
    # Create application user
    if ! id "$APP_USER" &>/dev/null; then
        useradd -m -s /bin/bash "$APP_USER"
        usermod -aG www-data "$APP_USER"
        echo_success "Created user: $APP_USER"
    else
        echo_warning "User $APP_USER already exists"
    fi
    
    # Create application directory
    mkdir -p "$APP_DIR"
    chown "$APP_USER:$APP_USER" "$APP_DIR"
    
    echo_success "Application user configured"
}

deploy_application() {
    echo_header "🚀 DEPLOYING APPLICATION"
    
    # Switch to application user for deployment
    sudo -u "$APP_USER" bash << EOF
        cd "$APP_DIR"
        
        # Clone or update repository
        if [ -d ".git" ]; then
            echo "Updating existing repository..."
            git pull origin main
        else
            echo "Cloning repository..."
            git clone "$REPO_URL" .
        fi
        
        # Create virtual environment
        python3.11 -m venv venv
        source venv/bin/activate
        
        # Install Python dependencies
        pip install --upgrade pip
        pip install -r requirements.txt
        
        # Create necessary directories
        mkdir -p logs Data/Databases Config/production Scripts
        chmod 755 Data/Databases
        
        echo "Application deployed successfully"
EOF
    
    echo_success "Application deployment complete"
}

configure_environment() {
    echo_header "⚙️  CONFIGURING ENVIRONMENT"
    
    # Create production environment file
    sudo -u "$APP_USER" tee "$APP_DIR/.env" > /dev/null << EOF
# Production Environment Variables
ENVIRONMENT=production
BASE_URL=https://$DOMAIN
API_BASE_URL=https://$DOMAIN

# Database
DATABASE_PATH=$APP_DIR/Data/Databases/MyLibrary.db

# Security (generate random secrets)
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
JWT_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
OAUTH_STATE_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# Email Service (configure with your provider)
# SENDGRID_API_KEY=your_sendgrid_api_key_here
# AWS_ACCESS_KEY_ID=your_aws_access_key
# AWS_SECRET_ACCESS_KEY=your_aws_secret_key
# MAILGUN_API_KEY=your_mailgun_api_key
# MAILGUN_DOMAIN=your_mailgun_domain

# OAuth Provider Secrets (configure with your provider credentials)
# GOOGLE_CLIENT_SECRET=your_google_client_secret
# GITHUB_CLIENT_SECRET=your_github_client_secret
# FACEBOOK_CLIENT_SECRET=your_facebook_client_secret

# Application Settings
LOG_LEVEL=INFO
MAX_WORKERS=4
PORT=8000
HOST=127.0.0.1
EOF
    
    # Secure the environment file
    chmod 600 "$APP_DIR/.env"
    chown "$APP_USER:$APP_USER" "$APP_DIR/.env"
    
    echo_success "Environment configuration complete"
    echo_warning "Remember to configure your email service and OAuth providers in $APP_DIR/.env"
}

setup_database() {
    echo_header "🗄️  SETTING UP DATABASE"
    
    sudo -u "$APP_USER" bash << EOF
        cd "$APP_DIR"
        source venv/bin/activate
        
        # Initialize database
        python -c "
from Source.Core.DatabaseManager import DatabaseManager
db = DatabaseManager('$APP_DIR/Data/Databases/MyLibrary.db')
print('Database initialized successfully')
"
EOF
    
    # Set proper permissions
    chmod 644 "$APP_DIR/Data/Databases/MyLibrary.db"
    chown "$APP_USER:$APP_USER" "$APP_DIR/Data/Databases/MyLibrary.db"
    
    echo_success "Database setup complete"
}

configure_nginx() {
    echo_header "🌐 CONFIGURING NGINX WEB SERVER"
    
    # Create Nginx configuration
    tee /etc/nginx/sites-available/andylibrary > /dev/null << EOF
# AndyLibrary Production Configuration
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;
    
    # SSL Configuration (will be configured by certbot)
    
    # Security headers
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 10240;
    gzip_proxied expired no-cache no-store private must-revalidate auth;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
    
    # Static files
    location /static/ {
        alias $APP_DIR/WebPages/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Favicon
    location /favicon.ico {
        alias $APP_DIR/WebPages/favicon.ico;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Application proxy
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$http_host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # Health check endpoint
    location /health {
        access_log off;
        proxy_pass http://127.0.0.1:8000/health;
    }
}
EOF
    
    # Enable site
    ln -sf /etc/nginx/sites-available/andylibrary /etc/nginx/sites-enabled/
    
    # Remove default site
    rm -f /etc/nginx/sites-enabled/default
    
    # Test configuration
    nginx -t
    
    echo_success "Nginx configuration complete"
}

setup_ssl() {
    echo_header "🔒 SETTING UP SSL CERTIFICATES"
    
    # Reload nginx for initial configuration
    systemctl reload nginx
    
    # Obtain SSL certificate
    certbot --nginx -d "$DOMAIN" -d "www.$DOMAIN" --email "$EMAIL" --agree-tos --non-interactive
    
    # Setup auto-renewal
    (crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -
    
    echo_success "SSL certificates configured"
}

configure_supervisor() {
    echo_header "⚙️  CONFIGURING PROCESS MANAGEMENT"
    
    # Create supervisor configuration
    tee /etc/supervisor/conf.d/andylibrary.conf > /dev/null << EOF
[program:andylibrary]
command=$APP_DIR/venv/bin/python $APP_DIR/StartAndyGoogle.py --host 127.0.0.1 --port 8000
directory=$APP_DIR
user=$APP_USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=$APP_DIR/logs/application.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=5
environment=PATH="$APP_DIR/venv/bin"

[program:andylibrary-healthcheck]
command=$APP_DIR/Scripts/health_check.sh
directory=$APP_DIR
user=$APP_USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=$APP_DIR/logs/healthcheck.log
stdout_logfile_maxbytes=10MB
stdout_logfile_backups=3
environment=PATH="$APP_DIR/venv/bin"
EOF
    
    # Reload supervisor
    supervisorctl reread
    supervisorctl update
    
    echo_success "Process management configured"
}

setup_firewall() {
    echo_header "🛡️  CONFIGURING FIREWALL"
    
    # Configure UFW firewall
    ufw --force reset
    ufw default deny incoming
    ufw default allow outgoing
    ufw allow ssh
    ufw allow 'Nginx Full'
    ufw --force enable
    
    echo_success "Firewall configured"
}

create_backup_scripts() {
    echo_header "💾 SETTING UP BACKUP SYSTEM"
    
    # Create backup directory
    mkdir -p "$APP_DIR/backups"
    chown "$APP_USER:$APP_USER" "$APP_DIR/backups"
    
    # Create backup script
    sudo -u "$APP_USER" tee "$APP_DIR/Scripts/backup_database.sh" > /dev/null << 'EOF'
#!/bin/bash
# Database backup script

BACKUP_DIR="/opt/andylibrary/backups"
DB_PATH="/opt/andylibrary/Data/Databases/MyLibrary.db"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
sqlite3 $DB_PATH ".backup $BACKUP_DIR/MyLibrary_$DATE.db"
gzip $BACKUP_DIR/MyLibrary_$DATE.db

# Keep last 30 days of backups
find $BACKUP_DIR -name "*.db.gz" -mtime +30 -delete

echo "Database backup completed: MyLibrary_$DATE.db.gz"
EOF
    
    chmod +x "$APP_DIR/Scripts/backup_database.sh"
    
    # Schedule backups
    sudo -u "$APP_USER" bash << 'EOF'
        (crontab -l 2>/dev/null; echo "0 2 * * * /opt/andylibrary/Scripts/backup_database.sh") | crontab -
EOF
    
    echo_success "Backup system configured"
}

create_health_check() {
    echo_header "🏥 SETTING UP HEALTH MONITORING"
    
    # Create health check script
    sudo -u "$APP_USER" tee "$APP_DIR/Scripts/health_check.sh" > /dev/null << 'EOF'
#!/bin/bash
# Health check script for AndyLibrary

APP_DIR="/opt/andylibrary"
LOG_FILE="$APP_DIR/logs/health.log"

echo "=== AndyLibrary Health Check $(date) ===" >> $LOG_FILE

# Check application process
if pgrep -f "StartAndyGoogle.py" > /dev/null; then
    echo "✅ Application process running" >> $LOG_FILE
else
    echo "❌ Application process not running" >> $LOG_FILE
    supervisorctl restart andylibrary
fi

# Check database accessibility
if python3 -c "
import sqlite3
conn = sqlite3.connect('$APP_DIR/Data/Databases/MyLibrary.db')
cursor = conn.execute('SELECT COUNT(*) FROM books')
count = cursor.fetchone()[0]
print(f'✅ Database accessible: {count} books')
conn.close()
" >> $LOG_FILE 2>&1; then
    echo "Database check passed" >> $LOG_FILE
else
    echo "❌ Database check failed" >> $LOG_FILE
fi

# Check web server response
if curl -sf https://$(hostname)/health > /dev/null 2>&1; then
    echo "✅ Web server responding" >> $LOG_FILE
else
    echo "❌ Web server not responding" >> $LOG_FILE
fi

# Check disk space
DISK_USAGE=$(df $APP_DIR | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -lt 80 ]; then
    echo "✅ Disk usage: ${DISK_USAGE}%" >> $LOG_FILE
else
    echo "⚠️  High disk usage: ${DISK_USAGE}%" >> $LOG_FILE
fi

echo "=== Health Check Complete ===" >> $LOG_FILE
sleep 300  # Run every 5 minutes
EOF
    
    chmod +x "$APP_DIR/Scripts/health_check.sh"
    
    echo_success "Health monitoring configured"
}

setup_log_rotation() {
    echo_header "📋 CONFIGURING LOG ROTATION"
    
    tee /etc/logrotate.d/andylibrary > /dev/null << EOF
$APP_DIR/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 644 $APP_USER $APP_USER
    postrotate
        supervisorctl restart andylibrary
    endscript
}
EOF
    
    echo_success "Log rotation configured"
}

start_services() {
    echo_header "🚀 STARTING SERVICES"
    
    # Start and enable services
    systemctl enable nginx
    systemctl enable supervisor
    systemctl start nginx
    systemctl start supervisor
    
    # Start application
    supervisorctl start andylibrary
    
    echo_success "Services started"
}

run_tests() {
    echo_header "🧪 RUNNING DEPLOYMENT TESTS"
    
    echo "Testing basic connectivity..."
    sleep 10  # Wait for services to start
    
    # Test HTTP redirect
    if curl -I "http://$DOMAIN" 2>/dev/null | grep -q "301\|Location.*https"; then
        echo_success "HTTP to HTTPS redirect working"
    else
        echo_warning "HTTP to HTTPS redirect may not be working"
    fi
    
    # Test HTTPS
    if curl -I "https://$DOMAIN" 2>/dev/null | grep -q "200 OK"; then
        echo_success "HTTPS connection working"
    else
        echo_error "HTTPS connection failed"
    fi
    
    # Test application health
    if curl -sf "https://$DOMAIN/health" > /dev/null 2>&1; then
        echo_success "Application health check passing"
    else
        echo_warning "Application health check not responding (may need configuration)"
    fi
    
    echo_success "Basic deployment tests complete"
}

show_completion_message() {
    echo_header "🎉 DEPLOYMENT COMPLETE!"
    
    echo -e "${GREEN}AndyLibrary has been successfully deployed!${NC}\n"
    
    echo "📋 NEXT STEPS:"
    echo "1. Configure your email service in: $APP_DIR/.env"
    echo "   - Uncomment and set SENDGRID_API_KEY, AWS credentials, or MAILGUN settings"
    echo ""
    echo "2. Configure OAuth providers (optional) in: $APP_DIR/.env"
    echo "   - Set GOOGLE_CLIENT_SECRET, GITHUB_CLIENT_SECRET, FACEBOOK_CLIENT_SECRET"
    echo ""
    echo "3. Test your deployment:"
    echo "   - Visit: https://$DOMAIN"
    echo "   - Try user registration and email verification"
    echo "   - Check logs: tail -f $APP_DIR/logs/application.log"
    echo ""
    echo "📊 MONITORING:"
    echo "   - Health checks: $APP_DIR/logs/health.log"
    echo "   - Backups: $APP_DIR/backups/"
    echo "   - Process status: supervisorctl status"
    echo ""
    echo "🔧 MANAGEMENT COMMANDS:"
    echo "   - Restart app: supervisorctl restart andylibrary"
    echo "   - Reload nginx: systemctl reload nginx"
    echo "   - View logs: tail -f $APP_DIR/logs/application.log"
    echo ""
    echo -e "${BLUE}🎯 Mission Ready: Getting education into the hands of people who can least afford it!${NC}"
}

# Main deployment flow
main() {
    echo_header "🚀 ANDYLIBRARY PRODUCTION DEPLOYMENT"
    echo "Automated deployment script for Ubuntu 20.04+"
    echo "This script will install and configure AndyLibrary for production use."
    echo ""
    
    check_root
    check_ubuntu
    get_user_input
    
    update_system
    install_dependencies
    create_app_user
    deploy_application
    configure_environment
    setup_database
    configure_nginx
    setup_ssl
    configure_supervisor
    setup_firewall
    create_backup_scripts
    create_health_check
    setup_log_rotation
    start_services
    run_tests
    
    show_completion_message
}

# Handle script interruption
trap 'echo_error "Deployment interrupted"; exit 1' INT TERM

# Run main function
main "$@"
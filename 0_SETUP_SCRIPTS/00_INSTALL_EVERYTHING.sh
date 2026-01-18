#!/bin/bash

# ██████╗  ██████╗  █████╗ ███████╗████████╗██╗███████╗██╗   ██╗
# ██╔══██╗██╔═══██╗██╔══██╗██╔════╝╚══██╔══╝██║██╔════╝╚██╗ ██╔╝
# ██████╔╝██║   ██║███████║███████╗   ██║   ██║█████╗   ╚████╔╝ 
# ██╔══██╗██║   ██║██╔══██║╚════██║   ██║   ██║██╔══╝    ╚██╔╝  
# ██║  ██║╚██████╔╝██║  ██║███████║   ██║   ██║██║        ██║   
# ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝╚═╝        ╚═╝   
#                                                                
# ROASTIFY PRO - ULTIMATE ONE-COMMAND INSTALLATION
# Complete system deployment in single command

set -e

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                   ROASTIFY PRO v2.0                      ║"
echo "║         Ultimate Telegram Bot System Installer           ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "🚀 Starting complete installation..."
echo "⏱️  Estimated time: 5-10 minutes"
echo ""

# Configuration
VERSION="2.0.0"
INSTALL_DIR="/opt/roastify"
REPO_URL="https://github.com/roastify/roastify-pro.git"
DOMAIN=""
EMAIL=""
BOT_TOKEN=""
OWNER_ID=""
ADMIN_IDS=""
AUTO_CONFIGURE=true
SKIP_CHECKS=false
FORCE_INSTALL=false
CLOUD_DEPLOY=false

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ASCII Art
print_banner() {
    clear
    cat << "EOF"
    
    ██████╗  ██████╗  █████╗ ███████╗████████╗██╗███████╗██╗   ██╗
    ██╔══██╗██╔═══██╗██╔══██╗██╔════╝╚══██╔══╝██║██╔════╝╚██╗ ██╔╝
    ██████╔╝██║   ██║███████║███████╗   ██║   ██║█████╗   ╚████╔╝ 
    ██╔══██╗██║   ██║██╔══██║╚════██║   ██║   ██║██╔══╝    ╚██╔╝  
    ██║  ██║╚██████╔╝██║  ██║███████║   ██║   ██║██║        ██║   
    ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝╚═╝        ╚═╝   
                                                                
    ██████╗ ██████╗  ██████╗      ██████╗ ██████╗  ██████╗ 
    ██╔══██╗██╔══██╗██╔═══██╗    ██╔═══██╗██╔══██╗██╔═══██╗
    ██████╔╝██████╔╝██║   ██║    ██║   ██║██████╔╝██║   ██║
    ██╔══██╗██╔══██╗██║   ██║    ██║   ██║██╔══██╗██║   ██║
    ██║  ██║██║  ██║╚██████╔╝    ╚██████╔╝██║  ██║╚██████╔╝
    ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ 
    
    ════════════════════════════════════════════════════════
                  ULTIMATE INSTALLATION SYSTEM
    ════════════════════════════════════════════════════════
    
EOF
}

# Progress bar
progress_bar() {
    local duration=$1
    local steps=50
    local step_duration=$(echo "scale=3; $duration/$steps" | bc)
    
    echo -n "["
    for ((i=0; i<steps; i++)); do
        sleep $step_duration
        echo -n "█"
    done
    echo "]"
}

# Check system requirements
check_requirements() {
    echo -e "${BLUE}🔍 Checking system requirements...${NC}"
    
    # Check OS
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
        echo -e "  ✓ OS: $OS $VER"
    else
        echo -e "${YELLOW}⚠  Could not detect OS${NC}"
    fi
    
    # Check architecture
    ARCH=$(uname -m)
    echo -e "  ✓ Architecture: $ARCH"
    
    # Check Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | awk '{print $2}')
        echo -e "  ✓ Python: $PYTHON_VERSION"
        
        if [[ $(echo "$PYTHON_VERSION 3.8" | awk '{print ($1 >= $2)}') -eq 1 ]]; then
            echo -e "  ✓ Python version OK"
        else
            echo -e "${RED}✗ Python 3.8+ required${NC}"
            exit 1
        fi
    else
        echo -e "${RED}✗ Python3 not found${NC}"
        exit 1
    fi
    
    # Check RAM
    TOTAL_RAM=$(free -g | awk '/^Mem:/{print $2}')
    if [[ $TOTAL_RAM -ge 2 ]]; then
        echo -e "  ✓ RAM: ${TOTAL_RAM}GB (Minimum: 2GB)"
    else
        echo -e "${YELLOW}⚠  Low RAM: ${TOTAL_RAM}GB (Recommended: 4GB+)${NC}"
    fi
    
    # Check disk space
    FREE_SPACE=$(df -h / | awk 'NR==2 {print $4}')
    echo -e "  ✓ Free disk space: $FREE_SPACE"
    
    # Check internet
    if ping -c 1 google.com &> /dev/null; then
        echo -e "  ✓ Internet connection: OK"
    else
        echo -e "${YELLOW}⚠  No internet connection${NC}"
    fi
    
    echo -e "${GREEN}✓ All requirements satisfied${NC}"
}

# Parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --domain=*)
                DOMAIN="${1#*=}"
                shift
                ;;
            --email=*)
                EMAIL="${1#*=}"
                shift
                ;;
            --bot-token=*)
                BOT_TOKEN="${1#*=}"
                shift
                ;;
            --owner-id=*)
                OWNER_ID="${1#*=}"
                shift
                ;;
            --admin-ids=*)
                ADMIN_IDS="${1#*=}"
                shift
                ;;
            --install-dir=*)
                INSTALL_DIR="${1#*=}"
                shift
                ;;
            --skip-checks)
                SKIP_CHECKS=true
                shift
                ;;
            --force)
                FORCE_INSTALL=true
                shift
                ;;
            --cloud)
                CLOUD_DEPLOY=true
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                echo -e "${RED}Unknown option: $1${NC}"
                show_help
                exit 1
                ;;
        esac
    done
}

# Show help
show_help() {
    echo ""
    echo "Roastify Pro Installation Script"
    echo "================================="
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --domain=DOMAIN           Your domain name (e.g., roastify.com)"
    echo "  --email=EMAIL             Email for SSL certificates"
    echo "  --bot-token=TOKEN         Telegram Bot Token from @BotFather"
    echo "  --owner-id=ID             Your Telegram User ID"
    echo "  --admin-ids=IDS           Comma-separated admin IDs"
    echo "  --install-dir=PATH        Installation directory (default: /opt/roastify)"
    echo "  --skip-checks             Skip system requirement checks"
    echo "  --force                   Force installation even if checks fail"
    echo "  --cloud                   Configure for cloud deployment"
    echo "  --help                    Show this help message"
    echo ""
    echo "Example:"
    echo "  $0 --domain=roastify.com --email=admin@roastify.com \\"
    echo "      --bot-token=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11 \\"
    echo "      --owner-id=123456789 --admin-ids=987654321,1122334455"
    echo ""
}

# Interactive configuration
interactive_config() {
    echo ""
    echo -e "${CYAN}⚙️  Configuration Setup${NC}"
    echo "══════════════════════════"
    
    # Ask for domain
    if [[ -z "$DOMAIN" ]]; then
        read -p "Enter your domain (e.g., roastify.com): " DOMAIN
    fi
    
    # Ask for email
    if [[ -z "$EMAIL" ]]; then
        read -p "Enter your email (for SSL certificates): " EMAIL
    fi
    
    # Ask for bot token
    if [[ -z "$BOT_TOKEN" ]]; then
        echo ""
        echo -e "${YELLOW}📱 Telegram Bot Token Required${NC}"
        echo "1. Open Telegram and search for @BotFather"
        echo "2. Send /newbot command"
        echo "3. Follow instructions to create a bot"
        echo "4. Copy the bot token (looks like: 123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11)"
        echo ""
        read -p "Enter your bot token: " BOT_TOKEN
        
        if [[ -z "$BOT_TOKEN" ]]; then
            echo -e "${RED}❌ Bot token is required!${NC}"
            exit 1
        fi
    fi
    
    # Ask for owner ID
    if [[ -z "$OWNER_ID" ]]; then
        echo ""
        echo -e "${YELLOW}👤 Your Telegram User ID Required${NC}"
        echo "1. Open Telegram and search for @userinfobot"
        echo "2. Send any message to the bot"
        echo "3. Copy your user ID"
        echo ""
        read -p "Enter your Telegram user ID: " OWNER_ID
        
        if [[ -z "$OWNER_ID" ]]; then
            echo -e "${RED}❌ Owner ID is required!${NC}"
            exit 1
        fi
    fi
    
    # Ask for admin IDs
    if [[ -z "$ADMIN_IDS" ]]; then
        read -p "Enter admin IDs (comma-separated, optional): " ADMIN_IDS
    fi
    
    # Confirm configuration
    echo ""
    echo -e "${CYAN}📋 Configuration Summary${NC}"
    echo "══════════════════════════"
    echo "Domain:       $DOMAIN"
    echo "Email:        $EMAIL"
    echo "Bot Token:    ${BOT_TOKEN:0:10}..."
    echo "Owner ID:     $OWNER_ID"
    echo "Admin IDs:    ${ADMIN_IDS:-None}"
    echo "Install Dir:  $INSTALL_DIR"
    echo ""
    
    read -p "Continue with installation? (yes/no): " CONFIRM
    if [[ "$CONFIRM" != "yes" && "$CONFIRM" != "y" ]]; then
        echo -e "${YELLOW}Installation cancelled.${NC}"
        exit 0
    fi
}

# Install system dependencies
install_dependencies() {
    echo ""
    echo -e "${BLUE}📦 Installing system dependencies...${NC}"
    
    # Detect package manager
    if command -v apt-get &> /dev/null; then
        echo "Detected apt package manager"
        
        # Update package list
        sudo apt-get update -y
        
        # Install dependencies
        sudo apt-get install -y \
            git curl wget \
            python3-pip python3-venv python3-dev \
            docker.io docker-compose \
            nginx certbot python3-certbot-nginx \
            redis-server postgresql postgresql-contrib \
            ffmpeg libsm6 libxext6 libgl1-mesa-glx \
            build-essential libssl-dev libffi-dev \
            net-tools htop tree jq
    
    elif command -v yum &> /dev/null; then
        echo "Detected yum package manager"
        
        sudo yum update -y
        sudo yum install -y \
            git curl wget \
            python3 python3-pip python3-devel \
            docker docker-compose \
            nginx certbot python3-certbot-nginx \
            redis postgresql postgresql-server \
            ffmpeg mesa-libGL \
            gcc openssl-devel libffi-devel \
            net-tools htop tree jq
    
    elif command -v dnf &> /dev/null; then
        echo "Detected dnf package manager"
        
        sudo dnf update -y
        sudo dnf install -y \
            git curl wget \
            python3 python3-pip python3-devel \
            docker docker-compose \
            nginx certbot python3-certbot-nginx \
            redis postgresql postgresql-server \
            ffmpeg mesa-libGL \
            gcc openssl-devel libffi-devel \
            net-tools htop tree jq
    
    elif command -v pacman &> /dev/null; then
        echo "Detected pacman package manager"
        
        sudo pacman -Syu --noconfirm
        sudo pacman -S --noconfirm \
            git curl wget \
            python python-pip \
            docker docker-compose \
            nginx certbot certbot-nginx \
            redis postgresql \
            ffmpeg mesa \
            base-devel openssl libffi \
            net-tools htop tree jq
    
    else
        echo -e "${RED}⚠  Unsupported package manager${NC}"
        exit 1
    fi
    
    # Enable and start services
    sudo systemctl enable docker
    sudo systemctl start docker
    
    sudo systemctl enable redis
    sudo systemctl start redis
    
    sudo systemctl enable postgresql
    sudo systemctl start postgresql
    
    echo -e "${GREEN}✓ System dependencies installed${NC}"
}

# Setup installation directory
setup_install_dir() {
    echo ""
    echo -e "${BLUE}📁 Setting up installation directory...${NC}"
    
    # Create directory
    sudo mkdir -p "$INSTALL_DIR"
    sudo chown -R $USER:$USER "$INSTALL_DIR"
    
    # Backup existing installation if exists
    if [[ -f "$INSTALL_DIR/docker-compose.yml" ]]; then
        echo "Backing up existing installation..."
        BACKUP_DIR="$INSTALL_DIR/backup_$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$BACKUP_DIR"
        cp -r "$INSTALL_DIR"/* "$BACKUP_DIR/" 2>/dev/null || true
        echo "Backup created at: $BACKUP_DIR"
    fi
    
    # Clean directory
    rm -rf "$INSTALL_DIR"/*
    
    cd "$INSTALL_DIR"
    echo -e "${GREEN}✓ Installation directory ready${NC}"
}

# Clone repository
clone_repository() {
    echo ""
    echo -e "${BLUE}📥 Cloning Roastify Pro repository...${NC}"
    
    # Clone from GitHub
    git clone "$REPO_URL" .
    
    # Check if clone was successful
    if [[ ! -f "docker-compose.yml" ]]; then
        echo -e "${RED}❌ Failed to clone repository${NC}"
        
        # Try alternative download method
        echo "Trying alternative download method..."
        curl -L "https://github.com/roastify/roastify-pro/archive/main.zip" -o roastify.zip
        unzip roastify.zip
        rm roastify.zip
        cp -r roastify-pro-main/* .
        rm -rf roastify-pro-main
    fi
    
    echo -e "${GREEN}✓ Repository cloned${NC}"
}

# Configure environment
configure_environment() {
    echo ""
    echo -e "${BLUE}⚙️  Configuring environment...${NC}"
    
    # Create .env file
    cat > .env << EOF
# Roastify Pro Production Environment
# Generated on $(date)

# ===== REQUIRED =====
BOT_TOKEN=$BOT_TOKEN
OWNER_ID=$OWNER_ID
ADMIN_IDS=$ADMIN_IDS

# ===== DOMAIN =====
DOMAIN=$DOMAIN
EMAIL=$EMAIL

# ===== DATABASE =====
POSTGRES_DB=roastify
POSTGRES_USER=roastify_admin
POSTGRES_PASSWORD=$(openssl rand -base64 32)
POSTGRES_HOST=db
POSTGRES_PORT=5432

# ===== REDIS =====
REDIS_PASSWORD=$(openssl rand -base64 32)
REDIS_HOST=redis
REDIS_PORT=6379

# ===== SECURITY =====
API_SECRET_KEY=$(openssl rand -base64 64)
JWT_SECRET=$(openssl rand -base64 64)
ENCRYPTION_KEY=$(openssl rand -base64 32)
SECURITY_SALT=$(openssl rand -base64 32)
HMAC_KEY=$(openssl rand -base64 64)

# ===== MONITORING =====
PROMETHEUS_PASSWORD=$(openssl rand -base64 16)
GRAFANA_PASSWORD=$(openssl rand -base64 16)

# ===== PERFORMANCE =====
WORKER_PROCESSES=4
CONNECTION_POOL_SIZE=20
CACHE_TTL=3600
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_BURST=150

# ===== STORAGE =====
MAX_UPLOAD_SIZE=10485760
BACKUP_RETENTION_DAYS=7

# ===== OPTIONAL =====
# TELEGRAM_API_ID=
# TELEGRAM_API_HASH=
# CLOUD_STORAGE_KEY=
# CLOUD_STORAGE_SECRET=

# ===== DEPLOYMENT =====
NODE_ENV=production
LOG_LEVEL=info
TZ=Asia/Dhaka
EOF
    
    echo -e "${GREEN}✓ Environment configured${NC}"
    echo -e "${YELLOW}⚠  Generated passwords saved to .env file${NC}"
}

# Setup Docker
setup_docker() {
    echo ""
    echo -e "${BLUE}🐳 Setting up Docker...${NC}"
    
    # Add user to docker group
    sudo usermod -aG docker $USER
    
    # Create Docker network
    docker network create roastify-network 2>/dev/null || true
    
    # Build Docker images
    echo "Building Docker images..."
    docker-compose build --no-cache --pull
    
    echo -e "${GREEN}✓ Docker setup complete${NC}"
}

# Initialize database
initialize_database() {
    echo ""
    echo -e "${BLUE}🗄️  Initializing database...${NC}"
    
    # Start database services
    docker-compose up -d db redis
    
    # Wait for services to be ready
    echo "Waiting for database to start..."
    sleep 10
    
    # Run database migrations
    echo "Running database migrations..."
    docker-compose run --rm bot python scripts/init_database.py
    
    # Create initial admin user
    echo "Creating admin user..."
    docker-compose exec db psql -U roastify_admin -d roastify -c "
        INSERT INTO users (user_id, username, first_name, last_name, is_premium, roast_count) 
        VALUES ($OWNER_ID, 'owner', 'System', 'Owner', true, 0)
        ON CONFLICT (user_id) DO NOTHING;
    "
    
    echo -e "${GREEN}✓ Database initialized${NC}"
}

# Setup SSL certificates
setup_ssl() {
    echo ""
    echo -e "${BLUE}🔐 Setting up SSL certificates...${NC}"
    
    # Create SSL directory
    mkdir -p ssl
    
    # Stop nginx if running
    sudo systemctl stop nginx 2>/dev/null || true
    
    # Generate self-signed certificates for initial setup
    echo "Generating self-signed certificates..."
    openssl req -x509 -newkey rsa:4096 \
        -keyout ssl/privkey.pem \
        -out ssl/fullchain.pem \
        -days 365 -nodes \
        -subj "/C=BD/ST=Dhaka/L=Dhaka/O=Roastify/CN=$DOMAIN"
    
    # Setup Nginx configuration
    echo "Configuring Nginx..."
    sudo cp deployment/nginx.conf /etc/nginx/sites-available/roastify
    sudo ln -sf /etc/nginx/sites-available/roastify /etc/nginx/sites-enabled/
    sudo nginx -t && sudo systemctl restart nginx
    
    echo -e "${GREEN}✓ SSL setup complete${NC}"
    echo -e "${YELLOW}⚠  Using self-signed certificates. Run certbot later for real certificates.${NC}"
}

# Start application
start_application() {
    echo ""
    echo -e "${BLUE}🚀 Starting application...${NC}"
    
    # Start all services
    docker-compose up -d
    
    # Wait for services to be ready
    echo "Waiting for services to start..."
    sleep 15
    
    # Health check
    echo "Performing health check..."
    if curl -f http://localhost:8080/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Application started successfully${NC}"
    else
        echo -e "${RED}❌ Application health check failed${NC}"
        docker-compose logs --tail=50
        exit 1
    fi
}

# Setup monitoring
setup_monitoring() {
    echo ""
    echo -e "${BLUE}📊 Setting up monitoring...${NC}"
    
    # Start monitoring stack
    docker-compose -f docker-compose.monitoring.yml up -d
    
    # Wait for monitoring to start
    sleep 10
    
    echo -e "${GREEN}✓ Monitoring setup complete${NC}"
}

# Setup backup system
setup_backup() {
    echo ""
    echo -e "${BLUE}💾 Setting up backup system...${NC}"
    
    # Make backup script executable
    chmod +x scripts/auto_backup.sh
    
    # Add to crontab
    (crontab -l 2>/dev/null; echo "0 2 * * * $INSTALL_DIR/scripts/auto_backup.sh") | crontab -
    
    echo -e "${GREEN}✓ Backup system configured${NC}"
}

# Setup firewall
setup_firewall() {
    echo ""
    echo -e "${BLUE}🔥 Setting up firewall...${NC}"
    
    # Check if ufw exists
    if command -v ufw &> /dev/null; then
        sudo ufw default deny incoming
        sudo ufw default allow outgoing
        sudo ufw allow 22/tcp
        sudo ufw allow 80/tcp
        sudo ufw allow 443/tcp
        echo "y" | sudo ufw enable
        echo -e "${GREEN}✓ Firewall configured${NC}"
    else
        echo -e "${YELLOW}⚠  UFW not available, skipping firewall setup${NC}"
    fi
}

# Final setup
final_setup() {
    echo ""
    echo -e "${BLUE}🎯 Final setup...${NC}"
    
    # Set proper permissions
    sudo chown -R $USER:$USER "$INSTALL_DIR"
    sudo chmod -R 750 "$INSTALL_DIR"
    
    # Create systemd service
    if [[ "$CLOUD_DEPLOY" == false ]]; then
        cat > roastify.service << EOF
[Unit]
Description=Roastify Pro Bot System
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$INSTALL_DIR
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
ExecReload=/usr/local/bin/docker-compose restart
User=$USER
Group=$USER

[Install]
WantedBy=multi-user.target
EOF
        
        sudo mv roastify.service /etc/systemd/system/
        sudo systemctl daemon-reload
        sudo systemctl enable roastify.service
        
        echo -e "${GREEN}✓ Systemd service created${NC}"
    fi
    
    # Create update script
    cat > update_roastify.sh << 'EOF'
#!/bin/bash
cd /opt/roastify
git pull
docker-compose pull
docker-compose up -d --build
docker system prune -f
EOF
    
    chmod +x update_roastify.sh
    echo -e "${GREEN}✓ Update script created${NC}"
}

# Run tests
run_tests() {
    echo ""
    echo -e "${BLUE}🧪 Running tests...${NC}"
    
    # Run smoke tests
    if docker-compose exec -T bot python -m pytest tests/smoke_test.py -v; then
        echo -e "${GREEN}✓ Smoke tests passed${NC}"
    else
        echo -e "${YELLOW}⚠  Smoke tests failed, but continuing...${NC}"
    fi
}

# Show completion message
show_completion() {
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                  INSTALLATION COMPLETE!                  ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${CYAN}🎉 Congratulations! Roastify Pro has been successfully installed.${NC}"
    echo ""
    
    # Get server IP
    SERVER_IP=$(curl -s ifconfig.me)
    
    # Show access information
    echo -e "${YELLOW}📱 ACCESS INFORMATION:${NC}"
    echo "════════════════════════════════════════"
    echo ""
    echo -e "${CYAN}🌐 Web Dashboard:${NC}"
    echo "   URL: https://$DOMAIN/admin"
    echo "   Default credentials:"
    echo "   - Username: admin"
    echo "   - Password: Check .env file (GRAFANA_PASSWORD)"
    echo ""
    echo -e "${CYAN}🤖 Telegram Bot:${NC}"
    echo "   Bot: @$(curl -s "https://api.telegram.org/bot$BOT_TOKEN/getMe" | jq -r '.result.username')"
    echo "   Start command: /start"
    echo ""
    echo -e "${CYAN}📊 Monitoring:${NC}"
    echo "   Grafana: https://$DOMAIN:3000"
    echo "   Prometheus: https://$DOMAIN:9090"
    echo ""
    echo -e "${CYAN}🔧 API Endpoints:${NC}"
    echo "   Health: https://$DOMAIN/health"
    echo "   API Docs: https://$DOMAIN/docs"
    echo "   Metrics: https://$DOMAIN/metrics"
    echo ""
    
    # Show credentials file location
    echo -e "${YELLOW}🔐 IMPORTANT SECURITY INFORMATION:${NC}"
    echo "════════════════════════════════════════"
    echo ""
    echo "Credentials are stored in: $INSTALL_DIR/.env"
    echo ""
    echo -e "${RED}⚠  IMPORTANT:${NC}"
    echo "1. Change all passwords in .env file"
    echo "2. Enable proper SSL certificates:"
    echo "   sudo certbot --nginx -d $DOMAIN"
    echo "3. Configure firewall: sudo ufw status"
    echo "4. Setup daily backups are scheduled"
    echo ""
    
    # Show management commands
    echo -e "${YELLOW}⚙️  MANAGEMENT COMMANDS:${NC}"
    echo "════════════════════════════════════════"
    echo ""
    echo "View logs:              docker-compose logs -f"
    echo "Restart bot:           docker-compose restart bot"
    echo "Update system:         ./update_roastify.sh"
    echo "Backup manually:       ./scripts/auto_backup.sh"
    echo "Check status:          docker-compose ps"
    echo "System logs:           sudo journalctl -u roastify -f"
    echo ""
    
    # Show next steps
    echo -e "${YELLOW}🚀 NEXT STEPS:${NC}"
    echo "════════════════════════════════════════"
    echo ""
    echo "1. Add bot to your Telegram groups"
    echo "2. Configure welcome messages"
    echo "3. Test image generation"
    echo "4. Setup monitoring alerts"
    echo "5. Configure auto-scaling (if needed)"
    echo ""
    
    # Final message
    echo -e "${GREEN}✅ Your bot is now running at: https://t.me/$(curl -s "https://api.telegram.org/bot$BOT_TOKEN/getMe" | jq -r '.result.username')${NC}"
    echo ""
    echo -e "${CYAN}Need help? Join our community: https://t.me/roastify_support${NC}"
    echo -e "${CYAN}Documentation: https://docs.roastify.com${NC}"
    echo ""
    echo -e "${MAGENTA}Thank you for choosing Roastify Pro! 🚀${NC}"
    echo ""
}

# Main installation function
main_installation() {
    print_banner
    
    # Parse arguments
    parse_arguments "$@"
    
    # Check requirements
    if [[ "$SKIP_CHECKS" == false ]]; then
        check_requirements
    fi
    
    # Interactive configuration
    interactive_config
    
    # Start installation
    echo ""
    echo -e "${MAGENTA}🚀 Starting installation process...${NC}"
    echo ""
    
    # Step 1: Install dependencies
    echo -e "${BLUE}[1/10] Installing dependencies...${NC}"
    install_dependencies
    
    # Step 2: Setup directory
    echo -e "${BLUE}[2/10] Setting up directory...${NC}"
    setup_install_dir
    
    # Step 3: Clone repository
    echo -e "${BLUE}[3/10] Cloning repository...${NC}"
    clone_repository
    
    # Step 4: Configure environment
    echo -e "${BLUE}[4/10] Configuring environment...${NC}"
    configure_environment
    
    # Step 5: Setup Docker
    echo -e "${BLUE}[5/10] Setting up Docker...${NC}"
    setup_docker
    
    # Step 6: Initialize database
    echo -e "${BLUE}[6/10] Initializing database...${NC}"
    initialize_database
    
    # Step 7: Setup SSL
    echo -e "${BLUE}[7/10] Setting up SSL...${NC}"
    setup_ssl
    
    # Step 8: Start application
    echo -e "${BLUE}[8/10] Starting application...${NC}"
    start_application
    
    # Step 9: Setup monitoring
    echo -e "${BLUE}[9/10] Setting up monitoring...${NC}"
    setup_monitoring
    
    # Step 10: Final setup
    echo -e "${BLUE}[10/10] Final setup...${NC}"
    setup_backup
    setup_firewall
    final_setup
    run_tests
    
    # Show completion message
    show_completion
    
    # Save installation log
    echo "Installation completed: $(date)" >> "$INSTALL_DIR/install.log"
}

# Error handler
error_handler() {
    echo -e "${RED}❌ Installation failed!${NC}"
    echo "Error occurred at: $(date)"
    echo "Check logs in: $INSTALL_DIR/install.log"
    exit 1
}

# Trap errors
trap error_handler ERR

# Run main installation
main_installation "$@"

# Exit successfully
exit 0
#!/bin/bash

# Roastify Pro - Auto Deployment Wizard
# Automated deployment with intelligent configuration

# ... [Previous setup code remains similar, adding wizard-specific features]

auto_detect_configuration() {
    echo -e "${CYAN}🎯 Auto-detecting configuration...${NC}"
    
    # Auto-detect domain from server
    if [[ -z "$DOMAIN" ]]; then
        SERVER_IP=$(curl -s ifconfig.me)
        DOMAIN="$SERVER_IP.nip.io"
        echo -e "  ✓ Auto-detected domain: $DOMAIN"
    fi
    
    # Auto-detect email
    if [[ -z "$EMAIL" ]]; then
        # Try to get from system
        SYSTEM_EMAIL=$(whoami)@$(hostname)
        if [[ "$SYSTEM_EMAIL" =~ @ ]]; then
            EMAIL="$SYSTEM_EMAIL"
            echo -e "  ✓ Auto-detected email: $EMAIL"
        fi
    fi
    
    # Test Telegram bot token
    if [[ -n "$BOT_TOKEN" ]]; then
        echo -e "  🔍 Testing bot token..."
        BOT_INFO=$(curl -s "https://api.telegram.org/bot$BOT_TOKEN/getMe")
        if echo "$BOT_INFO" | grep -q '"ok":true'; then
            BOT_USERNAME=$(echo "$BOT_INFO" | jq -r '.result.username')
            echo -e "  ✓ Bot token valid: @$BOT_USERNAME"
        else
            echo -e "  ❌ Invalid bot token"
            exit 1
        fi
    fi
    
    # Check port availability
    echo -e "  🔍 Checking port availability..."
    for port in 80 443 8080 3000 9090; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
            echo -e "  ⚠  Port $port is in use"
        else
            echo -e "  ✓ Port $port available"
        fi
    done
    
    # Check system resources
    echo -e "  🔍 Checking system resources..."
    CPU_CORES=$(nproc)
    RAM_GB=$(free -g | awk '/^Mem:/{print $2}')
    DISK_GB=$(df -BG / | awk 'NR==2 {print $4}' | sed 's/G//')
    
    echo -e "  ✓ CPU Cores: $CPU_CORES"
    echo -e "  ✓ RAM: ${RAM_GB}GB"
    echo -e "  ✓ Disk: ${DISK_GB}GB"
    
    # Recommend configuration based on resources
    if [[ $RAM_GB -ge 8 ]]; then
        echo -e "  🚀 High resource system detected"
        RECOMMENDED_WORKERS=8
        RECOMMENDED_CACHE=4096
    elif [[ $RAM_GB -ge 4 ]]; then
        echo -e "  ⚡ Medium resource system detected"
        RECOMMENDED_WORKERS=4
        RECOMMENDED_CACHE=2048
    else
        echo -e "  ⚠  Low resource system detected"
        RECOMMENDED_WORKERS=2
        RECOMMENDED_CACHE=1024
    fi
    
    echo -e "  💡 Recommended: $RECOMMENDED_WORKERS workers, ${RECOMMENDED_CACHE}MB cache"
}

deploy_to_cloud() {
    local cloud_provider=$1
    
    echo -e "${CYAN}☁️  Deploying to $cloud_provider...${NC}"
    
    case $cloud_provider in
        aws)
            deploy_aws
            ;;
        gcp)
            deploy_gcp
            ;;
        azure)
            deploy_azure
            ;;
        digitalocean)
            deploy_digitalocean
            ;;
        *)
            echo -e "${RED}Unsupported cloud provider${NC}"
            exit 1
            ;;
    esac
}

deploy_aws() {
    echo -e "${BLUE}Deploying to AWS...${NC}"
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        echo "Installing AWS CLI..."
        curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
        unzip awscliv2.zip
        sudo ./aws/install
    fi
    
    # Configure AWS
    if [[ ! -f ~/.aws/credentials ]]; then
        echo "AWS configuration required..."
        aws configure
    fi
    
    # Create CloudFormation stack
    echo "Creating CloudFormation stack..."
    aws cloudformation create-stack \
        --stack-name roastify-pro \
        --template-body file://deployment/aws/cloudformation.yml \
        --parameters \
            ParameterKey=DomainName,ParameterValue=$DOMAIN \
            ParameterKey=InstanceType,ParameterValue=t3.medium \
            ParameterKey=KeyName,ParameterValue=roastify-key \
        --capabilities CAPABILITY_IAM
    
    echo "Stack creation started. Check AWS Console for progress."
}

# ... [More deployment functions for other clouds]
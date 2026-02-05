#!/bin/bash
#
# Cloud Rosetta Installation Script
# Downloads and installs the latest version of Rosetta CLI
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO="gordonmurray/cloud-rosetta"
INSTALL_DIR="/usr/local/bin"
CLI_NAME="rosetta"

# Functions
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root for system-wide install
check_permissions() {
    if [[ $EUID -eq 0 ]]; then
        INSTALL_DIR="/usr/local/bin"
        NEEDS_SUDO=false
    else
        # Try to write to /usr/local/bin
        if [ -w "$INSTALL_DIR" ]; then
            NEEDS_SUDO=false
        else
            NEEDS_SUDO=true
        fi
    fi
}

# Install to user's local bin if no sudo
setup_local_install() {
    mkdir -p "$HOME/.local/bin"
    INSTALL_DIR="$HOME/.local/bin"
    NEEDS_SUDO=false
    
    # Add to PATH if not already there
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        print_warning "Adding $HOME/.local/bin to your PATH"
        
        # Add to appropriate shell config
        if [ -n "$ZSH_VERSION" ]; then
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
            print_warning "Please run: source ~/.zshrc"
        elif [ -n "$BASH_VERSION" ]; then
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
            print_warning "Please run: source ~/.bashrc"
        fi
    fi
}

# Main installation
install_rosetta() {
    print_status "Installing Cloud Rosetta CLI..."
    
    # Check permissions
    check_permissions
    
    # If can't write to system directory, use local
    if [ "$NEEDS_SUDO" = true ] && ! command -v sudo &> /dev/null; then
        print_warning "sudo not available, installing to user directory"
        setup_local_install
    fi
    
    # Download the CLI
    DOWNLOAD_URL="https://raw.githubusercontent.com/$REPO/main/rosetta"
    TEMP_FILE=$(mktemp)
    
    print_status "Downloading from: $DOWNLOAD_URL"
    
    if command -v curl &> /dev/null; then
        curl -fsSL "$DOWNLOAD_URL" -o "$TEMP_FILE"
    elif command -v wget &> /dev/null; then
        wget -q "$DOWNLOAD_URL" -O "$TEMP_FILE"
    else
        print_error "Neither curl nor wget found. Please install one of them."
        exit 1
    fi
    
    # Verify download
    if [ ! -s "$TEMP_FILE" ]; then
        print_error "Download failed or file is empty"
        exit 1
    fi
    
    # Check if it's a valid Python script
    if ! head -n1 "$TEMP_FILE" | grep -q python; then
        print_error "Downloaded file doesn't appear to be a valid Python script"
        exit 1
    fi
    
    # Install the file
    INSTALL_PATH="$INSTALL_DIR/$CLI_NAME"
    
    if [ "$NEEDS_SUDO" = true ]; then
        sudo cp "$TEMP_FILE" "$INSTALL_PATH"
        sudo chmod +x "$INSTALL_PATH"
    else
        cp "$TEMP_FILE" "$INSTALL_PATH"
        chmod +x "$INSTALL_PATH"
    fi
    
    # Cleanup
    rm "$TEMP_FILE"
    
    print_success "Rosetta CLI installed to: $INSTALL_PATH"
}

# Install dependencies
install_dependencies() {
    print_status "Checking dependencies..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required but not installed"
        print_status "Please install Python 3.8+ and try again"
        exit 1
    fi
    
    # Check Infracost
    if ! command -v infracost &> /dev/null; then
        print_status "Installing Infracost..."
        curl -fsSL https://raw.githubusercontent.com/infracost/infracost/master/scripts/install.sh | bash
    fi
    
    # Check Terraform/OpenTofu
    if ! command -v terraform &> /dev/null && ! command -v tofu &> /dev/null; then
        print_warning "Neither Terraform nor OpenTofu found"
        print_status "Please install one of them:"
        print_status "  Terraform: https://terraform.io/downloads"
        print_status "  OpenTofu: https://opentofu.org/docs/intro/install/"
    fi
}

# Test installation
test_installation() {
    print_status "Testing installation..."
    
    if command -v "$CLI_NAME" &> /dev/null; then
        $CLI_NAME --version >/dev/null 2>&1 || true
        print_success "Installation test passed!"
    else
        print_warning "CLI not found in PATH. You may need to restart your shell or run:"
        echo "  export PATH=\"$INSTALL_DIR:\$PATH\""
    fi
}

# Show usage info
show_usage() {
    print_success "Cloud Rosetta CLI installed successfully!"
    echo
    echo "Quick start:"
    echo "  cd your-terraform-project/"
    echo "  terraform plan"
    echo "  rosetta --provider aws      # Get AWS costs"
    echo "  rosetta --provider ovh      # Translate to OVH and estimate"
    echo "  rosetta --provider hetzner  # Translate to Hetzner and estimate"
    echo
    echo "For more information:"
    echo "  rosetta --help"
    echo "  https://github.com/$REPO"
}

# Main execution
main() {
    echo -e "${BLUE}"
    cat << "EOF"
    ______ _                 _   ______                _   _        
    |  ___| |               | |  | ___ \              | | | |       
    | |__ | | ___  _   _  __| |  | |_/ /___  ___  ___ | |_| |_ __ _ 
    |  __|| |/ _ \| | | |/ _` |  |    // _ \/ __|/ _ \| __| __/ _` |
    | |___| | (_) | |_| | (_| |  | |\ \ (_) \__ \  __/| |_| || (_| |
    \____/|_|\___/ \__,_|\__,_|  \_| \_\___/|___/\___| \__|\__\__,_|
                                                                    
    Universal Cloud Cost Translator
EOF
    echo -e "${NC}"
    
    install_dependencies
    install_rosetta
    test_installation
    show_usage
}

# Run main function
main "$@"
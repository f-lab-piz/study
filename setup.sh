#!/bin/bash
set -e

echo "🚀 Setting up development environment..."

# Install Node.js (required for Claude Code)
echo "🟢 Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install UV (Python package manager)
echo "🐍 Installing UV..."
curl -LsSf https://astral.sh/uv/install.sh | sh
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.zshrc

# Create persistent Claude directory
# echo "📁 Creating persistent Claude directory..."

# Install Claude Code (after Node.js)
echo "🤖 Installing Claude Code..."
npm install -g @anthropic-ai/claude-code

# Install zsh-autosuggestions plugin for oh-my-zsh
echo "⚡ Installing zsh-autosuggestions..."
git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions

# Configure zsh plugins and aliases
echo "🔧 Configuring zsh..."
# Backup existing .zshrc if it exists
if [ -f ~/.zshrc ]; then
    cp ~/.zshrc ~/.zshrc.backup
fi

# Update .zshrc with plugins and alias
cat > ~/.zshrc << 'EOF'
# Path to your oh-my-zsh installation.
export ZSH="$HOME/.oh-my-zsh"

# Set name of the theme to load
ZSH_THEME="robbyrussell"

# Which plugins would you like to load?
plugins=(git zsh-autosuggestions)

source $ZSH/oh-my-zsh.sh

# User configuration
export PATH="$HOME/.cargo/bin:$PATH"

# Claude Code persistent storage
# export CLAUDE_CONFIG_DIR="/workspaces/.claude-persistent"
# export CLAUDE_DATA_DIR="/workspaces/.claude-persistent"

# Custom aliases
alias gitl='git log --graph --oneline --all --decorate=short --pretty=format:"%h %d : %s [%an, %ar]"'
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'

EOF

# Source the new configuration
source ~/.zshrc || true

echo "✅ Development environment setup complete!"
echo "🔄 Please restart your terminal or run 'source ~/.zshrc' to apply changes."
echo ""
echo "📋 Installed tools:"
echo "  - Docker & Docker Compose"
echo "  - Node.js & npm"
echo "  - UV (Python package manager)"
echo "  - Essential tools: curl, wget, tree, htop, jq, ripgrep"
echo "  - Text editors: vim, neovim"
echo "  - zsh with oh-my-zsh"
echo "  - zsh-autosuggestions plugin"
echo "  - gitl alias for git log"
echo "  - Claude Code CLI"

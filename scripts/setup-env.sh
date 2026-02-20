#!/usr/bin/env bash
# MiMind - 环境配置脚本
# 用于安装 uv 和 Specify CLI（当网络可用时运行）

set -e

echo "=== MiMind 环境配置 ==="

# 1. 安装 uv
if command -v uv &>/dev/null; then
    echo "✓ uv 已安装: $(uv --version)"
else
    echo "正在安装 uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

# 2. 安装 Specify CLI
if command -v specify &>/dev/null; then
    echo "✓ specify 已安装"
else
    echo "正在安装 Specify CLI..."
    uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
fi

# 3. 验证
echo ""
echo "运行 specify check 验证..."
specify check 2>/dev/null || echo "specify check 可能需要 cursor-agent 等工具"

echo ""
echo "=== 配置完成 ==="
echo "在项目目录运行以下命令初始化 Spec Kit（若尚未初始化）："
echo "  specify init . --ai cursor-agent --force"
echo ""
echo "项目已包含 .specify/ 和 .cursor/commands/，可直接使用 /speckit.* 和 /autodev 命令。"

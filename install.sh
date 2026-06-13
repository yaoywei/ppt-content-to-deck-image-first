#!/usr/bin/env bash
# ppt-content-to-deck-image-first 一键安装脚本
# 用法: curl -fsSL https://raw.githubusercontent.com/yaoywei/ppt-content-to-deck-image-first/main/install.sh | bash
# 作用: 把这个 skill 安装到 ~/.hermes/skills/ppt-content-to-deck-image-first/

set -e

REPO_URL="https://github.com/yaoywei/ppt-content-to-deck-image-first.git"
SKILL_NAME="ppt-content-to-deck-image-first"
SKILL_DIR="${HOME}/.hermes/skills/${SKILL_NAME}"

echo "🚀 安装 ${SKILL_NAME} skill"
echo "================================"

# 1. 检查依赖
if ! command -v git &> /dev/null; then
  echo "❌ 错误: 需要 git，请先安装 git"
  exit 1
fi

# 2. 检查是否已安装
if [ -d "${SKILL_DIR}" ]; then
  echo "⚠️  ${SKILL_NAME} 已经安装在 ${SKILL_DIR}"
  read -p "是否覆盖? [y/N] " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 取消安装"
    exit 1
  fi
  rm -rf "${SKILL_DIR}"
fi

# 3. 克隆仓库
echo "📥 克隆仓库..."
git clone --depth 1 "${REPO_URL}" "${SKILL_DIR}"

# 4. 验证 SKILL.md
if [ ! -f "${SKILL_DIR}/SKILL.md" ]; then
  echo "❌ 安装失败: SKILL.md 不存在"
  exit 1
fi

# 5. 完成
echo ""
echo "✅ 安装成功!"
echo "📁 位置: ${SKILL_DIR}"
echo ""
echo "🎯 使用方法:"
echo "   1. 重启 Hermes (或重新加载 skills)"
echo "   2. 用关键词触发: '用 ppt-content-to-deck-image-first 风格 给[公司名]做公司简介 PPT'"
echo "   3. 或: '这份 PPT 给领导看，风格按湖南驰阳介绍来'"
echo ""
echo "📖 文档: ${SKILL_DIR}/SKILL.md"
echo "🌐 仓库: ${REPO_URL}"
echo ""
echo "📸 风格示例: 打开 README.md 即可看到 5 种风格的真实样图 (无需运行 image_generate)"
echo ""

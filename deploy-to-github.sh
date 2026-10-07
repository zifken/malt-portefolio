#!/usr/bin/env bash
# deploy-to-github.sh — crée le repo GitHub et pousse le portfolio
# À exécuter après `gh auth login` (authentification GitHub CLI)
set -euo pipefail

REPO_NAME="data-portfolio"
DEPLOY_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "🚀 Déploiement du portfolio data sur GitHub"
echo "=========================================="
echo "Repo: $REPO_NAME"
echo "Dossier: $DEPLOY_DIR"
echo ""

# Vérifier que gh est authentifié
if ! gh auth status &>/dev/null; then
    echo "❌ Vous n'êtes pas authentifié sur GitHub."
    echo "   Lancez d'abord: gh auth login"
    echo "   (choisissez GitHub.com → HTTPS → Login with web browser)"
    exit 1
fi

echo "✅ Authentifié sur GitHub"

# Vérifier que le repo n'existe pas déjà
if gh repo view "$REPO_NAME" &>/dev/null; then
    echo "⚠️  Le repo $REPO_NAME existe déjà. Push uniquement."
    cd "$DEPLOY_DIR"
    git remote set-url origin "https://github.com/$(gh api user --jq .login)/$REPO_NAME.git" 2>/dev/null || \
        git remote add origin "https://github.com/$(gh api user --jq .login)/$REPO_NAME.git"
    git push -u origin main
else
    echo "📦 Création du repo public $REPO_NAME..."
    cd "$DEPLOY_DIR"
    gh repo create "$REPO_NAME" --public --source=. --remote=origin --push
fi

echo ""
echo "✅ Repo poussé avec succès !"
echo "   URL: https://github.com/$(gh api user --jq .login)/$REPO_NAME"
echo ""
echo "📋 Prochaines étapes — déploiement Streamlit Cloud :"
echo "   1. Allez sur https://share.streamlit.io"
echo "   2. New app → Repository: $(gh api user --jq .login)/data-portfolio"
echo "   3. Main file path: immobilier/app.py → Deploy"
echo "   4. Répétez avec carburants/app.py et marches-publics/app.py"
echo "   5. Récupérez les 3 URLs et mettez à jour MALT_PROFILE_FINAL.md"
echo ""
echo "📖 Voir ~/opendata/DEPLOYMENT.md pour le guide détaillé"

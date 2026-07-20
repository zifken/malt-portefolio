#!/usr/bin/env bash
# create-malt-portfolio.sh — authentifie GitHub, crée le repo "malt portefolio", pousse les 3 projets
# Usage: ./create-malt-portfolio.sh <your-github-token>
set -euo pipefail

if [ -z "${1:-}" ]; then
    echo "❌ Usage: $0 <github-token>"
    echo "   Créez un token sur https://github.com/settings/tokens (classic, scope: repo)"
    echo "   Puis: $0 ghp_xxxxxxxxxxxx"
    exit 1
fi

TOKEN="$1"
REPO_NAME="malt portefolio"
DEPLOY_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "🚀 Création du repo GitHub « malt portefolio »"
echo "================================================"

# Authentification avec le token
echo "$TOKEN" | gh auth login --with-token 2>&1
echo "✅ Authentifié sur GitHub en tant que: $(gh api user --jq .login)"

# Vérifier si le repo existe déjà (gérer le nom avec espace)
REPO_SLUG="malt-portefolio"
USER="$(gh api user --jq .login)"

# Créer le repo (public)
if gh repo view "$USER/$REPO_SLUG" &>/dev/null; then
    echo "⚠️  Le repo $REPO_SLUG existe déjà — push uniquement."
else
    echo "📦 Création du repo public « $REPO_NAME »..."
    gh repo create "$REPO_SLUG" --public --description "Portfolio Data Science — 3 projets open data France (immobilier, carburants, marchés publics) pour profil Malt.fr" 2>&1
    echo "✅ Repo créé: https://github.com/$USER/$REPO_SLUG"
fi

# Configurer le remote et pousser
cd "$DEPLOY_DIR"
git remote remove origin 2>/dev/null || true
git remote add origin "https://$USER:$TOKEN@github.com/$USER/$REPO_SLUG.git"
echo "📤 Push du code..."
git push -u origin main 2>&1

echo ""
echo "================================================"
echo "✅ SUCCÈS ! Repo en ligne :"
echo "   https://github.com/$USER/$REPO_SLUG"
echo ""
echo "📋 Les 3 apps sont aussi accessibles en ligne :"
echo "   🏠 Immobilier : https://dictionaries-gentleman-spare-consequence.trycloudflare.com"
echo "   ⛽ Carburants : https://lotus-reform-interim-culture.trycloudflare.com"
echo "   🏛️ Marchés    : https://subscriber-highlight-significance-html.trycloudflare.com"
echo ""
echo "📖 Profil Malt final (avec liens) : ~/opendata/MALT_PROFILE_FINAL.md"

#!/usr/bin/env bash
# One-time Codespace/devcontainer setup: clones the sibling Rubra repos,
# installs the full stack, and installs kubectl/helm/kind for rubra-deploy
# testing. Ollama itself is started separately in start-ollama.sh (runs on
# every container start, not just creation).
set -euo pipefail

echo "==> Cloning sibling repos into /workspaces"
cd /workspaces
[ -d rubra-sdk ]    || git clone --depth 1 https://github.com/pm1715/rubra-sdk.git
[ -d rubra-deploy ] || git clone --depth 1 https://github.com/pm1715/rubra-deploy.git
mkdir -p /workspaces/.rubra-shared

echo "==> Installing rubra-sdk (editable, all extras)"
pip install --quiet --upgrade pip
pip install --quiet -e "/workspaces/rubra-sdk[all]"

echo "==> Installing rubra-server (editable, dev extras)"
pip install --quiet -e "/workspaces/rubra-server[dev]"

echo "==> Installing kubectl"
KUBECTL_VERSION="$(curl -L -s https://dl.k8s.io/release/stable.txt)"
curl -sLO "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/amd64/kubectl"
chmod +x kubectl && sudo mv kubectl /usr/local/bin/kubectl

echo "==> Installing Helm"
curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

echo "==> Installing kind"
curl -sLo /tmp/kind https://kind.sigs.k8s.io/dl/latest/kind-linux-amd64
chmod +x /tmp/kind && sudo mv /tmp/kind /usr/local/bin/kind

echo "==> Installing Ollama"
curl -fsSL https://ollama.com/install.sh | sh

echo "==> Setup complete."
echo "    - rubra-sdk, rubra-server, rubra-deploy are all installed/cloned under /workspaces"
echo "    - kubectl, helm, kind are ready for rubra-deploy testing"
echo "    - Ollama will start automatically and pull its model (see start-ollama.sh)"

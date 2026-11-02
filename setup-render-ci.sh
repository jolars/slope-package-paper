#!/usr/bin/env bash

set -euo pipefail

: "${GITHUB_ENV:?This hook requires the GitHub Actions environment file.}"
: "${GITHUB_PATH:?This hook requires the GitHub Actions path file.}"

cd "$(dirname "${BASH_SOURCE[0]}")"

bootstrap_dir=$(mktemp -d)
trap 'rm -rf "$bootstrap_dir"' EXIT

if ! command -v nix >/dev/null 2>&1; then
  curl --fail --location --retry 3 \
    https://releases.nixos.org/nix/nix-2.34.9/install \
    --output "$bootstrap_dir/install-nix"
  printf '%s  %s\n' \
    a03ce2e9eaf4ea1560260b9a93e311dbaf589d28fb5c9318f8d9e768ee6339d8 \
    "$bootstrap_dir/install-nix" | sha256sum --check

  sudo install -d -m 0755 -o "$(id -u)" -g "$(id -g)" /nix
  sh "$bootstrap_dir/install-nix" \
    --no-daemon --no-channel-add --no-modify-profile
  # GitHub's noninteractive steps do not load Nix's profile automatically.
  source "$HOME/.nix-profile/etc/profile.d/nix.sh"
fi

export NIX_CONFIG="${NIX_CONFIG:-}
experimental-features = nix-command flakes
build-users-group =
sandbox = false
extra-substituters = https://devenv.cachix.org https://cachix.cachix.org
extra-trusted-public-keys = devenv.cachix.org-1:w1cLUi8dv3hnoSPGAuibQv+f9TZLr6cv/Hm9XgU50cw= cachix.cachix.org-1:eWNHQldwUO7G2VkjpnjDbWwy4KQ/HNxht7H4SSoMckM="

# The locked nixpkgs predates the CLI used with this project's devenv modules.
devenv_profile="$bootstrap_dir/devenv"
nix profile add --profile "$devenv_profile" \
  github:cachix/devenv/b904dcb51fe48c30db250038241507f60752f222#devenv

"$devenv_profile/bin/devenv" --no-tui shell -- \
  python code/export_computo_env.py

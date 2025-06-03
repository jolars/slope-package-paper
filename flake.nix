{
  description = "A basic flake with a shell";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  inputs.systems.url = "github:nix-systems/default";
  inputs.flake-utils = {
    url = "github:numtide/flake-utils";
    inputs.systems.follows = "systems";
  };

  outputs =
    { nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        SLOPE = (
          pkgs.rPackages.buildRPackage {
            name = "SLOPE";
            src = pkgs.fetchFromGitHub {
              owner = "jolars";
              repo = "SLOPE";
              rev = "0007c493ad961d87d10c3781e2711ba543835103";
              hash = "sha256-TEcm+iIaOqoFgmK2/S9DJNFsvV2s+q3hHal/w9UdPwQ=";
            };
            propagatedBuildInputs = with pkgs.rPackages; [
              Matrix
              Rcpp
              RcppEigen
              SparseM
              bigmemory
              BH
            ];
          }
        );
      in
      {
        devShells.default = pkgs.mkShell {
          packages = with pkgs; [
            bashInteractive
            (rWrapper.override {
              packages = with rPackages; [
                here
                knitr
                lars
                languageserver
                SLOPE
                ggplot2
              ];
            })
          ];
        };
      }
    );
}

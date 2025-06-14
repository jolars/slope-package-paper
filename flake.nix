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

        sortedl1 = (
          pkgs.python3.pkgs.buildPythonPackage rec {
            pname = "sortedl1";
            version = "1.1.0";
            pyproject = true;

            src = pkgs.fetchPypi {
              inherit pname version;
              hash = "sha256-bon1d6r18eayuqhhK8zAckFWGSilX3eUc213HSeO2dQ=";
            };

            dontUseCmakeConfigure = true;

            build-system = [
              pkgs.python3.pkgs.scikit-build-core
              pkgs.python3.pkgs.pybind11
              pkgs.cmake
              pkgs.ninja
            ];

            dependencies = with pkgs.python3.pkgs; [
              numpy
              scikit-learn
              scipy
              furo
              sphinx-copybutton
              myst-parser
              pytest
            ];

            disabledTests = [
              "test_cdist"
            ];

            pythonImportsCheck = [
              "sortedl1"
            ];
          }
        );

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
            apptainer
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
            (python3.withPackages (ps: [
              ps.matplotlib
              ps.numpy
              ps.pandas
              sortedl1
            ]))
          ];
        };
      }
    );
}

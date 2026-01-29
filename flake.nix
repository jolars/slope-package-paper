{
  description = "A basic flake with a shell";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  inputs.systems.url = "github:nix-systems/default";
  inputs.flake-utils = {
    url = "github:numtide/flake-utils";
    inputs.systems.follows = "systems";
  };
  inputs.libslope.url = "github:jolars/libslope";
  inputs.libslope.inputs.nixpkgs.follows = "nixpkgs";

  outputs =
    {
      nixpkgs,
      libslope,
      flake-utils,
      ...
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        sortedl1 = (
          pkgs.python3.pkgs.buildPythonPackage rec {
            pname = "sortedl1";
            version = "1.9.0";
            pyproject = true;

            src = pkgs.fetchFromGitHub {
              owner = "jolars";
              repo = "sortedl1";
              rev = "v${version}";
              hash = "sha256-ERBFFkqwRXVrxylDHb0xvfOY16QpLoX65/CAVgwqOG8=";
            };

            dontUseCmakeConfigure = true;

            nativeBuildInputs = [
              pkgs.cmake
              pkgs.ninja
              pkgs.eigen
            ];

            buildInputs = [
              pkgs.eigen
              libslope.packages.${system}.default
            ];

            build-system = [
              pkgs.python3.pkgs.scikit-build-core
              pkgs.python3.pkgs.pybind11
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
          pkgs.rPackages.buildRPackage rec {
            name = "SLOPE";
            version = "2.0.0";
            src = pkgs.fetchFromGitHub {
              owner = "jolars";
              repo = "SLOPE";
              rev = "v${version}";
              hash = "sha256-3JsxyvbzIQdj3KMvwsO1bwEpkXkFJnIUdy08Is5mERE=";
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

        exampleCpp = pkgs.stdenv.mkDerivation {
          name = "slope-example";
          src = ./code;

          nativeBuildInputs = [
            pkgs.cmake
          ];

          buildInputs = [
            libslope.packages.${system}.default
            pkgs.eigen
          ];
        };
      in
      {
        devShells.default = pkgs.mkShell {
          packages = with pkgs; [
            libslope.packages.${system}.default
            bashInteractive
            apptainer
            go-task
            (rWrapper.override {
              packages = with rPackages; [
                here
                knitr
                lars
                languageserver
                SLOPE
                ggplot2
                MLmetrics
                tinytex
                caret
                dplyr
                glmnet
                pROC
                readxl
              ];
            })
            (python3.withPackages (ps: [
              ps.matplotlib
              ps.numpy
              ps.pandas
              ps.pyarrow
              ps.scipy
              ps.scipy-stubs
              ps.fastparquet
              ps.ipython
              sortedl1
            ]))
            (pkgs.julia-bin.withPackages [
              "SLOPE"
              "Plots"
              "LaTeXStrings"
              "LinearAlgebra"
              "ProjectRoot"
              "SparseArrays"
              "CSV"
              "DataFrames"
            ])
            exampleCpp
          ];
        };
      }
    );
}

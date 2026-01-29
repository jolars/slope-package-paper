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
              # rev = "v${version}";
              rev = "3025946be951368b6be80e9fc2df549a043ef54e";
              hash = "sha256-5OmNjom8i/LgkeyfaI+kMbKSJ9MXHo1s0iqYcSWihcc=";
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

            # preConfigure = ''
            #   export CMAKE_PREFIX_PATH="${libslope.packages.${system}.default}:${pkgs.eigen}:$CMAKE_PREFIX_PATH"
            # '';

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

          buildInputs = [
            libslope.packages.${system}.default
            pkgs.eigen
          ];

          buildPhase = ''
            $CXX example.cpp -o slope-example \
              -I${libslope.packages.${system}.default}/include \
              -I${pkgs.eigen}/include/eigen3 \
              -L${libslope.packages.${system}.default}/lib \
              -lslope -std=c++17
          '';

          installPhase = ''
            mkdir -p $out/bin
            cp slope-example $out/bin/
          '';
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

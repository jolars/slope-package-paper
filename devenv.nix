{
  inputs,
  pkgs,
  ...
}:

let
  system = pkgs.stdenv.hostPlatform.system;
  libslope = inputs.libslope.packages.${system}.default;
  libslopeVersion = "6.5.4";
  sortedl1Version = "1.11.2";
  slopeRVersion = "2.1.1";
  slopeJuliaVersion = "1.3.1";

  sortedl1 = pkgs.python3.pkgs.buildPythonPackage {
    pname = "sortedl1";
    version = sortedl1Version;
    pyproject = true;

    src = pkgs.fetchFromGitHub {
      owner = "jolars";
      repo = "sortedl1";
      rev = "v${sortedl1Version}";
      hash = "sha256-oIPQ1eGeMZPt92EjJ/mPwel2fwUQIYeekDXFnBT6tnw=";
    };

    dontUseCmakeConfigure = true;

    nativeBuildInputs = [
      pkgs.cmake
      pkgs.ninja
      pkgs.eigen
    ];

    buildInputs = [
      pkgs.eigen
      libslope
    ];

    build-system = with pkgs.python3.pkgs; [
      scikit-build-core
      pybind11
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
  };

  SLOPE = pkgs.rPackages.buildRPackage {
    name = "SLOPE";
    version = slopeRVersion;
    src = pkgs.fetchFromGitHub {
      owner = "jolars";
      repo = "SLOPE";
      rev = "v${slopeRVersion}";
      hash = "sha256-9NebMi+OpRyS+whHVKvLm+sAtICWuM/wKRDEWM6HkHI=";
    };
    propagatedBuildInputs = with pkgs.rPackages; [
      Matrix
      Rcpp
      RcppEigen
      SparseM
      bigmemory
      BH
    ];
  };

  exampleCpp = pkgs.stdenv.mkDerivation {
    name = "slope-example";
    src = ./code;

    nativeBuildInputs = [
      pkgs.cmake
    ];

    buildInputs = [
      libslope
      pkgs.eigen
    ];
  };
in
{
  packages = with pkgs; [
    libslope
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
    julia-bin
    exampleCpp
  ];

  enterTest = ''
    test "$(printf %s '${libslope.version}')" = "${libslopeVersion}"
    python -c 'import importlib.metadata; assert importlib.metadata.version("sortedl1") == "${sortedl1Version}"'
    Rscript -e 'stopifnot(as.character(packageVersion("SLOPE")) == "${slopeRVersion}")'
    julia --project=. -e 'using Pkg; Pkg.instantiate(); using SLOPE; versions = [dep.version for dep in values(Pkg.dependencies()) if dep.name == "SLOPE"]; @assert only(versions) == v"${slopeJuliaVersion}"'
    slope-example >/dev/null
  '';
}

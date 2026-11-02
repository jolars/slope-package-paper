{
  config,
  inputs,
  pkgs,
  lib,
  ...
}:

let
  system = pkgs.stdenv.hostPlatform.system;
  libslope = inputs.libslope.packages.${system}.default;
  libslopeVersion = "6.5.4";
  sortedl1Version = "1.11.3";
  slopeRVersion = "2.1.1";
  slopeJuliaVersion = "1.3.1";
  benchmarkPackages = import ./nix/benchmark-python-packages.nix { inherit pkgs; };
  patchedMetewand = pkgs.applyPatches {
    name = "metewand-source";
    src = inputs.metewand;
    patches = [ ./nix/metewand.patch ];
  };
  rustPkgs = pkgs.extend (import inputs.rust-overlay);
  metewandPackages = import ./nix/metewand.nix {
    inherit pkgs;
    source = config.slopeBenchmark.metewandSource;
    toolchain = rustPkgs.rust-bin.fromRustupToolchainFile (inputs.metewand + "/rust-toolchain.toml");
  };
  singlePythonPackages = ps: [
    ps.appdirs
    ps.numba
    ps.rpy2
    ps.scikit-learn
    benchmarkPackages.tick
    metewandPackages.python
    ps.pyyaml
    benchmarkPackages.libsvmdata
    benchmarkPackages.skglm
    benchmarkPackages.slopePath
    benchmarkPackages.slopescreening
    sortedl1
  ];
  benchmarkPythonPackages = ps: singlePythonPackages ps ++ [ benchmarkPackages.benchopt ];
  benchmarkPython = pkgs.python3.withPackages benchmarkPythonPackages;
  singlePython = pkgs.python3.withPackages singlePythonPackages;
  singleWorker =
    pkgs.runCommand "slope-single-python" { nativeBuildInputs = [ pkgs.makeWrapper ]; }
      ''
        mkdir -p "$out/bin"
        makeWrapper ${singlePython}/bin/python3 "$out/bin/python3" \
          --prefix PATH : ${pkgs.R}/bin --set R_HOME ${pkgs.R}/lib/R
      '';
  developmentPython = pkgs.python3.withPackages (
    ps:
    benchmarkPythonPackages ps
    ++ [
      ps.matplotlib
      ps.numpy
      ps.pandas
      ps.pyarrow
      ps.scipy
      ps.scipy-stubs
      ps.fastparquet
      ps.ipython
    ]
  );
  renderTex = pkgs.texlive.combine {
    inherit (pkgs.texlive)
      scheme-small
      collection-latexextra
      collection-luatex
      algorithms
      algorithmicx
      collection-xetex
      cm-super
      dvipng
      libertinus
      libertinus-fonts
      libertinus-otf
      lm
      latexmk
      mathtools
      pdfcrop
      siunitx
      type1cm
      ;
  };
  benchmarkSource = lib.cleanSourceWith {
    name = "slope-benchmark-source";
    src = ./.;
    filter =
      path: type:
      let
        relative = lib.removePrefix (toString ./. + "/") (toString path);
        top = builtins.head (lib.splitString "/" relative);
      in
      (
        toString path == toString ./.
        || builtins.elem top [
          "bench_config_path.yml"
          "bench_config_smoke_path.yml"
          "bench_config_smoke_single.yml"
          "bench_config_single.yml"
          "benchmark_slope"
          "benchmark_slope_path"
        ]
      )
      && !(builtins.elem (baseNameOf path) [
        ".git"
        ".github"
        ".devenv"
        ".pytest_cache"
        "__pycache__"
        "__cache__"
        "outputs"
      ])
      && !(lib.hasSuffix ".pyc" relative);
  };
  prepareBenchmarkData = ''
    benchmark_data_dir="''${SLOPE_BENCHMARK_DATA_DIR:-$PWD/.benchmark-data}"
    mkdir -p "$benchmark_data_dir/cache" "$benchmark_data_dir/libsvm"
    export LIBSVMDATA_HOME="$benchmark_data_dir/libsvm"
    export XDG_CACHE_HOME="$benchmark_data_dir/cache"
  '';

  sortedl1 = pkgs.python3.pkgs.buildPythonPackage {
    pname = "sortedl1";
    version = sortedl1Version;
    pyproject = true;

    src = pkgs.fetchFromGitHub {
      owner = "jolars";
      repo = "sortedl1";
      rev = "v${sortedl1Version}";
      hash = "sha256-86DCJ8LjwTXLmuCz2oo+Bi982FNb1IHns3m1XwQysw8=";
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
  options.slopeBenchmark.metewandSource = lib.mkOption {
    type = lib.types.path;
    default = patchedMetewand;
    description = "Metewand source, optionally overridden with a local development checkout.";
  };

  config = {
    env = {
      PYTHONHASHSEED = "0";
    }
    // pkgs.lib.optionalAttrs (!config.container.isBuilding) {
      # Keep personal Pandoc overrides from changing Quarto's document model.
      QUARTO_PANDOC = "${pkgs.pandoc}/bin/pandoc";
    };

    packages =
      with pkgs;
      [
        bashInteractive
        git
        util-linux
        metewandPackages.cli
      ]
      ++ lib.optionals config.container.isBuilding [
        R
        benchmarkPython
      ]
      ++ lib.optionals (!config.container.isBuilding) [
        libslope
        apptainer
        cmake
        eigen
        ghostscript
        go-task
        librsvg
        poppler-utils
        quartoMinimal
        renderTex
        (rWrapper.override {
          packages = with rPackages; [
            here
            knitr
            lars
            languageserver
            SLOPE
            ggplot2
            tinytex
            caret
            dplyr
            glmnet
            pROC
            readxl
            rmarkdown
            svglite
          ];
        })
        developmentPython
        julia-bin
        exampleCpp
      ];

    scripts.benchmark-single = {
      description = "Run the pinned single-penalty benchmark";
      exec = ''
        test -d benchmark_slope || {
          echo "Run benchmark-single from the repository root." >&2
          exit 1
        }
        ${prepareBenchmarkData}
        export PATH="${singleWorker}/bin:$PATH"
        mkdir -p benchmark_slope/outputs "$benchmark_data_dir"
        have_output=false
        for argument in "$@"; do
          if [ "$argument" = --output-dir ]; then have_output=true; fi
        done
        if ! "$have_output"; then
          set -- --output-dir "benchmark_slope/outputs/run-$(date +%Y%m%d-%H%M%S-%N)" "$@"
        fi
        exec metewand run --manifest bench_config_single.yml \
          --cache-dir "$benchmark_data_dir/metewand" "$@"
      '';
    };

    scripts.benchmark-path = {
      description = "Run the pinned solution-path benchmark";
      exec = ''
        test -d benchmark_slope_path || {
          echo "Run benchmark-path from the repository root." >&2
          exit 1
        }
        ${prepareBenchmarkData}
        exec benchopt run ./benchmark_slope_path --config bench_config_path.yml \
          --no-cache --timeout 30 "$@"
      '';
    };

    scripts.benchmark-environment = {
      description = "Print benchmark software, source, hardware, and thread settings";
      exec = ''
        python - <<'PY'
        from importlib.metadata import version

        packages = (
            "benchopt",
            "metewand",
            "libsvmdata",
            "numpy",
            "scikit-learn",
            "scipy",
            "skglm",
            "slopepath",
            "slopescreening",
            "sortedl1",
            "tick",
        )
        for package in packages:
            print(f"{package}: {version(package)}")
        PY
        metewand --version
        python --version
        Rscript -e 'cat("R:", R.version.string, "\n")'
        printf 'libslope: %s\n' '${libslopeVersion}'
        printf 'nixpkgs: %s\n' '${inputs.nixpkgs.rev}'
        printf 'benchmark source: %s\n' '${benchmarkSource}'
        if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
          printf 'paper: %s\n' "$(git rev-parse HEAD)"
          git submodule status --recursive
        fi
        for variable in \
          BLIS_NUM_THREADS MKL_NUM_THREADS NUMEXPR_NUM_THREADS OMP_DYNAMIC \
          OMP_NUM_THREADS OPENBLAS_NUM_THREADS PYTHONHASHSEED \
          VECLIB_MAXIMUM_THREADS; do
          printf '%s: %s\n' "$variable" "''${!variable}"
        done
        uname -a
        lscpu
      '';
    };

    scripts.benchmark-smoke = {
      description = "Run fast checks through both pinned benchmark suites";
      exec = ''
        test -d benchmark_slope && test -d benchmark_slope_path || {
          echo "Initialize the submodules and run benchmark-smoke from the repository root." >&2
          exit 1
        }
        ${prepareBenchmarkData}
        export PATH="${singleWorker}/bin:$PATH"
        mkdir -p benchmark_slope/outputs "$benchmark_data_dir"
        metewand check --manifest bench_config_smoke_single.yml --workers
        metewand run --manifest bench_config_smoke_single.yml \
          --cache-dir "$benchmark_data_dir/metewand" \
          --output-dir "benchmark_slope/outputs/smoke-$(date +%Y%m%d-%H%M%S-%N)"
        benchopt run ./benchmark_slope_path \
          --config bench_config_smoke_path.yml --no-cache
      '';
    };

    scripts.benchmark-data-checksums = {
      description = "Hash all data cached by the canonical benchmark commands";
      exec = ''
        ${prepareBenchmarkData}
        find "$benchmark_data_dir" -type f -print0 \
          | sort -z \
          | xargs -0 --no-run-if-empty sha256sum
      '';
    };

    containers.shell = {
      name = "slope-package-benchmarks";
      copyToRoot = benchmarkSource;
    };

    enterTest = ''
      test "$(printf %s '${libslope.version}')" = "${libslopeVersion}"
      python -c 'import importlib.metadata; assert importlib.metadata.version("sortedl1") == "${sortedl1Version}"'
      Rscript -e 'stopifnot(as.character(packageVersion("SLOPE")) == "${slopeRVersion}")'
      julia --project=. -e 'using Pkg; Pkg.instantiate(); using SLOPE; versions = [dep.version for dep in values(Pkg.dependencies()) if dep.name == "SLOPE"]; @assert only(versions) == v"${slopeJuliaVersion}"'
      python -c 'import benchopt, libsvmdata, modules, rpy2, skglm, slopescreening, tick'
      test "$(benchopt --version)" = "1.9.1"
      python -c 'import metewand'
      python -m pytest benchmark_slope/tests -q
      benchmark-smoke >/dev/null
      slope-example >/dev/null
    '';
  };
}

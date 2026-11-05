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
  rustPkgs = pkgs.extend (import inputs.rust-overlay);
  metewandPackages = import ./nix/metewand.nix {
    inherit pkgs;
    source = config.slopeBenchmark.metewandSource;
    toolchain = rustPkgs.rust-bin.fromRustupToolchainFile (inputs.metewand + "/rust-toolchain.toml");
  };
  benchmarkPythonPackages = ps: [
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
  benchmarkPython = pkgs.python3.withPackages benchmarkPythonPackages;
  benchmarkWorker =
    pkgs.runCommand "slope-benchmark-python"
      {
        nativeBuildInputs = [ pkgs.makeWrapper ];
        buildInputs = [
          pkgs.R
          SLOPE
          pkgs.rPackages.Matrix
        ];
      }
      ''
        mkdir -p "$out/bin"
        makeWrapper ${benchmarkPython}/bin/python3 "$out/bin/python3" \
          --prefix PATH : ${pkgs.R}/bin --set R_HOME ${pkgs.R}/lib/R \
          --set R_LIBS_SITE "$R_LIBS_SITE"
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
        || top == "benchmarks"
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
    default = inputs.metewand;
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
        test -d benchmarks/single || {
          echo "Run benchmark-single from the repository root." >&2
          exit 1
        }
        ${prepareBenchmarkData}
        export PATH="${benchmarkWorker}/bin:$PATH"
        mkdir -p benchmarks/single/outputs "$benchmark_data_dir"
        have_output=false
        for argument in "$@"; do
          case "$argument" in --output-dir|--output-dir=*) have_output=true ;; esac
        done
        if ! "$have_output"; then
          set -- --output-dir "benchmarks/single/outputs/run-$(date +%Y%m%d-%H%M%S-%N)" "$@"
        fi
        exec metewand run --manifest benchmarks/single/config.yml \
          --cache-dir "$benchmark_data_dir/metewand" "$@"
      '';
    };

    scripts.benchmark-path = {
      description = "Run the pinned solution-path benchmark";
      exec = ''
        test -d benchmarks/path || {
          echo "Run benchmark-path from the repository root." >&2
          exit 1
        }
        ${prepareBenchmarkData}
        export PATH="${benchmarkWorker}/bin:$PATH"
        mkdir -p benchmarks/path/outputs "$benchmark_data_dir"
        have_output=false
        for argument in "$@"; do
          case "$argument" in --output-dir|--output-dir=*) have_output=true ;; esac
        done
        if ! "$have_output"; then
          set -- --output-dir "benchmarks/path/outputs/run-$(date +%Y%m%d-%H%M%S-%N)" "$@"
        fi
        exec metewand run --manifest benchmarks/path/config.yml \
          --cache-dir "$benchmark_data_dir/metewand" "$@"
      '';
    };

    scripts.benchmark-environment = {
      description = "Print benchmark software, source, hardware, and thread settings";
      exec = ''
        python - <<'PY'
        from importlib.metadata import version

        packages = (
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
        fi
        python - <<'PYTHON'
        import yaml
        for manifest in ("benchmarks/single/config.yml", "benchmarks/path/config.yml"):
            with open(manifest) as stream:
                settings = yaml.safe_load(stream)["environments"]["local"]["environment-variables"]
            print(f"Worker settings ({manifest}):")
            for name, value in sorted(settings.items()):
                print(f"{name}: {value}")
        PYTHON
        uname -a
        lscpu
      '';
    };

    scripts.benchmark-smoke = {
      description = "Run fast checks through both pinned benchmark suites";
      exec = ''
        set -e
        test -d benchmarks/single && test -d benchmarks/path || {
          echo "Run benchmark-smoke from the repository root." >&2
          exit 1
        }
        ${prepareBenchmarkData}
        export PATH="${benchmarkWorker}/bin:$PATH"
        mkdir -p benchmarks/single/outputs benchmarks/path/outputs "$benchmark_data_dir"
        metewand check --manifest benchmarks/single/config.yml --experiment smoke --workers
        metewand run --manifest benchmarks/single/config.yml --experiment smoke \
          --cache-dir "$benchmark_data_dir/metewand" \
          --output-dir "benchmarks/single/outputs/smoke-$(date +%Y%m%d-%H%M%S-%N)"
        metewand check --manifest benchmarks/path/config.yml --experiment smoke --workers
        metewand run --manifest benchmarks/path/config.yml --experiment smoke \
          --cache-dir "$benchmark_data_dir/metewand" \
          --output-dir "benchmarks/path/outputs/smoke-$(date +%Y%m%d-%H%M%S-%N)"
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
      python -c 'import libsvmdata, modules, rpy2, skglm, slopescreening, tick'
      python -c 'import metewand'
      python -m pytest benchmarks/single/tests slopeutils/tests -q
      ${benchmarkWorker}/bin/python3 -m pytest benchmarks/path/tests -q
      benchmark-smoke >/dev/null
      slope-example >/dev/null
    '';
  };
}

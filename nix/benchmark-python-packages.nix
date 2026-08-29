{
  pkgs,
}:

let
  pythonPackages = pkgs.python3.pkgs;
  lineProfiler = pythonPackages.line-profiler.overridePythonAttrs (_: {
    # The source distribution omits fixtures required by two upstream tests.
    doCheck = false;
  });

  download = pythonPackages.buildPythonPackage rec {
    pname = "download";
    version = "0.3.5";
    pyproject = true;

    src = pkgs.fetchPypi {
      inherit pname version;
      hash = "sha256-iEqIVHWzzb7Aqid+QWQ5lcM5Sh4GSggW9T//rko4ITA=";
    };

    build-system = with pythonPackages; [ setuptools ];

    dependencies = with pythonPackages; [
      requests
      six
      tqdm
    ];

    doCheck = false;
    pythonImportsCheck = [ "download" ];
  };
in
rec {
  benchopt = pythonPackages.buildPythonPackage rec {
    pname = "benchopt";
    version = "1.9.1";
    pyproject = true;

    src = pkgs.fetchPypi {
      inherit pname version;
      hash = "sha256-zHuMFiIvSNbhUbtLIN7Njjndt/ECPojTEoo8IyrxtKU=";
    };

    build-system = with pythonPackages; [
      setuptools
      wheel
    ];

    dependencies = with pythonPackages; [
      click
      joblib
      lineProfiler
      mako
      matplotlib
      numpy
      pandas
      plotly
      psutil
      pyarrow
      pygithub
      pyyaml
      scipy
    ];

    doCheck = false;
    pythonImportsCheck = [ "benchopt" ];
  };

  skglm = pythonPackages.buildPythonPackage rec {
    pname = "skglm";
    version = "0.5";
    pyproject = true;

    src = pkgs.fetchPypi {
      inherit pname version;
      hash = "sha256-EQN67BGd0oada1dLbMqLrmkJHu7v4Gy70KWqh5rXncc=";
    };

    build-system = with pythonPackages; [ setuptools ];

    dependencies = with pythonPackages; [
      numba
      numpy
      scikit-learn
      scipy
    ];

    doCheck = false;
    pythonImportsCheck = [ "skglm" ];
  };

  libsvmdata = pythonPackages.buildPythonPackage rec {
    pname = "libsvmdata";
    version = "0.5";
    pyproject = true;

    src = pkgs.fetchPypi {
      inherit pname version;
      hash = "sha256-KStnXOjqNj3799MrS2peE7WbdP//VFohmCNycNpxDkY=";
    };

    build-system = with pythonPackages; [ setuptools ];

    dependencies = with pythonPackages; [
      download
      numpy
      scikit-learn
      scipy
    ];

    doCheck = false;
    pythonImportsCheck = [ "libsvmdata" ];
  };

  slopePath = pythonPackages.buildPythonPackage {
    pname = "slopepath";
    version = "1.0.0";
    pyproject = true;

    src = pkgs.fetchFromGitHub {
      owner = "jolars";
      repo = "slope-path";
      rev = "55165ab10079fe356ce56aef6e956750e6297060";
      hash = "sha256-WVbT0fW/lhBoJgyozl/lQy+i/rH9mX+0E5SwdAUsRhw=";
    };

    build-system = with pythonPackages; [ setuptools ];

    dependencies = with pythonPackages; [
      numba
      numpy
      scipy
    ];

    doCheck = false;
    pythonImportsCheck = [ "modules" ];
  };

  slopescreening = pythonPackages.buildPythonPackage {
    pname = "slopescreening";
    version = "2.0.0";
    pyproject = true;

    src = pkgs.fetchFromGitHub {
      owner = "c-elvira";
      repo = "slopescreening";
      rev = "4e20cf95cc5be23f4bb8e5ed6c1b98f34fc1867a";
      hash = "sha256-wIDDC8FLNf0TZ//pdzTNbZMNPZtcn5E94eFmOqkxgCU=";
    };

    build-system = with pythonPackages; [
      cython
      numpy
      scipy
      setuptools
    ];

    dependencies = with pythonPackages; [
      matplotlib
      numpy
      pyparsing
      python-dateutil
      scikit-learn
      scipy
    ];

    doCheck = false;
    pythonImportsCheck = [
      "slopescreening"
      "slopescreening.screening.gap_test_all"
      "slopescreening.screening.gap_test_p_1"
      "slopescreening.screening.utils"
    ];
  };
}

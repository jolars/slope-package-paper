{
  pkgs,
  source,
  toolchain,
}:
let
  cargoToml = builtins.fromTOML (builtins.readFile (source + "/Cargo.toml"));
  pythonToml = builtins.fromTOML (builtins.readFile (source + "/packages/python/pyproject.toml"));
  rustPlatform = pkgs.makeRustPlatform {
    cargo = toolchain;
    rustc = toolchain;
  };
in
{
  cli = rustPlatform.buildRustPackage {
    pname = "metewand";
    version = cargoToml.package.version;
    src = pkgs.lib.cleanSourceWith {
      src = source;
      filter =
        path: type:
        let
          name = baseNameOf path;
        in
        !(builtins.elem name [
          ".git"
          ".devenv"
          "target"
          "node_modules"
        ]);
    };
    cargoLock.lockFile = source + "/Cargo.lock";
    # The full framework suite runs in its own repository and requires R.
    doCheck = false;
    meta.mainProgram = "metewand";
  };

  python = pkgs.python3.pkgs.buildPythonPackage {
    pname = "metewand";
    version = pythonToml.project.version;
    src = pkgs.lib.cleanSourceWith {
      src = source + "/packages/python";
      filter =
        path: type:
        let
          name = baseNameOf path;
        in
        !(builtins.elem name [
          "build"
          "dist"
          "__pycache__"
        ])
        && !(pkgs.lib.hasSuffix ".egg-info" name);
    };
    pyproject = true;
    build-system = [ pkgs.python3.pkgs.setuptools ];
    pythonImportsCheck = [ "metewand" ];
  };
}

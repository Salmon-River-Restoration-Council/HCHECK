{
  description = "HCHECK HOBO Temperature Anomaly Flagger";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
  }:
    flake-utils.lib.eachDefaultSystem (
      system: let
        pkgs = nixpkgs.legacyPackages.${system};
        python = pkgs.python3;
        pythonPackages = python.pkgs;

        hcheckEnv = python.withPackages (ps:
          with ps; [
            pyqt5
            pandas
            openpyxl
          ]);

        hcheckPackage = pkgs.stdenv.mkDerivation {
          pname = "hcheck";
          version = "0.1.0";
          src = ./.;
          buildInputs = [hcheckEnv];
          installPhase = ''
            mkdir -p $out/bin
            cp hcheck.py $out/bin/hcheck
            chmod +x $out/bin/hcheck
            wrapProgram $out/bin/hcheck \
              --prefix PYTHONPATH : $PYTHONPATH
          '';
          nativeBuildInputs = [pkgs.makeWrapper];
        };
      in {
        packages.default = hcheckPackage;

        apps.default = flake-utils.lib.mkApp {
          drv = hcheckPackage;
          name = "hcheck";
        };

        devShell = pkgs.mkShell {
          buildInputs = [hcheckPackage];
        };
      }
    );
}

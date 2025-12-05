{
  description = "Development environment with nix-ld support";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
  }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = import nixpkgs {
        inherit system;
        config = {
          allowUnfree = true;
        };
      };
    in {
      devShells.default = pkgs.mkShell {
        # your project name
        name = "anita-cms-dev-environment";

        NIX_LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath (with pkgs; [
          stdenv.cc.cc
          libz
        ]);

        # Set the dynamic linker for nix-ld
        NIX_LD = pkgs.lib.fileContents "${pkgs.stdenv.cc}/nix-support/dynamic-linker";

        packages = with pkgs; [
          uv
          gcc
        ];

        # Shell hook with nix-ld configuration
        shellHook = ''
          # Set up nix-ld for compatibility
          export LD_LIBRARY_PATH=$NIX_LD_LIBRARY_PATH
          alias venv-ldd-check='find .venv/ -type f -name "*.so" | xargs ldd | grep "not found" | sort | uniq'

          # Initialize uv virtual environment if not exists
          if [ ! -d .venv ] && command -v uv > /dev/null; then
            echo "📝 Initializing uv virtual environment..."
            uv venv
          fi

          # Activate virtual environment if it exists
          if [ -d .venv ] && [ -f .venv/bin/activate ]; then
            echo "🔧 Activating virtual environment..."
            source .venv/bin/activate
          fi

          # Check for nix-ld
          if [ -n "$NIX_LD" ]; then
            echo "⚡ nix-ld is enabled: $(basename $NIX_LD)"
          else
            echo "⚠️  nix-ld not configured"
          fi
        '';
      };
    });
}

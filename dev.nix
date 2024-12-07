{ pkgs ? import <nixpkgs> {} }:

with pkgs;
mkShell {
  buildInputs = [
    # Python and pip
    python311
    python311Packages.pip
    
    # LaTeX
    texlive.combined.scheme-full
    
    # Playwright and dependencies
    python311Packages.playwright
    
    # Additional dependencies
    nodejs
    chromium
    firefox
  ];

  shellHook = ''
    # Install poetry and project dependencies
    pip install --user poetry
    poetry install
  '';
}

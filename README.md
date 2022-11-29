# xapp

A dnf, flatpak and nix-env wrapper inspired by paru

# Usage

Extract the files to a folder and alias it to xapp.py for it to work (alias xapp="python3 /path/to/folder/xapp.py")

# Setup

For nix-env to work as intendend, you need to export ~/.local/share/nix-env/share to XDG_DATA_DIRS

The reason is that at least on my pc, directly exporting ~/.nix-profile/share slows down my pc a lot due to the symlinks, so by doing a rsync with no symlinks and exporting that folder it's usable

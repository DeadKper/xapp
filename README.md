# xapp

A dnf, flatpak and nix-env wrapper inspired by paru

# Install

git clone git@github.com:DeadKper/xapp.git
cd xapp
ln -s $PWD/xapp.py ~/.local/bin/xapp

~/.local/bin needs to be added to your path

# Setup

For nix-env to work as intendend, you need to export ~/.local/share/nix-env/share to XDG_DATA_DIRS

The reason is that at least on my pc, directly exporting ~/.nix-profile/share slows down my pc a lot due to the symlinks, so by doing a rsync with no symlinks and exporting that folder it's usable

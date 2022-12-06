# xapp

A dnf, flatpak and nix-env wrapper inspired by paru

# Install

```
git clone https://github.com/DeadKper/xapp.git
cd xapp
ln -s $PWD/xapp.py ~/.local/bin/xapp
```

~/.local/bin needs to be added to your path

# Setup

For nix-env to work as intendend, you need to export ~/.local/share/nix-env/share to XDG_DATA_DIRS

The reason is that at least on my pc, directly exporting ~/.nix-profile/share slows down my pc a lot due to the symlinks, so this program does a rsync that resolves symlinks to said folder to make it usable when installing or removing from nix-env

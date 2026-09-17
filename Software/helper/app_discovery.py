"""Find user-installed launch shortcuts without changing system settings."""
import os
import pathlib
import sys
from platform_io import NotReady

NAMES = {'fortnite': {'fortnite'}, 'valorant': {'valorant'},
         'discord': {'discord'}, 'spotify': {'spotify'},
         'capcut': {'capcut'}}

def find_shortcut(name, roots):
    names = NAMES.get(name, {name.casefold()})
    matches = []
    for root in roots:
        root = pathlib.Path(root)
        if not root.is_dir():
            continue
        for path in root.rglob('*'):
            if path.suffix.lower() in ('.lnk', '.url') and path.stem.casefold() in names:
                matches.append(path)
    if not matches:
        raise NotReady('Choose '+name+' in Apps setup')
    # Prefer the user's Start Menu over the shared menu, then Desktop.
    return matches[0]

def installed_app(name):
    if sys.platform != 'win32':
        return {'messages':'Messages','terminal':'Terminal','photos':'Photos',
                'capcut':'CapCut','spotify':'Spotify','discord':'Discord'}.get(name,'')
    if name == 'terminal':
        return 'wt.exe'
    if name == 'photos':
        return 'ms-photos:'
    roots = []
    for env in ('APPDATA','PROGRAMDATA'):
        base = os.getenv(env)
        if base:
            roots.append(pathlib.Path(base)/'Microsoft/Windows/Start Menu/Programs')
    roots.append(pathlib.Path.home()/'Desktop')
    return str(find_shortcut(name, roots))

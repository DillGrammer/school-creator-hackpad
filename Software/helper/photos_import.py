"""Export only the user's selected Photos item using Photos' documented API.

Originals remain in Photos. Export folders are retained because CapCut links media.
This adapter needs macOS Automation permission and an on-device integration test.
"""
import pathlib
import subprocess
import sys
import tempfile
import time
from platform_io import NotReady

SCRIPT = '''on run argv
    set destination to POSIX file (item 1 of argv) as alias
    tell application "Photos"
        set chosenItems to selection
        if (count of chosenItems) is not 1 then error "Select exactly one photo or video in Photos."
        export chosenItems to destination using originals true
    end tell
end run
'''
EXTENSIONS = {'.mp4', '.mov', '.m4v', '.png', '.jpg', '.jpeg', '.heic', '.tif', '.tiff', '.gif'}

def exported_media(folder):
    files = sorted(p for p in pathlib.Path(folder).iterdir()
                   if p.is_file() and p.suffix.lower() in EXTENSIONS and p.stat().st_size)
    if len(files) != 1:
        raise NotReady('Photos exported multiple or unsupported files; choose a file with Selected')
    return files[0]

def export_selected(parent, cancelled):
    if sys.platform != 'darwin':
        raise NotReady('Photos selection is available on Mac; use Selected on Windows')
    if cancelled.is_set():
        raise NotReady('Cancelled')
    parent = pathlib.Path(parent)
    parent.mkdir(parents=True, exist_ok=True)
    folder = pathlib.Path(tempfile.mkdtemp(prefix='photos-', dir=parent))
    # Fixed script and separate argv keep filenames out of executable source.
    with tempfile.TemporaryFile(mode='w+b') as errors:
        process = subprocess.Popen(['/usr/bin/osascript', '-e', SCRIPT, str(folder)],
                                   stdout=subprocess.DEVNULL, stderr=errors)
        deadline = time.monotonic() + 180
        try:
            while process.poll() is None:
                if cancelled.wait(.1):
                    raise NotReady('Cancelled; Photos may still finish its local export')
                if time.monotonic() > deadline:
                    raise NotReady('Photos export timed out; download the original in Photos and retry')
            if process.returncode:
                errors.seek(0)
                detail = errors.read().decode('utf-8', errors='replace')
                if 'Select exactly one' in detail:
                    raise NotReady('Select exactly one photo or video in Photos')
                raise NotReady('Photos export failed; check Automation permission and original availability')
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
    if cancelled.is_set():
        raise NotReady('Cancelled')
    return exported_media(folder)

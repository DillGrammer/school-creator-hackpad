"""Install/update this project's isolated dependencies, then launch the helper."""
import hashlib, os, pathlib, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parent

def main():
 if sys.version_info < (3,11):
  raise RuntimeError('Install Python 3.11 or newer first.')
 try:import tkinter
 except ImportError:
  raise RuntimeError('Python is missing Tk. Use a python.org Python installer with Tk, or install the matching python-tk package for Homebrew Python.')
 env=ROOT/'.venv';python=env/('Scripts/python.exe' if os.name=='nt' else 'bin/python')
 if not python.exists():subprocess.run([sys.executable,'-m','venv',str(env)],check=True)
 requirements=ROOT/'helper/requirements.txt';stamp=env/'hackpad-requirements.sha256';digest=hashlib.sha256(requirements.read_bytes()).hexdigest()
 if not stamp.exists() or stamp.read_text()!=digest:
  subprocess.run([str(python),'-m','pip','install','-r',str(requirements)],check=True)
  stamp.write_text(digest)
 os.chdir(ROOT)
 return subprocess.call([str(python),str(ROOT/'helper/main.py')])

if __name__=='__main__':
 try:sys.exit(main())
 except (RuntimeError,subprocess.CalledProcessError) as error:
  print('Hackpad setup failed:',error);input('Press Enter to close.');sys.exit(1)

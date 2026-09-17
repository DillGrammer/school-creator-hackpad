"""Save the active Safari Word document. Native integration requires Mac Accessibility.
UI command names observed in Word for the web, September 2026. English UI only.
No document content, cookies, or authentication tokens are read.
"""
import pathlib, re, sys, time, zipfile
from platform_io import NotReady


def matching_name(filename, title):
    stem = re.sub(r'\.docx$', '', title.strip(), flags=re.I)
    return bool(re.fullmatch(re.escape(stem) + r'(?:[ -]\d+| \(\d+\))?\.docx', filename, re.I))


def complete_docx(path):
    try:
        with zipfile.ZipFile(path) as z:
            return {'[Content_Types].xml', 'word/document.xml'} <= set(z.namelist()) and z.testzip() is None
    except (OSError, zipfile.BadZipFile):
        return False


def signature(path):
    s = path.stat()
    return s.st_size, s.st_mtime_ns


def snapshot(folder):
    return {p.name: signature(p) for p in folder.iterdir() if p.is_file()}


def wait_download(folder, before, title, cancelled, timeout=60):
    deadline = time.monotonic() + timeout
    stable = {}
    while time.monotonic() < deadline:
        if cancelled.is_set():
            raise NotReady('Cancelled')
        candidates = []
        for p in folder.iterdir():
            if not p.is_file() or not matching_name(p.name, title):
                continue
            try:
                sig = signature(p)
                if before.get(p.name) == sig:
                    continue
                if stable.get(p.name) == sig and complete_docx(p):
                    candidates.append(p)
                stable[p.name] = sig
            except OSError:
                continue
        if len(candidates) > 1:
            raise NotReady('Multiple matching downloads; retry separately')
        if candidates:
            return candidates[0]
        cancelled.wait(.3)
    raise NotReady('Word download not found; check Safari Downloads folder')


class SafariWord:
    def __init__(self, cancelled):
        if sys.platform != 'darwin':
            raise NotReady('Word copy currently requires Safari on Mac')
        import ApplicationServices as AX
        from AppKit import NSWorkspace
        self.ax, self.workspace, self.cancelled = AX, NSWorkspace.sharedWorkspace(), cancelled
        app = self.workspace.frontmostApplication()
        if app.bundleIdentifier() != 'com.apple.Safari':
            raise NotReady('Focus your Word document in Safari')
        if not AX.AXIsProcessTrusted():
            raise NotReady('Allow Hackpad helper Accessibility in System Settings')
        self.pid = app.processIdentifier()
        self.app = AX.AXUIElementCreateApplication(self.pid)
        self.window = self.attr(self.app, 'AXFocusedWindow')
        if self.window is None:
            raise NotReady('Open Word document in Safari')
        self.title = str(self.attr(self.window, 'AXTitle') or '')
        # Restrict operation to the displayed Office Word editor, not Safari's File menu.
        frames = self.find(self.window, lambda e: self.attr(e, 'AXRole') == 'AXWebArea' and
                           'word' in str(self.attr(e, 'AXURL') or '').lower() and
                           '.officeapps.live.com/' in str(self.attr(e, 'AXURL') or '').lower())
        if len(frames) != 1:
            raise NotReady('Focus an open Word web document')
        self.frame = frames[0]

    def attr(self, node, name):
        err, value = self.ax.AXUIElementCopyAttributeValue(node, name, None)
        return value if err == 0 else None

    def guard(self):
        if self.cancelled.is_set():
            raise NotReady('Cancelled')
        if self.workspace.frontmostApplication().processIdentifier() != self.pid:
            raise NotReady('Safari lost focus; retry from Word')
        window = self.attr(self.app, 'AXFocusedWindow')
        if str(self.attr(window, 'AXTitle') or '') != self.title:
            raise NotReady('Document changed; retry from Word')

    def find(self, root, predicate):
        queue = [(root, 0)]; matches = []; count = 0
        while queue and count < 6000:
            node, depth = queue.pop(); count += 1
            if predicate(node):
                matches.append(node)
            if depth >= 35 or self.attr(node, 'AXRole') in ('AXTextArea', 'AXTextField'):
                continue
            if self.attr(node, 'AXDescription') == 'Document Contents':
                continue
            queue.extend((child, depth+1) for child in (self.attr(node, 'AXChildren') or []))
        return matches

    def press(self, label, root, role=None):
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            self.guard()
            matches = self.find(root, lambda e: (role is None or self.attr(e, 'AXRole') == role) and
                                label in (self.attr(e, 'AXTitle'), self.attr(e, 'AXDescription')))
            actionable = []
            for e in matches:
                err, actions = self.ax.AXUIElementCopyActionNames(e, None)
                if err == 0 and 'AXPress' in actions and self.attr(e, 'AXEnabled') is not False:
                    actionable.append(e)
            if len(actionable) == 1:
                if self.ax.AXUIElementPerformAction(actionable[0], 'AXPress') != 0:
                    raise NotReady('Word control unavailable: ' + label)
                return
            if len(actionable) > 1:
                raise NotReady('Ambiguous Word control: ' + label)
            self.cancelled.wait(.15)
        raise NotReady('Word control not found: ' + label)

    def download(self, folder):
        before = snapshot(folder)
        self.press('File', self.frame, 'AXPopUpButton')
        self.press('Create a Copy', self.window)
        self.press('Download a copy', self.window)
        return wait_download(folder, before, self.title, self.cancelled)


def save_word_copy(destination, config, cancelled):
    from actions import copy_unique
    downloads = pathlib.Path(config.get('word_downloads_folder') or pathlib.Path.home()/'Downloads').expanduser()
    if not downloads.is_dir():
        raise NotReady('Set Safari downloads folder in Setup')
    source = SafariWord(cancelled).download(downloads)
    if cancelled.is_set():
        raise NotReady('Cancelled')
    return copy_unique(source, destination)

import pathlib
import sys
import tempfile
import unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'helper'))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'firmware'))
from photos_import import exported_media
from platform_io import NotReady
from engine import Engine

class PhotosImportTests(unittest.TestCase):
    def test_original_with_metadata_sidecar(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d)
            (p/'clip.MOV').write_bytes(b'video')
            (p/'clip.xmp').write_bytes(b'metadata')
            self.assertEqual(exported_media(p), p/'clip.MOV')

    def test_live_photo_does_not_guess_between_still_and_video(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d)
            (p/'live.HEIC').write_bytes(b'image')
            (p/'live.MOV').write_bytes(b'video')
            with self.assertRaises(NotReady):
                exported_media(p)

    def test_empty_export_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            (pathlib.Path(d)/'empty.mov').touch()
            with self.assertRaises(NotReady):
                exported_media(d)

    def test_menu_keeps_open_and_import_separate(self):
        events=[]
        engine=Engine(events.append)
        engine.page='capcut'
        engine.select('import')
        engine.index=2
        engine.click()
        self.assertEqual(engine.title,'photos')
        self.assertEqual(events,[])
        engine.click()
        self.assertEqual(events[-1]['action'],'open.photos')
        engine.rotate(1)
        engine.click()
        self.assertEqual(events[-1]['action'],'capcut.import_photos')
        engine.back()
        self.assertEqual(engine.title,'import')

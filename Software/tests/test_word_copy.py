import pathlib, sys, tempfile, threading, unittest, zipfile
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'helper'))
from word_copy import matching_name, complete_docx, wait_download, snapshot
from platform_io import NotReady

class WordCopyTests(unittest.TestCase):
 def make_doc(self,p):
  with zipfile.ZipFile(p,'w') as z:
   z.writestr('[Content_Types].xml','<Types/>');z.writestr('word/document.xml','<document/>')
 def test_filename_match(self):
  for name in ['Essay.docx','Essay (1).docx','Essay-2.docx']:
   self.assertTrue(matching_name(name,'Essay.docx'))
  for name in ['Other.docx','Essay.docx.download','Essay notes.docx']:
   self.assertFalse(matching_name(name,'Essay.docx'))
 def test_reject_partial_and_unrelated_zip(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'Essay.docx';p.write_bytes(b'PKpartial');self.assertFalse(complete_docx(p))
   with zipfile.ZipFile(p,'w') as z:z.writestr('other','x')
   self.assertFalse(complete_docx(p))
 def test_does_not_take_existing_download(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d);self.make_doc(p/'Essay.docx');before=snapshot(p)
   with self.assertRaises(NotReady):wait_download(p,before,'Essay',threading.Event(),timeout=.05)
 def test_new_complete_copy(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d);before=snapshot(p);self.make_doc(p/'Essay.docx')
   self.assertEqual(wait_download(p,before,'Essay',threading.Event(),timeout=2).name,'Essay.docx')
 def test_cancel(self):
  with tempfile.TemporaryDirectory() as d:
   event=threading.Event();event.set()
   with self.assertRaises(NotReady):wait_download(pathlib.Path(d),{},'Essay',event)

import pathlib,sys,unittest
from unittest.mock import Mock
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'helper'))
from browser_workflows import BrowserWorkflows
from platform_io import NotReady
from playwright.sync_api import Error,TimeoutError

class BrowserFallbackTests(unittest.TestCase):
 def test_navigation_timeout_becomes_manual_fallback(self):
  browser=BrowserWorkflows();browser.page=Mock(side_effect=TimeoutError('navigation timed out'))
  with self.assertRaises(NotReady):browser.upload('https://example.com','video.mp4')
 def test_closed_page_during_chat_becomes_manual_fallback(self):
  browser=BrowserWorkflows();browser.page=Mock(side_effect=Error('Target closed'))
  with self.assertRaises(NotReady):browser.chat_draft('https://example.com','Help')
 def test_closed_context_can_be_reopened(self):
  browser=BrowserWorkflows();old=Mock();browser.context=old
  browser.closed(old)
  self.assertIsNone(browser.context)
 def test_old_close_event_cannot_clear_new_context(self):
  browser=BrowserWorkflows();current=Mock();browser.context=current
  browser.closed(Mock())
  self.assertIs(browser.context,current)
 def test_existing_draft_never_overwritten(self):
  browser=BrowserWorkflows();page=Mock();browser.page=Mock(return_value=page)
  editor=page.locator.return_value;editor.count.return_value=1
  editor.get_attribute.return_value='true';editor.inner_text.return_value='Unfinished user draft'
  with self.assertRaises(NotReady):browser.chat_draft('https://example.com','New question')
  editor.fill.assert_not_called()

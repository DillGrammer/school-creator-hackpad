"""Optional isolated browser session. Never sends chat messages or publishes posts."""
from urllib.parse import urlparse
from platform_io import NotReady
from config import location
from functools import wraps

def browser_fallback(operation):
 @wraps(operation)
 def guarded(self,*args,**kwargs):
  from playwright.sync_api import Error
  try:return operation(self,*args,**kwargs)
  except Error as exc:
   raise NotReady('Browser action unavailable; finish manually or reopen the helper browser') from exc
 return guarded

class BrowserWorkflows:
 def __init__(self):self.pw=None;self.context=None
 def start(self):
  if self.context:return
  from playwright.sync_api import sync_playwright
  if self.pw is None:self.pw=sync_playwright().start()
  self.context=self.pw.chromium.launch_persistent_context(str(location().parent/'browser'),headless=False,accept_downloads=True)
  context=self.context
  context.on('close',lambda *_:self.closed(context))
 def closed(self,context):
  if self.context is context:self.context=None
 def page(self,url):
  if urlparse(url).scheme not in ('https','http'):raise NotReady('Invalid web URL')
  self.start()
  page=next((p for p in self.context.pages if p.url.rstrip('/')==url.rstrip('/')),None)
  if page is None:page=self.context.new_page();page.goto(url,wait_until='domcontentloaded')
  page.bring_to_front();return page
 @browser_fallback
 def chat_draft(self,url,prompt,image=None):
  p=self.page(url)
  editor=p.locator('#prompt-textarea')
  if editor.count()!=1:raise NotReady('Sign in to helper browser first')
  old=editor.inner_text() if editor.get_attribute('contenteditable') else editor.input_value()
  if old.strip():raise NotReady('Finish existing ChatGPT draft')
  if image:
   files=p.locator('input[type=file]')
   if files.count()!=1:raise NotReady('Attach screenshot manually')
   files.set_input_files(str(image))
  editor.fill(prompt)
  # Deliberately no Enter, send-button click, or implicit auto-submit.
 @browser_fallback
 def upload(self,url,file):
  p=self.page(url);files=p.locator('input[type=file]')
  if files.count()!=1:raise NotReady('Open upload editor; choose video manually')
  files.set_input_files(str(file))
  # Stop at attachment. No Next/Share/Post/Schedule control is invoked.

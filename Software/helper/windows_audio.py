"""Windows Core Audio mixer. No master-volume fallback and no game injection."""
import sys,asyncio
from platform_io import NotReady,foreground

def sessions(config):
 from pycaw.pycaw import AudioUtilities
 pid,name=foreground();aliases=config.get('audio_process_aliases',{}).get(name.lower(),[])
 matches=[]
 from pycaw.constants import EDataFlow,DEVICE_STATE
 from pycaw.utils import AudioSession
 from pycaw.api.audiopolicy import IAudioSessionControl2
 all_sessions=[]
 for device in AudioUtilities.GetAllDevices(data_flow=EDataFlow.eRender.value,device_state=DEVICE_STATE.ACTIVE.value):
  try:
   enum=device.AudioSessionManager.GetSessionEnumerator()
   all_sessions.extend(AudioSession(enum.GetSession(i).QueryInterface(IAudioSessionControl2)) for i in range(enum.GetCount()))
  except Exception:continue
 for s in all_sessions:
  try:
   if s.Process and (s.Process.pid==pid or s.Process.name().lower() in aliases):matches.append(s)
  except Exception:pass
 return name,matches

def mic_state(config):
 from pycaw.pycaw import AudioUtilities
 name=config.get('headset_microphone','')
 if not name:return None
 # Match a capture endpoint only, never a playback/headphones endpoint.
 from pycaw.constants import EDataFlow,DEVICE_STATE
 devices=AudioUtilities.GetAllDevices(data_flow=EDataFlow.eCapture.value,device_state=DEVICE_STATE.ACTIVE.value)
 match=[d for d in devices if d.FriendlyName==name or d.id==name]
 if len(match)!=1:return None
 return bool(match[0].EndpointVolume.GetMute())

def snapshot(config,delta=0):
 if sys.platform!='win32':return {'app':'Windows only','volume':None,'mic':None,'icon':'app'}
 import comtypes
 comtypes.CoInitialize()
 try:
  name,matched=sessions(config)
  if delta and not matched:raise NotReady('No audio for this app')
  for s in matched:
   if delta:s.SimpleAudioVolume.SetMasterVolume(max(0,min(1,s.SimpleAudioVolume.GetMasterVolume()+delta*.02)),None)
  vols=[round(s.SimpleAudioVolume.GetMasterVolume()*100) for s in matched]
  # Multiple different session values are not represented as one invented number.
  vol=vols[0] if vols and len(set(vols))==1 else None
  low=name.lower();icon=next((n for n in ['spotify','discord','fortnite','valorant'] if n in low),'app')
  try:mic=mic_state(config)
  except Exception:mic=None
  return {'app':name.removesuffix('.exe'),'volume':vol,'mic':mic,'icon':icon}
 finally:comtypes.CoUninitialize()

async def _transport(previous):
 from winrt.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as Manager
 manager=await Manager.request_async()
 found=[s for s in manager.get_sessions() if 'spotify' in s.source_app_user_model_id.lower()]
 if len(found)!=1:raise NotReady('Spotify session unavailable')
 ok=await (found[0].try_skip_previous_async() if previous else found[0].try_skip_next_async())
 if not ok:raise NotReady('Spotify rejected command')
def transport(previous=False):asyncio.run(_transport(previous))

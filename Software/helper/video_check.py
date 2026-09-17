"""Validate a completed portrait video locally before offering it to upload pages."""
import pathlib, time
from platform_io import NotReady

def validate_video(file, cancelled):
 import av
 file=pathlib.Path(file)
 if file.suffix.lower() not in ('.mp4','.mov','.m4v') or not file.is_file():
  raise NotReady('Choose a completed video export')
 before=file.stat()
 if not before.st_size or time.time()-before.st_mtime<2:
  raise NotReady('Export is still finishing')
 count=0;last_time=0.0
 try:
  with av.open(str(file)) as container:
   streams=list(container.streams.video)
   if len(streams)!=1:raise NotReady('Export must have one video track')
   stream=streams[0]
   if (stream.width,stream.height)!=(1080,1920):raise NotReady('Export at 1080 x 1920 portrait')
   rate=float(stream.average_rate or 0)
   if abs(rate-30)>.1:raise NotReady('Export at 30 fps')
   expected=float(stream.duration*stream.time_base) if stream.duration else None
   for frame in container.decode(stream):
    if cancelled.is_set():raise NotReady('Cancelled')
    count+=1
    if frame.time is not None:last_time=max(last_time,float(frame.time))
   if count==0:raise NotReady('Export has no playable frames')
   if expected and last_time+max(1.0,2/rate)<expected:raise NotReady('Export appears incomplete')
 except NotReady:raise
 except Exception as error:raise NotReady('Video is incomplete or unreadable; export again') from error
 after=file.stat()
 if (before.st_size,before.st_mtime_ns)!=(after.st_size,after.st_mtime_ns):raise NotReady('Export changed during validation; retry')
 return {'width':1080,'height':1920,'fps':rate,'decoded_frames':count,'size':after.st_size}

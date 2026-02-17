import os
import subprocess
import threading
import time

log2 = None
log = None
line_raw = None
line_link = None


def iw_start_threads():
  global log2, log, line_raw, line_link
  threading.Thread(target=thread_iw_link, daemon=True).start()
  threading.Thread(target=thread_iw_event, daemon=True).start()


def thread_iw_link():
  global log2, log, line_raw, line_link
  log2 = open('/opt/ft/workspaces/iw2.log', 'w', encoding='utf8')
  #subprocess.Popen(['chown', 'ftgui:ftgui', '/opt/ft/workspaces/iw.log'])
  subprocess.Popen(['chmod', '777', '/opt/ft/workspaces/iw2.log'])
  log2.close()
  while True:
    #/usr/sbin/iw dev mlan0 link
    proc = subprocess.Popen(['/usr/sbin/iw','dev', 'mlan0', 'link'],stdout=subprocess.PIPE)
    while True:
      line_link = proc.stdout.readline().decode()
      if not line_link:
        break
      #print(line_link.rstrip('\n'))
      log2 = open('/opt/ft/workspaces/iw2.log', 'a', encoding='utf8')
      log2.write(line_link)
      log2.close()
    time.sleep(1)


def thread_iw_event():
  global log2, log, line_raw, line_link
  #/usr/sbin/iw event -r -f
  proc = subprocess.Popen(['/usr/sbin/iw','event', '-t', '-f'],stdout=subprocess.PIPE)
  log = open('/opt/ft/workspaces/iw.log', 'w', encoding='utf8')
  #subprocess.Popen(['chown', 'ftgui:ftgui', '/opt/ft/workspaces/iw.log'])
  subprocess.Popen(['chmod', '777', '/opt/ft/workspaces/iw.log'])
  log.close()
  while True:
    line_raw = proc.stdout.readline().decode()
    if not line_raw:
      break
    print(line_raw.rstrip('\n'))
    line = line_raw.split(": ")
    ts = line[0]
    msg = line[2]
    if len(line)>3:
      args = line[3]
    #print(ts, " # ", msg, " # ", args)
    log = open('/opt/ft/workspaces/iw.log', 'a', encoding='utf8')
    log.write(line_raw)
    log.close()



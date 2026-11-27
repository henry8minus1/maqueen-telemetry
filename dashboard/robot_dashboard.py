"""Four-slot local graphical Maqueen dashboard; USB receiver COM5."""
import sys,json,time,threading,queue
from pathlib import Path
import serial
import tkinter as tk
from tkinter import ttk
ROOT=Path(__file__).resolve().parent
BG='#0b1420'; PANEL='#142333'; TEXT='#e3edf5'; MUTED='#8da6bb'; COLORS=['#4ce0be','#67b9ff','#f5bc63','#d59aff']
class Model:
 def __init__(self):
  self.values={};self.last=0;self.seq=None;self.received=0;self.missed=0;self.rssi=None;self.events=[]
 def accept(self,packet,rssi,now):
  version,rid,seq,ms,kind,data=packet
  if self.seq is not None and seq>self.seq:self.missed+=max(0,seq-self.seq-1)
  self.seq=seq;self.last=now;self.received+=1;self.rssi=rssi
  if kind=='state':
   for k,v in data.items():self.values[k]=(v,now)
  elif kind=='event':self.events=(self.events+[(ms,data)])[-8:]
 def value(self,k,default=None):return self.values.get(k,(default,0))[0]
 def fresh(self,k,now):return k in self.values and now-self.values[k][1]<3
class Fleet:
 def __init__(self):self.robots={i:Model() for i in range(1,5)}
 def accept(self,line,now):
  tag,rssi,payload=line.split(' ',2);p=json.loads(payload)
  if tag!='R' or len(p)!=6 or p[0]!=2 or type(p[1])!=int or p[1] not in self.robots:raise ValueError('Unsupported robot packet')
  if p[4] not in ('state','event'):raise ValueError('Unknown packet kind')
  if p[4]=='state' and not isinstance(p[5],dict):raise ValueError('Invalid state')
  self.robots[p[1]].accept(p,int(rssi),now)
class Dashboard:
 def __init__(self,port_name='COM5',expected_lesson='lesson1-v1'):
  self.root=tk.Tk();self.root.title('Maqueen Fleet | Live Telemetry');self.root.geometry('1380x900');self.root.configure(bg=BG)
  self.fleet=Fleet();self.q=queue.Queue();self.closed=threading.Event();self.generation=0
  self.expected=tk.StringVar(value=expected_lesson);self.port=tk.StringVar(value=port_name);self.status=tk.StringVar(value='Connecting…')
  top=tk.Frame(self.root,bg=BG);top.pack(fill='x',padx=20,pady=12)
  tk.Label(top,text='MAQUEEN  /  FLEET MONITOR',font=('Segoe UI',21,'bold'),fg=TEXT,bg=BG).pack(side='left')
  ttk.Button(top,text='Reconnect receiver',command=self.connect).pack(side='right',padx=8)
  ttk.Entry(top,textvariable=self.port,width=8).pack(side='right')
  ttk.Entry(top,textvariable=self.expected,width=15).pack(side='right',padx=8)
  tk.Label(top,text='Expected lesson',fg=MUTED,bg=BG).pack(side='right')
  tk.Label(self.root,textvariable=self.status,anchor='w',fg=MUTED,bg=BG,font=('Segoe UI',10)).pack(fill='x',padx=20)
  grid=tk.Frame(self.root,bg=BG);grid.pack(fill='both',expand=True,padx=14,pady=10)
  self.cards=[]
  for i in range(4):
   grid.rowconfigure(i//2,weight=1);grid.columnconfigure(i%2,weight=1)
   c=tk.Canvas(grid,bg=PANEL,highlightthickness=0);c.grid(row=i//2,column=i%2,sticky='nsew',padx=6,pady=6);self.cards.append(c)
  bottom=tk.Frame(self.root,bg=BG);bottom.pack(fill='x',padx=20,pady=(0,10))
  tk.Label(bottom,text='One USB receiver · four unique robot IDs · LED pixels are measured, not inferred',fg=MUTED,bg=BG,font=('Segoe UI',10)).pack(side='left')
  self.selected=tk.IntVar(value=1)
  ttk.Combobox(bottom,values=[1,2,3,4],textvariable=self.selected,width=3,state='readonly').pack(side='right')
  ttk.Button(bottom,text='Sensor details',command=self.details).pack(side='right',padx=8)
  self.connect();self.root.after(100,self.refresh);self.root.protocol('WM_DELETE_WINDOW',self.close)
 def connect(self):
  self.generation+=1;threading.Thread(target=self.reader,args=(self.generation,self.port.get().strip()),daemon=True).start()
 def reader(self,gen,name):
  folder=ROOT/'wireless_logs';folder.mkdir(exist_ok=True);path=folder/(time.strftime('%Y%m%d-%H%M%S')+'-fleet.jsonl')
  while not self.closed.is_set() and gen==self.generation:
   try:
    with serial.Serial(name,115200,timeout=.3) as p,path.open('a',encoding='utf8') as log:
     self.q.put(('status','Receiver '+name+' connected  |  Logging '+path.name))
     while not self.closed.is_set() and gen==self.generation:
      line=p.readline().decode('utf8',errors='replace').strip()
      if line:
       log.write(json.dumps({'host_time':time.time(),'raw':line})+'\n');log.flush()
       if line.startswith('R '):self.q.put(('packet',line))
   except Exception as e:
    self.q.put(('status','Waiting for '+name+': '+str(e)));self.closed.wait(1)
 def draw(self,c,rid,now):
  c.delete('all');w=max(600,c.winfo_width());h=max(330,c.winfo_height());sx=w/660;sy=h/380
  def text(x,y,t,size=11,color=TEXT,anchor='w',bold=False):c.create_text(x*sx,y*sy,text=t,fill=color,font=('Segoe UI',size,'bold' if bold else 'normal'),anchor=anchor)
  def rect(x,y,a,b,fill,outline=''):c.create_rectangle(x*sx,y*sy,a*sx,b*sy,fill=fill,outline=outline)
  def oval(x,y,a,b,fill,outline=''):c.create_oval(x*sx,y*sy,a*sx,b*sy,fill=fill,outline=outline)
  m=self.fleet.robots[rid];accent=COLORS[rid-1];live=m.last and now-m.last<2
  text(18,26,'ROBOT '+str(rid),16,accent,bold=True)
  text(630,26,('LIVE' if live else 'OFFLINE' if m.last else 'WAITING'),11,accent if live else MUTED,anchor='e',bold=True)
  if not m.last:
   text(330,165,'No transmitter heard yet',15,MUTED,anchor='center')
   text(330,195,'Program a robot with ID '+str(rid),11,MUTED,anchor='center');return
  text(18,54,f'{m.rssi} dBm  ·  {m.received} packets  ·  {m.missed} USB gaps  ·  {now-m.last:.1f}s ago',9,MUTED)
  # Stylized top view follows Maqueen component arrangement.
  rect(45,133,80,302,'#070b10');rect(235,133,270,302,'#070b10')
  for y in range(140,300,15):rect(48,y,77,y+3,'#26313b');rect(238,y,267,y+3,'#26313b')
  c.create_polygon(*[v for xy in [(82,126),(110,87),(205,87),(233,126),(233,312),(82,312)] for v in (xy[0]*sx,xy[1]*sy)],fill='#233d4a',outline=accent)
  oval(105,91,145,122,'#a9bbc6');oval(171,91,211,122,'#a9bbc6');text(158,76,'ULTRASONIC',8,MUTED,anchor='center')
  cm=m.value('cm');text(158,137,('NO ECHO' if cm is None else f'{cm:.1f} cm')+(' *' if not m.fresh('cm',now) else ''),10,anchor='center')
  rect(96,155,220,258,'#09111b');text(158,149,'micro:bit',9,MUTED,anchor='center')
  leds=m.value('leds','');valid=isinstance(leds,str) and len(leds)==25 and leds.isdigit()
  for yy in range(5):
   for xx in range(5):
    level=int(leds[yy*5+xx]) if valid else 0
    fill='#%02x%02x%02x'%(45+int(level/9*210),20+int(level/9*50),27+int(level/9*45))
    oval(116+xx*17,169+yy*17,126+xx*17,179+yy*17,fill)
  text(158,270,('LED LIVE' if m.fresh('leds',now) else 'LED STALE'),8,accent if m.fresh('leds',now) else MUTED,anchor='center')
  bits=m.value('line',0)
  for xx,label,mask in [(115,'L',4),(158,'C',2),(201,'R',1)]:
   oval(xx-10,285,xx+10,305,accent if bits&mask else '#617487')
   text(xx,319,label,8,anchor='center')
  text(158,341,'LINE SENSORS'+('  · stale' if not m.fresh('line',now) else ''),8,MUTED,anchor='center')
  mode=m.value('mode') or 'Idle';text(303,90,'MODE',9,MUTED);text(303,113,mode+(' · running' if m.value('active') else ' · stopped' if m.value('active') is False else ''),14,bold=True)
  batt=m.value('battery');text(303,150,'BATTERY',9,MUTED);text(630,150,'—' if batt is None else str(batt)+'%',11,anchor='e')
  rect(303,165,630,174,'#263a4c')
  if batt is not None:rect(303,165,303+327*max(0,min(100,batt))/100,174,accent)
  def field(y,label,key):
   value=m.value(key);out='—' if value is None else str(value)
   text(303,y,label,10,MUTED);text(630,y,out+(' *' if not m.fresh(key,now) else ''),10,anchor='e')
  field(199,'Light L / R','light');field(224,'Heading °','heading');field(249,'Tilt X / Y / Z','acc');field(274,'Temperature °C','temp')
  text(303,300,'A '+('PRESSED' if m.value('a') else 'released')+'    B '+('PRESSED' if m.value('b') else 'released'),10)
  event=next((e for e in reversed(m.events) if e[1][0]!='heartbeat'),None)
  if event:
   msg=str(event[1][0])+': '+str(event[1][1]);text(18,365,msg[:95],9,MUTED)
  codes=m.value('light_commands','000000');palette=['#253441','#ff4040','#40ff70','#ffff50','#4080ff','#e050ff','#40ffff','#ffffff']
  if len(codes)==6 and all(v in '01234567' for v in codes):
   for i,v in enumerate(codes):oval(85+i*25,350,102+i*25,362,palette[int(v)])
  text(18,375,'Light commands: headlights L/R, RGB 1–4',8,MUTED)
  text(303,346,'Sound '+str(m.value('sound','—'))+'  Logo '+str(m.value('logo','—'))+'  IR '+str(m.value('ir_activity','—')),9)
  text(303,368,'Mag µT '+str(m.value('magnetic_uT','—'))+'  Ambient '+str(m.value('microbit_light','—')),9,MUTED)
  tag=m.value('program_tag','unreported'); version=m.value('library_version','?'); runtime=m.value('runtime','?')
  expected=self.expected.get().strip()
  verified=m.fresh('program_tag',now) and m.fresh('library_version',now) and tag==expected and version=='1.0.0'
  text(303,320,('MATCH' if verified else 'CHECK')+'  '+str(tag)+'  /  '+str(version)+' '+str(runtime),9,accent if verified else '#ffbd69')
 def details(self):
  rid=self.selected.get();win=tk.Toplevel(self.root);win.title('Robot '+str(rid)+' / Sensor details');win.geometry('760x620')
  tree=ttk.Treeview(win,columns=('key','value','age'),show='headings')
  for k in ('key','value','age'):tree.heading(k,text=k.title());tree.column(k,width=240)
  tree.pack(fill='both',expand=True)
  def update():
   if not win.winfo_exists():return
   tree.delete(*tree.get_children());m=self.fleet.robots[rid];now=time.monotonic()
   for k,(v,t) in sorted(m.values.items()):tree.insert('','end',values=(k,str(v),f'{now-t:.1f}s'))
   win.after(500,update)
  update()
 def refresh(self):
  now=time.monotonic()
  while not self.q.empty():
   typ,value=self.q.get()
   if typ=='status':self.status.set(value)
   else:
    try:self.fleet.accept(value,now)
    except (ValueError,TypeError,KeyError):pass
  for i,c in enumerate(self.cards):self.draw(c,i+1,now)
  (ROOT/'wireless_status.json').write_text(json.dumps({str(i):{'age_s':now-m.last if m.last else None,'received':m.received,'missing':m.missed,'rssi':m.rssi,'values':{k:v[0] for k,v in m.values.items()}} for i,m in self.fleet.robots.items()},indent=2))
  if not self.closed.is_set():self.root.after(150,self.refresh)
 def close(self):self.closed.set();self.root.destroy()
if __name__=='__main__':
 import argparse
 parser=argparse.ArgumentParser(description='Read-only Maqueen wireless fleet dashboard')
 parser.add_argument('--port',default='COM5')
 parser.add_argument('--lesson',default='lesson1-v1')
 args=parser.parse_args()
 Dashboard(args.port,args.lesson).root.mainloop()

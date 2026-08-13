import React, {useState} from 'react';
import { createRoot } from 'react-dom/client';
import { Activity, AlertTriangle, BarChart3, Bell, CalendarDays, ChevronDown, CircleUserRound, Dumbbell, FileText, Gauge, HeartPulse, Home, LogOut, Menu, Play, ShieldCheck, Sparkles, Target, Upload, Users, Video, X } from 'lucide-react';
import { AreaChart, Area, ResponsiveContainer, XAxis, YAxis, Tooltip, BarChart, Bar, CartesianGrid } from 'recharts';
import './styles.css';

const trend = [
  {week:'W1', score:70, risk:58}, {week:'W2', score:74, risk:54},
  {week:'W3', score:77, risk:49}, {week:'W4', score:81, risk:45},
  {week:'W5', score:84, risk:41}, {week:'W6', score:88, risk:36}
];
const movements = [
  {name:'Squat', score:88, status:'Good'},
  {name:'Running', score:82, status:'Good'},
  {name:'Jump / Landing', score:76, status:'Needs focus'},
  {name:'Balance', score:81, status:'Good'}
];
const sessions = [
  ['12 Aug 2026','Squat','84','Moderate'],
  ['10 Aug 2026','Running','82','Low'],
  ['08 Aug 2026','Jump / Landing','76','Moderate'],
  ['05 Aug 2026','Squat','79','Moderate'],
];

function App(){
  const [page,setPage]=useState('Dashboard');
  const [menu,setMenu]=useState(false);
  const nav = [
    ['Dashboard',Home],['Analyze',Video],['Performance',BarChart3],
    ['Injury Risk',ShieldCheck],['History',CalendarDays],['Reports',FileText]
  ];
  return <div className="app">
    <aside className={menu?'sidebar open':'sidebar'}>
      <div className="brand"><div className="logo"><Activity size={22}/></div><div><b>SportAI</b><span>Performance Lab</span></div><button className="close" onClick={()=>setMenu(false)}><X size={18}/></button></div>
      <div className="nav-title">WORKSPACE</div>
      {nav.map(([label,Icon])=><button key={label} className={page===label?'nav active':'nav'} onClick={()=>{setPage(label);setMenu(false)}}><Icon size={19}/><span>{label}</span></button>)}
      <div className="nav-title">MANAGEMENT</div>
      <button className="nav" onClick={()=>setPage('Athletes')}><Users size={19}/><span>Athletes</span></button>
      <button className="nav" onClick={()=>setPage('Settings')}><Dumbbell size={19}/><span>Training</span></button>
      <div className="sidebar-bottom"><div className="mini-profile"><div className="avatar">RS</div><div><b>Rahul Sharma</b><span>Football · Midfielder</span></div></div><button className="logout"><LogOut size={17}/> Sign out</button></div>
    </aside>
    <main className="main">
      <header className="topbar"><button className="mobile-menu" onClick={()=>setMenu(true)}><Menu/></button><div className="crumb"><span>Workspace</span><b>/</b><strong>{page}</strong></div><div className="top-actions"><button className="icon-btn"><Bell size={19}/><i></i></button><div className="user"><div className="avatar small">RS</div><span>Rahul Sharma</span><ChevronDown size={16}/></div></div></header>
      {page==='Dashboard' ? <Dashboard setPage={setPage}/> : <GenericPage page={page} setPage={setPage}/>}
    </main>
  </div>
}

function Dashboard({setPage}){
 return <div className="content">
   <section className="hero"><div><div className="eyebrow"><Sparkles size={15}/> AI ATHLETE INSIGHTS</div><h1>Good morning, Rahul <span>👋</span></h1><p>Your performance is trending upward. Here's your latest training overview.</p></div><button className="primary" onClick={()=>setPage('Analyze')}><Upload size={18}/> Analyze new session</button></section>
   <section className="stats">
    <Stat title="Performance score" value="84" suffix="/100" change="+8.4%" icon={Gauge} positive/>
    <Stat title="Injury risk" value="Moderate" change="↓ 6% vs last session" icon={ShieldCheck} warning/>
    <Stat title="Sessions this month" value="12" change="+3 vs last month" icon={Target} positive/>
    <Stat title="Training load" value="High" change="+18% this week" icon={Dumbbell} warning/>
   </section>
   <section className="grid-2">
    <Card title="Performance trend" action="View history"><div className="chart"><ResponsiveContainer width="100%" height="100%"><AreaChart data={trend}><defs><linearGradient id="score" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopOpacity=".22"/><stop offset="100%" stopOpacity="0"/></linearGradient></defs><CartesianGrid strokeDasharray="3 3" vertical={false}/><XAxis dataKey="week" axisLine={false} tickLine={false}/><YAxis domain={[60,100]} axisLine={false} tickLine={false}/><Tooltip/><Area type="monotone" dataKey="score" stroke="var(--accent)" fill="url(#score)" strokeWidth={3}/></AreaChart></ResponsiveContainer></div></Card>
    <Card title="Injury risk indicators" action="Details"><div className="risk-list"><Risk name="Knee alignment" score={58} level="Moderate"/><Risk name="Landing stability" score={43} level="Moderate"/><Risk name="Left / right symmetry" score={29} level="Low"/><Risk name="Training load" score={67} level="High"/></div><div className="risk-note"><AlertTriangle size={17}/><div><b>Top concern</b><span>Training load increased 32% compared with your recent baseline.</span></div></div></Card>
   </section>
   <section className="grid-2">
    <Card title="Movement performance" action="Analyze" onAction={()=>setPage('Analyze')}><div className="movement-list">{movements.map(m=><div className="movement" key={m.name}><div className="movement-top"><span>{m.name}</span><b>{m.score}%</b></div><div className="progress"><span style={{width:m.score+'%'}}></span></div><small className={m.score<80?'attention':''}>{m.status}</small></div>)}</div></Card>
    <Card title="AI coach recommendations"><div className="coach"><div className="coach-icon"><Sparkles size={21}/></div><div><b>Your next focus</b><p>Your squat technique is strong, but landing stability needs attention. Keep your knee aligned with your foot during deceleration.</p></div></div><div className="recommendations"><Rec icon="✓" text="Practice controlled landing drills" tag="Technique"/><Rec icon="↗" text="Keep training load within baseline" tag="Recovery"/><Rec icon="◈" text="Retest jump mechanics next session" tag="Monitor"/></div></Card>
   </section>
   <section className="grid-3">
    <Card title="Training load"><div className="load-big"><span>High</span><b>742 AU</b></div><div className="load-bar"><i></i></div><div className="load-scale"><span>Low</span><span>Optimal</span><span>High</span><span>Very high</span></div><p className="muted">Consider an additional recovery session after today's workload.</p></Card>
    <Card title="Recovery"><div className="recovery"><div className="recovery-ring"><HeartPulse size={24}/><b>78%</b></div><div><b>Good recovery</b><p>Sleep and recent rest are supporting your current training.</p></div></div><div className="sleep"><span>Recovery readiness</span><b>78 / 100</b></div></Card>
    <Card title="Latest session"><div className="latest"><div className="video-thumb"><Play size={22}/></div><div><b>Squat analysis</b><span>12 Aug · 12 reps · 84/100</span><small>Moderate risk indicator</small></div></div><button className="outline full" onClick={()=>setPage('History')}>Open session</button></Card>
   </section>
   <Card title="Recent sessions" action="View all"><div className="table-wrap"><table><thead><tr><th>Date</th><th>Movement</th><th>Performance</th><th>Risk</th><th></th></tr></thead><tbody>{sessions.map((s,i)=><tr key={i}><td>{s[0]}</td><td>{s[1]}</td><td><b>{s[2]}/100</b></td><td><span className={'pill '+s[3].toLowerCase()}>{s[3]}</span></td><td><button className="more">•••</button></td></tr>)}</tbody></table></div></Card>
   <footer>SportAI · AI-generated movement insights are for performance and risk awareness, not medical diagnosis.</footer>
 </div>
}

function Stat({title,value,suffix,change,icon:Icon,positive,warning}){return <div className="stat"><div className={'stat-icon '+(warning?'warn':'')}><Icon size={20}/></div><div className="stat-body"><span>{title}</span><div><strong>{value}</strong>{suffix&&<em>{suffix}</em>}</div><small className={positive?'up':warning?'warn-text':''}>{change}</small></div></div>}
function Card({title,action,children,onAction}){return <section className="card"><div className="card-head"><h2>{title}</h2>{action&&<button onClick={onAction}>{action}<span>→</span></button>}</div>{children}</section>}
function Risk({name,score,level}){return <div className="risk"><div className="risk-head"><span>{name}</span><b>{level}</b></div><div className="progress riskbar"><span style={{width:score+'%'}}></span></div></div>}
function Rec({icon,text,tag}){return <div className="rec"><div className="rec-icon">{icon}</div><div><b>{text}</b><span>{tag}</span></div></div>}
function GenericPage({page,setPage}){return <div className="content"><section className="hero"><div><div className="eyebrow"><Sparkles size={15}/> SPORTAI WORKSPACE</div><h1>{page}</h1><p>This section is connected to the dashboard foundation. Build the feature-specific workflow here.</p></div>{page==='Analyze'&&<button className="primary"><Video size={18}/> Start camera</button>}</section><div className="empty"><div className="empty-icon">{page==='Analyze'?<Video/>:page==='Reports'?<FileText/>:<BarChart3/>}</div><h2>{page} workspace</h2><p>The dashboard is ready for backend/API integration. Connect this page to FastAPI endpoints and the MediaPipe analysis pipeline.</p>{page==='Analyze'&&<button className="primary" onClick={()=>setPage('Dashboard')}>Back to dashboard</button>}</div></div>}

createRoot(document.getElementById('root')).render(<App/>);

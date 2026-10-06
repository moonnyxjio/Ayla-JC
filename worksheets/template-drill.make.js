const fs=require('fs'),path=require('path');
const {chromium}=require('playwright');
const FONT_DIR=process.argv[2], OUT=process.argv[3];

const AX_MIN=["less than 30 minutes","30 minutes to 1 hour","1 to 2 hours","2 to 3 hours","3 hours or more"];
const AX_HR=["less than 1 hour","1 to 2 hours","2 to 3 hours","3 to 4 hours","4 hours or more"];
const AX_SLEEP=["less than 5 hours","5 to 6 hours","6 to 7 hours","7 to 8 hours","8 hours or more"];
const G={
 g1:{name:"수업 Graph 1",title:"The Average Time Teenagers Exercised per Day",act:"exercised",axis:AX_MIN,vals:[15,35,25,15,10],picks:[1,2,3]},
 g2:{name:"수업 Graph 2",title:"The Average Time Teenagers Played Computer Games per Day",act:"played computer games",axis:AX_HR,vals:[10,15,20,25,30],picks:[4,3,2]},
 s:{name:"새 그래프 A",title:"The Average Time Teenagers Slept per Day",act:"slept",axis:AX_SLEEP,vals:[10,20,35,25,10],picks:[2,3,1]},
 p:{name:"새 그래프 B",title:"The Average Time Teenagers Used Smartphones per Day",act:"used smartphones",axis:AX_HR,vals:[5,10,20,30,35],picks:[4,3,2]},
 b:{name:"새 그래프 C",title:"The Average Time Teenagers Read Books per Day",act:"read books",axis:AX_MIN,vals:[40,30,15,10,5],picks:[0,1,2]},
 t:{name:"새 그래프 D",title:"The Average Time Teenagers Watched TV per Day",act:"watched TV",axis:AX_HR,vals:[25,40,20,10,5],picks:[1,0,2]},
};
const wc=s=>s.trim().split(/\s+/).length;
const ans=g=>[
 `We asked 100 teenagers about the average time teenagers ${g.act} per day`,
 `Looking at the results`,
 ...g.picks.map(i=>`they ${g.act} for ${g.axis[i]} per day`),
 `As the amount of time teenagers ${g.act} increases`];
const lead=g=>["","",`${g.vals[g.picks[0]]}% said that`,`${g.vals[g.picks[1]]}% answered that`,`However, ${g.vals[g.picks[2]]}% said that`,""];
const N=["①","②","③","④","⑤","⑥"];

function chart(g,w=520){
  const W=520,H=230,L=34,R=8,T=30,B=46,max=g.vals.some(v=>v>40)?50:40,pw=W-L-R,ph=H-T-B,bw=pw/5,y=v=>T+ph-v/max*ph;
  let s=`<svg viewBox="0 0 ${W} ${H}" style="width:${w}px;max-width:100%"><text x="${W/2}" y="16" text-anchor="middle" font-size="13" font-weight="700" fill="#1c2621">${g.title}</text>`;
  for(let t=0;t<=max;t+=10)s+=`<line x1="${L}" x2="${W-R}" y1="${y(t)}" y2="${y(t)}" stroke="#d5ddd8"/><text x="${L-6}" y="${y(t)+4}" text-anchor="end" font-size="10" fill="#5d6b64">${t}</text>`;
  g.vals.forEach((v,i)=>{const x=L+i*bw+bw*.28,bwid=bw*.44;
    s+=`<rect x="${x}" y="${y(v)}" width="${bwid}" height="${T+ph-y(v)}" rx="3" fill="#2f62c9"/><text x="${x+bwid/2}" y="${y(v)-5}" text-anchor="middle" font-size="11" font-weight="700" fill="#1c2621">${v}%</text>`;
    const words=g.axis[i].split(" "),lines=[];let c="";words.forEach(wd=>{if((c+" "+wd).trim().length>11&&c){lines.push(c);c=wd}else c=(c+" "+wd).trim()});lines.push(c);
    lines.forEach((ln,j)=>s+=`<text x="${L+i*bw+bw/2}" y="${T+ph+14+j*12}" text-anchor="middle" font-size="10" fill="#5d6b64">${ln}</text>`)});
  return s+`</svg>`;
}
const line=(n=1)=>`<div class="ln"></div>`.repeat(n);
const tpl=[
 ["①","We asked 100 teenagers about <b class='v'>제목 그대로</b>","5 + 제목 단어 수","우리는 100명의 10대들에게 ~에 대해 물었다"],
 ["②","<u>Looking at the results</u>","4 (항상 같음)","그 결과들을 본다면"],
 ["③","they <b class='v'>동사</b> for <b class='t'>1등 막대 이름</b> per day","4 + 동사 + 막대","그들은 하루에 (1등 시간) 동안 ~했다"],
 ["④","they <b class='v'>동사</b> for <b class='t'>2등 막대 이름</b> per day","4 + 동사 + 막대","그들은 하루에 (2등 시간) 동안 ~했다"],
 ["⑤","they <b class='v'>동사</b> for <b class='t'>3등 막대 이름</b> per day","4 + 동사 + 막대","그들은 하루에 (3등 시간) 동안 ~했다"],
 ["⑥","<u>As</u> the amount of time teenagers <b class='v'>동사</b> increases","7 + 동사","10대들이 ~한 시간의 양이 증가함에 따라"],
];

const css=fs.readFileSync(path.join(FONT_DIR,'fonts.css'),'utf8');
let h=`<!doctype html><html lang="ko"><meta charset="utf-8"><style>${css}
@page{size:A4;margin:13mm 14mm}
*{box-sizing:border-box}
body{font-family:"Noto Sans KR",sans-serif;color:#1c2621;font-size:12.5pt;line-height:1.55;margin:0}
.page{page-break-after:always;display:flex;flex-direction:column;gap:12px}
.page:last-child{page-break-after:auto}
h1{font-size:22pt;font-weight:900;margin:0}
h2{font-size:16pt;font-weight:900;margin:0;display:flex;gap:10px;align-items:baseline}
.step{background:#1c2621;color:#fff;font-size:10pt;padding:2px 10px;border-radius:3px;font-weight:700}
.sub{color:#5d6b64;font-size:11pt}
.en{font-family:"IBM Plex Mono",monospace;font-weight:500}
table{border-collapse:collapse;width:100%}
td,th{border:1.2px solid #b9c4be;padding:7px 9px;vertical-align:middle;text-align:left}
th{background:#eef2ef;font-size:10.5pt}
.big td{font-size:12.5pt}
.no{font-size:16pt;font-weight:900;color:#2f62c9;text-align:center;width:36px}
b.v{background:#fff59a;padding:0 4px;border-radius:2px;font-family:"Noto Sans KR";font-weight:700}
b.t{background:#d9e5fb;padding:0 4px;border-radius:2px;font-family:"Noto Sans KR";font-weight:700}
u{text-decoration-thickness:2px;text-underline-offset:3px}
.box{border:2px solid #1c2621;border-radius:6px;padding:12px 14px}
.tip{background:#fffbd6;border:1.5px solid #e6d86a;border-radius:6px;padding:10px 14px}
.ln{border-bottom:1.3px solid #9aa9a1;height:30px}
.q{display:grid;grid-template-columns:32px 1fr;gap:4px 8px;align-items:end}
.q .n{font-size:14pt;font-weight:900;color:#2f62c9}
.q .k{grid-column:2;font-size:10.5pt;color:#5d6b64}
.q .pre{font-family:"IBM Plex Mono";font-size:11pt;color:#5d6b64}
.cnt{font-size:10pt;color:#5d6b64;white-space:nowrap}
.gap{font-family:"IBM Plex Mono";font-weight:500;letter-spacing:.02em}
.blank{display:inline-block;border-bottom:1.5px solid #1c2621;min-width:70px;height:1.1em}
.prep td{height:34px}
.ans{font-family:"IBM Plex Mono";font-size:8.6pt;line-height:1.35}
.ans td,.ans th{padding:2px 6px}
.ans th{font-size:9pt}
ol{margin:0;padding-left:22px}
</style><body>`;

// PAGE 1 — 한 장 요약
h+=`<div class="page">
<div><div class="sub">3학년 2학기 영어 서술쓰기 · Lesson 7 · 10월 7일(수)·8일(목)</div><h1>그래프가 바뀌어도 쓰는 6문장 템플릿</h1></div>
<div class="tip"><b>핵심:</b> 문장 6개는 <b>항상 같다.</b> 그래프가 바뀌면 딱 두 가지만 갈아 끼운다.<br>
<b class="v">노란 칸 = 동사</b> → 그래프 <b>제목</b>에 있는 말 그대로 (Exercised → exercised)<br>
<b class="t">파란 칸 = 시간</b> → 그래프 <b>막대 아래 글자</b> 그대로 (30 minutes to 1 hour)</div>
<table class="big"><tr><th></th><th>템플릿 (밑줄 칸에 쓸 영어)</th><th>단어 수</th></tr>
${tpl.map(r=>`<tr><td class="no">${r[0]}</td><td><span class="en">${r[1]}</span><div class="sub">${r[3]}</div></td><td class="cnt">${r[2]}</td></tr>`).join("")}</table>
<div class="box"><b>그래프 받으면 30초 준비 3단계</b><ol>
<li><b>제목</b>에서 동사 찾기: The Average Time Teenagers <b class="v">Exercised</b> per Day</li>
<li>막대 <b>큰 순서</b>로 1등·2등·3등 표시하기 → ③ ④ ⑤ 순서</li>
<li>1~3등 막대 <b>아래 글자</b> 그대로 베끼기 → <b class="t">파란 칸</b></li></ol></div>
<div class="tip"><b>①은 공짜 문장:</b> <span class="en">We asked 100 teenagers about</span> + <b>제목을 소문자로</b> 그대로.<br>
<span class="en">The Average Time Teenagers Exercised per Day</span> → <span class="en">…about the average time teenagers exercised per day</span><br>
<b>밑줄:</b> 답안지에서 ② <span class="en">Looking at the results</span> 와 ⑥ <span class="en">As …</span> 에 밑줄 긋기 (조건 4·5)</div>
</div>`;

// PAGE 2 — STEP 1 따라 쓰기 (Graph1)
const g1=G.g1,a1=ans(g1);
h+=`<div class="page"><h2><span class="step">STEP 1</span>보고 따라 쓰기 · 수업 Graph 1</h2>
<div class="sub">회색 문장을 보면서 아래 줄에 2번씩 쓴다. 쓰면서 소리 내어 읽기.</div>
${chart(g1,440)}
${a1.map((a,i)=>`<div class="q"><span class="n">${N[i]}</span><div><span class="pre">${lead(g1)[i]}</span> <span class="gap" style="color:#7a8a82">${a}</span> <span class="cnt">(${wc(a)}단어)</span></div>${line(2).replace(/<div class="ln"><\/div>/g,'<div></div><div class="ln"></div>')}</div>`).join("")}
</div>`;

// PAGE 3 — STEP 2 구멍 채우기 (Graph1, 핵심어 가림)
const hole=(s,keep)=>s.split(" ").map((w,j)=>keep(w,j)?w:`<span class="blank" style="min-width:${Math.max(40,w.length*11)}px"></span>`).join(" ");
const KEEP=new Set(["we","they","for","per","day","the","of","at","about","as","to","1","2","3","30","100"]);
h+=`<div class="page"><h2><span class="step">STEP 2</span>구멍 채우기 · 수업 Graph 1</h2>
<div class="sub">빈칸에 빠진 단어를 쓴다. 단어 수도 맞춰 본다. (그래프는 앞 장)</div>
${a1.map((a,i)=>`<div class="box" style="padding:10px 12px"><div class="q"><span class="n">${N[i]}</span><div class="gap" style="line-height:2.1"><span class="pre">${lead(g1)[i]}</span> ${hole(a,w=>KEEP.has(w.toLowerCase()))}</div><span class="k">${tpl[i][3]} · ${wc(a)}단어</span></div></div>`).join("")}
</div><div class="page"><h2><span class="step">STEP 3</span>한국어만 보고 템플릿 쓰기</h2>
<div class="sub">칸 이름(동사 / 1등 막대 …)까지 넣어서 템플릿 자체를 외워 쓴다.</div>
${tpl.map(r=>`<div class="q"><span class="n">${r[0]}</span><div class="k" style="grid-column:auto">${r[3]}</div><div></div><div class="ln" style="height:44px"></div><div></div><div class="ln" style="height:44px"></div></div>`).join("")}
<div class="tip">다 쓰면 1페이지 템플릿과 비교해서 빨간 펜으로 고치기. 틀린 칸만 3번 더 쓰기.</div>
</div>`;

// PAGES 4-6 — STEP 4 바뀐 그래프
const prac=[G.g2,G.s,G.p,G.b,G.t];
const pracBlock=(g,k)=>`<div style="display:flex;flex-direction:column;gap:8px;${k?'margin-top:6px':''}">
<h2><span class="step">STEP 4</span>${g.name} · 바뀐 그래프에 끼워 넣기</h2>
${chart(g,420)}
<table class="prep"><tr><th>동사 (제목에서)</th><th>1등 막대 → ③</th><th>2등 막대 → ④</th><th>3등 막대 → ⑤</th></tr><tr><td></td><td></td><td></td><td></td></tr></table>
${N.map((n,i)=>`<div class="q"><span class="n">${n}</span><div class="pre">${i==2?"___% said that":i==3?"___% answered that":i==4?"However, ___% said that":""}</div><div></div><div class="ln" style="height:46px"></div></div>`).join("")}
</div>`;
h+=`<div class="page">${pracBlock(prac[0],0)}</div>`;
for(let i=1;i<prac.length;i++) h+=`<div class="page">${pracBlock(prac[i],0)}</div>`;

// ANSWERS
h+=`<div class="page"><h2><span class="step">정답</span>STEP 4 정답 · 단어 수</h2>
<div style="display:flex;flex-direction:column;gap:8px">${prac.map(g=>{const a=ans(g),l=lead(g);return `<table class="ans"><tr><th colspan="3">${g.name} · ${g.title}</th></tr>${a.map((x,i)=>`<tr><td class="no" style="font-size:11pt;width:28px">${N[i]}</td><td>${l[i]?l[i]+" ":""}<b>${x}</b></td><td class="cnt">${wc(x)}단어</td></tr>`).join("")}</table>`}).join("")}</div>
<div class="sub">숫자(100, 30, 1 …)는 한 단어로 센다. 대소문자는 채점하지 않는다. ③④⑤는 막대가 큰 순서.</div>
</div>`;
h+=`</body></html>`;
const htmlPath=path.join(FONT_DIR,'sheet.html');fs.writeFileSync(htmlPath,h);
(async()=>{const b=await chromium.launch();const p=await b.newPage();await p.goto('file://'+htmlPath,{waitUntil:'networkidle'});await p.evaluate(()=>document.fonts.ready);
await p.pdf({path:OUT,format:'A4',preferCSSPageSize:true,printBackground:true});await b.close();console.log('done')})();

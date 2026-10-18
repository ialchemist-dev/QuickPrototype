const assert=require('node:assert/strict'),P=require('./physics');
const near=(a,b,t=1e-8)=>assert(Math.abs(a-b)<t,`${a} != ${b}`);
const energy=b=>.5*(b.vx*b.vx+b.vy*b.vy)+.2*P.R**2*(b.wx*b.wx+b.wy*b.wy+b.wz*b.wz);
let a=P.ball(.5,.5),b=P.ball(.5+2*P.R,.5);a.vx=2;P.collide(a,b,{...P.defaults,restitution:1,ballFriction:0});near(a.vx,0);near(b.vx,2);
a=P.ball(.5,.5);b=P.ball(.5+2*P.R,.5);a.vx=2;a.vy=.5;a.wz=30;let before=energy(a)+energy(b),px=a.vx+b.vx,py=a.vy+b.vy;P.collide(a,b,P.defaults);near(a.vx+b.vx,px);near(a.vy+b.vy,py);assert(energy(a)+energy(b)<=before+1e-8);
a=P.ball(1,.5);a.vx=1;for(let i=0;i<200;i++)P.cloth(a,{...P.defaults,roll:0},P.DT);near(a.vx,5/7,1e-6);near(a.vx-P.R*a.wy,0,1e-6);
for(const top of [-.85,0,.85]){const p={...P.defaults,top,power:2.8,cue:{x:.75,y:.635},object:{x:1.12,y:.635}};const r=P.simulate(p);assert(r.events.length);const index=Math.round((r.events[0].time+.12)/.01),v=r.frames[index][0].vx;if(top<0)assert(v<0,'draw must reverse cue');if(top>0)assert(v>0,'follow must advance cue');for(const frame of r.frames)for(const b of frame){assert(Object.values(b).filter(v=>typeof v==='number').every(Number.isFinite));assert(b.x>=P.R-1e-8&&b.x<=P.W-P.R+1e-8);assert(b.y>=P.R-1e-8&&b.y<=P.H-P.R+1e-8);}}
for(let i=0;i<20;i++){const r=P.simulate({...P.defaults,angle:i*18,side:Math.sin(i),top:0,power:5});const first=r.frames[0].reduce((s,b)=>s+energy(b),0);for(const frame of r.frames)assert(frame.reduce((s,b)=>s+energy(b),0)<=first+1e-5,'energy cannot grow');}
console.log('PASS: elastic transfer, momentum, collision dissipation, sliding-to-rolling, draw/follow, bounds, finite states, energy across 20 shots.');

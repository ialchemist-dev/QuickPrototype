(function(root){
'use strict';
const R=.028575,W=2.54,H=1.27,DT=1/1000,G=9.81;
const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
function ball(x,y){return {x,y,vx:0,vy:0,wx:0,wy:0,wz:0,phase:'rest'};}
function initial(p){const a=p.angle*Math.PI/180,c=Math.cos(a),s=Math.sin(a),v=p.power;
const b=ball(p.cue.x,p.cue.y);b.vx=v*c;b.vy=v*s;
// Uniform sphere I=2mR²/5; normalized cue offsets limited to 0.6R.
b.wx=-s*2.5*.6*p.top*v/R;b.wy=c*2.5*.6*p.top*v/R;b.wz=-2.5*.6*p.side*v/R;
return [b,ball(p.object.x,p.object.y)];}
function cloth(b,p,dt){const ux=b.vx-R*b.wy,uy=b.vy+R*b.wx,u=Math.hypot(ux,uy);
if(u>1e-7){const dv=Math.min(p.slide*G*dt,u/3.5),fx=-dv*ux/u,fy=-dv*uy/u;b.vx+=fx;b.vy+=fy;b.wx+=2.5*fy/R;b.wy-=2.5*fx/R;b.phase='sliding';}
else {const v=Math.hypot(b.vx,b.vy),f=v?Math.max(0,1-p.roll*G*dt/v):0;b.vx*=f;b.vy*=f;b.wx=-b.vy/R;b.wy=b.vx/R;b.phase=v>1e-5?'rolling':'rest';}
b.wz=Math.sign(b.wz)*Math.max(0,Math.abs(b.wz)-p.spinDecay*dt);
b.x+=b.vx*dt;b.y+=b.vy*dt;}
function collide(a,b,p){const dx=b.x-a.x,dy=b.y-a.y,d=Math.hypot(dx,dy);if(d>2*R+1e-12||d<1e-12)return false;
const nx=dx/d,ny=dy/d,tx=-ny,ty=nx,over=Math.max(0,2*R-d);a.x-=nx*over/2;a.y-=ny*over/2;b.x+=nx*over/2;b.y+=ny*over/2;
const vn=(b.vx-a.vx)*nx+(b.vy-a.vy)*ny;if(vn>=0)return false;
const j=-(1+p.restitution)*vn/2;
const slip=(b.vx-a.vx)*tx+(b.vy-a.vy)*ty-R*(a.wz+b.wz);
const jt=clamp(-slip/7,-p.ballFriction*j,p.ballFriction*j);
a.vx-=j*nx+jt*tx;a.vy-=j*ny+jt*ty;b.vx+=j*nx+jt*tx;b.vy+=j*ny+jt*ty;
a.wz-=2.5*jt/R;b.wz-=2.5*jt/R;return true;}
function rail(b,nx,ny,p){const vn=b.vx*nx+b.vy*ny;if(vn>=0)return;
const tx=-ny,ty=nx,j=-(1+p.railRestitution)*vn,slip=b.vx*tx+b.vy*ty-R*b.wz;
const jt=clamp(-slip/3.5,-p.railFriction*j,p.railFriction*j);
b.vx+=j*nx+jt*tx;b.vy+=j*ny+jt*ty;b.wz-=2.5*jt/R;}
function step(bs,p,dt=DT){bs.forEach(b=>cloth(b,p,dt));const hit=collide(bs[0],bs[1],p);
for(const b of bs){if(b.x<R){b.x=R;rail(b,1,0,p);}if(b.x>W-R){b.x=W-R;rail(b,-1,0,p);}if(b.y<R){b.y=R;rail(b,0,1,p);}if(b.y>H-R){b.y=H-R;rail(b,0,-1,p);}}return hit;}
function simulate(p){const bs=initial(p),frames=[bs.map(b=>({...b}))],events=[];let still=0;
for(let i=1;i<=30000;i++){if(step(bs,p))events.push({time:i*DT,x:(bs[0].x+bs[1].x)/2,y:(bs[0].y+bs[1].y)/2});if(i%10===0)frames.push(bs.map(b=>({...b})));
if(bs.every(b=>Math.hypot(b.vx,b.vy)<.0001&&Math.hypot(b.wx,b.wy,b.wz)<.001))still++;else still=0;if(still>20)break;}
return {frames,events,duration:(frames.length-1)*.01};}
const defaults={angle:0,power:2.3,top:0,side:0,slide:.2,roll:.012,spinDecay:8,ballFriction:.06,restitution:.96,railRestitution:.8,railFriction:.18,cue:{x:.6,y:.635},object:{x:1.35,y:.65}};
const api={R,W,H,DT,initial,cloth,collide,step,simulate,defaults,ball};if(typeof module!=='undefined')module.exports=api;else root.Physics=api;
})(typeof window!=='undefined'?window:globalThis);

const {test, before, after}=require('node:test');
const assert=require('node:assert/strict');
const {spawn}=require('node:child_process');
let child;
const base='http://127.0.0.1:3030';
before(async()=>{
 child=spawn(process.execPath,['app.js'],{stdio:'inherit'});
 for(let i=0;i<60;i++){
  try{const r=await fetch(base+'/health');if(r.ok)return;}catch{}
  await new Promise(r=>setTimeout(r,500));
 }
 throw new Error('Backend failed to become healthy');
});
after(()=>child?.kill());
test('seeded dealers, filter, dealer and reviews',async()=>{
 const all=await (await fetch(base+'/fetchDealers')).json();assert.ok(all.length>0);
 const selected=all[0];
 const filtered=await (await fetch(base+'/fetchDealers/'+encodeURIComponent(selected.state))).json();
 assert.ok(filtered.length>0);assert.ok(filtered.every(x=>x.state===selected.state));
 const detail=await (await fetch(base+'/fetchDealer/'+selected.id)).json();assert.equal(detail[0].id,selected.id);
 const reviews=await fetch(base+'/fetchReviews/dealer/'+selected.id);assert.equal(reviews.status,200);
 assert.equal((await fetch(base+'/fetchDealer/not-an-id')).status,400);
});
test('posted reviews persist and receive unique ids',async()=>{
 const dealers=await (await fetch(base+'/fetchDealers')).json();
 const review={name:'Integration Tester',dealership:dealers[0].id,review:'Helpful and professional staff',purchase:true,purchase_date:'2026-10-28',car_make:'Toyota',car_model:'Camry',car_year:2024};
 const responses=await Promise.all([1,2].map(()=>fetch(base+'/insert_review',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(review)})));
 const posted=await Promise.all(responses.map(r=>r.json()));
 assert.ok(responses.every(r=>r.status===201));assert.notEqual(posted[0].id,posted[1].id);
 const saved=await (await fetch(base+'/fetchReviews/dealer/'+review.dealership)).json();
 assert.ok(saved.some(x=>x.id===posted[0].id));
});

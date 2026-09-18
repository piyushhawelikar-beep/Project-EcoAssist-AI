async function classifyWaste(){
 const item=document.getElementById('item').value.trim(), box=document.getElementById('classification');
 if(!item){box.textContent="Please enter an item first.";return}
 box.textContent="Analysing...";
 const res=await fetch('/api/classify',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({item})});
 const d=await res.json();
 if(d.error){box.textContent=d.error;return}
 box.innerHTML=`<h3>${d.label} <span class="pill">${Math.round(d.confidence*100)}% indicative confidence</span></h3>
 <p><b>Suggested route:</b> ${d.bin}</p><p><b>Category:</b> ${d.category}</p>
 <b>Steps</b><ul>${d.steps.map(s=>`<li>${s}</li>`).join('')}</ul><p>💡 ${d.tip}</p><small>${d.disclaimer}</small>`;
}
async function chat(){
 const input=document.getElementById('message'), msg=input.value.trim();if(!msg)return;
 const log=document.getElementById('chatlog');log.innerHTML+=`<div class="user">${escapeHtml(msg)}</div>`;input.value='';
 const res=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:msg})});
 const d=await res.json();log.innerHTML+=`<div class="bot">${escapeHtml(d.reply)}</div>`;log.scrollTop=log.scrollHeight;
}
async function calculateImpact(){
 const actions=[...document.querySelectorAll('.actions input:checked')].map(x=>x.value);
 const res=await fetch('/api/impact',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({actions})});
 const d=await res.json();document.getElementById('impact').textContent=`🌟 ${d.level} — ${d.score} points. ${d.message}`;
}
function escapeHtml(s){return s.replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}

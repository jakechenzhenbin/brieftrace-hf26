"use strict";
const $=s=>document.querySelector(s);
let last=null, ready=false, synthetic=false;
const labels={related:"Related wording",boundary:"Boundary to check",review:"Needs review"};
function el(tag,text,cls){const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;}
function resetResults(){last=null;$('#results').hidden=true;$('#findings').replaceChildren();}
async function example(){try{const r=await fetch('/api/example');if(!r.ok)throw Error('Example unavailable');const d=await r.json();$('#brief').value=d.brief;$('#requests').value=d.requests;synthetic=true;resetResults();$('#error').textContent='Fictional bakery example loaded. No real customer data.';}catch(e){$('#error').textContent=e.message;}}
for(const id of ['#brief','#requests'])$(id).addEventListener('input',()=>{synthetic=false;resetResults();});
$('#example').addEventListener('click',example);
$('#clear').addEventListener('click',()=>{$('#brief').value='';$('#requests').value='';$('#error').textContent='Text cleared from this page.';synthetic=false;resetResults();});
$('#analyze').addEventListener('click',async()=>{
  if(!ready){$('#error').textContent='Local model is not ready.';return;}
  $('#analyze').disabled=true;$('#error').textContent='';resetResults();
  try{
    const r=await fetch('/api/analyze',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({brief:$('#brief').value,requests:$('#requests').value})});
    const data=await r.json();if(!r.ok)throw Error(data.error||'Analysis failed');
    last=data;
    for(const f of data.findings){
      const section=el('article',undefined,'finding '+f.status);section.append(el('div',f.id,'ticket'));
      const content=el('div');content.append(el('span',labels[f.status],'status'),el('h3',f.request),el('p',f.note,'reason'));
      const top=f.matches[0],quote=el('div',undefined,'quote');quote.append(el('small',top.id+' / '+top.kind.toUpperCase()),el('p',top.source));content.append(quote);
      const details=el('details');details.append(el('summary','Show all retrieved evidence · similarity is not certainty'));
      const list=el('ul');for(const m of f.matches)list.append(el('li',`${m.id} · ${m.kind} · similarity ${m.similarity.toFixed(3)} — ${m.source}`));details.append(list);content.append(details);section.append(content);$('#findings').append(section);
    }
    const count=data.findings.filter(f=>f.status==='boundary').length;
    $('#summary').textContent=`${data.findings.length} requests traced. ${count} ${count===1?'boundary':'boundaries'} to check. Every decision stays with you.`;
    $('#run-note').textContent=`${synthetic?'Fictional example. ':''}${data.elapsed_ms} ms · ${data.model} · zero external model requests · no text stored`;
    $('#results').hidden=false;$('#results').scrollIntoView({behavior:'smooth',block:'start'});
  }catch(e){$('#error').textContent=e.message;}
  finally{$('#analyze').disabled=false;}
});
$('#export').addEventListener('click',()=>{
  if(!last)return;
  const out=['# BriefTrace review','',synthetic?'Fictional example; no real customer.':'User-entered material; review before sharing.','',last.limitations,''];
  for(const f of last.findings){out.push(`## ${f.id}: ${f.request}`,labels[f.status],f.note,'');for(const m of f.matches)out.push(`- ${m.id} (${m.kind}; similarity ${m.similarity}): ${m.source}`);out.push('');}
  out.push('Model: '+last.model,'Revision: '+last.model_revision,'','Prepared locally. No message sent.');
  const url=URL.createObjectURL(new Blob([out.join('\n')],{type:'text/markdown;charset=utf-8'}));const a=el('a');a.href=url;a.download='brieftrace-review.md';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
});
fetch('/api/health').then(async r=>{if(!r.ok)throw Error('Local model unavailable');await r.json();ready=true;$('#health').textContent='● Local model ready';}).catch(e=>{$('#health').textContent=e.message;});

const map = document.querySelector('#map');
const STORAGE_KEY = 'jocarsa-project-map-collapsed-v1';
let collapsed = new Set(JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]'));

function rememberCollapse(){
  localStorage.setItem(STORAGE_KEY, JSON.stringify([...collapsed]));
}
function applyCollapse(){
  document.querySelectorAll('.pair-node').forEach(node => {
    node.classList.toggle('collapsed', collapsed.has(node.dataset.key));
  });
}
applyCollapse();

map.addEventListener('click', e => {
  const toggle = e.target.closest('.toggle:not(.empty)');
  if(!toggle) return;
  e.stopPropagation();
  const node = toggle.closest('.pair-node');
  node.classList.toggle('collapsed');
  if(node.classList.contains('collapsed')) collapsed.add(node.dataset.key);
  else collapsed.delete(node.dataset.key);
  rememberCollapse();
});

async function saveTitle(input){
  const state = input.parentElement.querySelector('.save-state');
  state.textContent = 'guardando…';
  const body = new URLSearchParams({
    ajax:'1', node_key:input.dataset.key, titulo:input.value,
    descripcion:'', estado:'pendiente'
  });
  try{
    const r = await fetch(location.pathname,{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded;charset=UTF-8'},body});
    if(!r.ok) throw new Error();
    state.textContent='guardado';
    setTimeout(()=>{ if(state.textContent==='guardado') state.textContent=''; },1200);
  }catch(err){ state.textContent='error al guardar'; }
}

document.querySelectorAll('.inline-project-title').forEach(input => {
  let timer;
  input.addEventListener('input',()=>{ clearTimeout(timer); timer=setTimeout(()=>saveTitle(input),500); });
  input.addEventListener('blur',()=>{ clearTimeout(timer); saveTitle(input); });
  input.addEventListener('keydown',e=>{ if(e.key==='Enter'){ e.preventDefault(); input.blur(); } });
});

document.querySelector('#expand').onclick=()=>{
  collapsed.clear(); rememberCollapse(); applyCollapse();
};
document.querySelector('#collapse').onclick=()=>{
  document.querySelectorAll('.pair-node').forEach(n=>{ if(+n.dataset.level>0) collapsed.add(n.dataset.key); });
  rememberCollapse(); applyCollapse();
};

const search=document.querySelector('#search');
search.addEventListener('input',()=>{
  const q=search.value.trim().toLowerCase();
  document.querySelectorAll('.pair-node').forEach(n=>n.classList.remove('hidden-search'));
  if(!q){ applyCollapse(); return; }
  document.querySelectorAll('.pair-node').forEach(n=>{
    const project=n.querySelector(':scope > .pair-row .inline-project-title')?.value.toLowerCase() || '';
    const own=n.dataset.search.includes(q) || project.includes(q);
    const child=[...n.querySelectorAll('.pair-node')].some(x=>x.dataset.search.includes(q) || (x.querySelector(':scope > .pair-row .inline-project-title')?.value.toLowerCase()||'').includes(q));
    if(!own&&!child)n.classList.add('hidden-search');
    else n.classList.remove('collapsed');
  });
});

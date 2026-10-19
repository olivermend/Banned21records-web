
// BANNED 21 RECORDS - accessible artist tabs
(function(){
  const tabs = [...document.querySelectorAll('[data-band-target]')];
  const panels = [...document.querySelectorAll('[data-band-panel]')];
  if(tabs.length !== 2 || panels.length !== 2) return;
  function activate(name) {
    if(!tabs.some(tab=>tab.dataset.bandTarget===name)) return;
    tabs.forEach(tab => {
      const active = tab.dataset.bandTarget===name;
      tab.setAttribute('aria-selected',String(active));
      tab.tabIndex=active?0:-1;
    });
    panels.forEach(panel => { panel.hidden = panel.dataset.bandPanel!==name; });
  }
  tabs.forEach((tab,index)=>{
    tab.addEventListener('click',()=>activate(tab.dataset.bandTarget));
    tab.addEventListener('keydown',event=>{
      if(!['ArrowLeft','ArrowRight','Home','End'].includes(event.key))return;
      event.preventDefault();
      const next=event.key==='Home'?0:event.key==='End'?tabs.length-1:
        (index+(event.key==='ArrowRight'?1:-1)+tabs.length)%tabs.length;
      tabs[next].focus();
      activate(tabs[next].dataset.bandTarget);
    });
  });
  activate(location.hash==='#moderately-alive'?'moderately':'numbers');
})();

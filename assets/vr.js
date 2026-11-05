// Vakreceptie subpagina's: WhatsApp-knoppen (nummer niet zichtbaar in de bron) en het aanmeldformulier.
(()=>{
  const n=['31','6844','05','155'].join('');
  document.querySelectorAll('[data-wa]').forEach(a=>{a.href='https://wa.me/'+n+'?text='+encodeURIComponent(a.dataset.wa)});
  const HOOK='https://hook.eu2.make.com/uvwot045d9trtr535ks4vfhctej8u6ep';
  document.querySelectorAll('form.aanmeld').forEach(f=>{
    const msg=f.querySelector('.formmsg'), btn=f.querySelector('button[type=submit]');
    f.addEventListener('submit',async e=>{
      e.preventDefault();
      if(!f.reportValidity())return;
      const d=new URLSearchParams(new FormData(f));
      d.set('pagina',location.pathname);
      btn.disabled=true;const t=btn.textContent;btn.textContent='Versturen…';
      msg.className='formmsg';
      try{
        const r=await fetch(HOOK,{method:'POST',body:d});
        if(!r.ok)throw new Error(r.status);
        f.closest('.formwrap').classList.add('sent');
        msg.className='formmsg ok';
        msg.innerHTML='<b>Gelukt, bedankt!</b> Je krijgt zo een bevestiging per e-mail met je keuze, de prijs en hoe je betaalt. Iemand van het Vakreceptie-team neemt zo snel mogelijk persoonlijk contact met je op.';
        msg.scrollIntoView({behavior:'smooth',block:'center'});
      }catch(err){
        msg.className='formmsg err';
        msg.innerHTML='Versturen lukte niet. Probeer het nog eens, of stuur ons een <a data-wa-err href="#">WhatsApp-bericht</a>.';
        const a=msg.querySelector('[data-wa-err]');a.href='https://wa.me/'+n+'?text='+encodeURIComponent(f.dataset.wa||'PILOT: ik wil me aanmelden');a.target='_blank';
        btn.disabled=false;btn.textContent=t;
      }
    });
  });
})();

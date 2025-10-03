(function(){
  const root = document.getElementById('showreel');
  if(!root) return;

  // أي عنصر عنده class="slide" (div أو img أو video)
  const slides = Array.from(root.querySelectorAll('.slide'));
  if(slides.length === 0) return;

  let i = 0, timer = null;

  function show(idx){
    slides.forEach((s,j)=>{
      if(j===idx){
        s.classList.add('active');
        s.style.zIndex = 2;
        // شغّل الفيديو لو موجود
        if(s.tagName === 'VIDEO'){
          try { s.muted = true; s.playsInline = true; s.currentTime = 0; s.play().catch(()=>{}); } catch(e){}
        }
      }else{
        s.classList.remove('active');
        s.style.zIndex = 1;
        if(s.tagName === 'VIDEO'){
          try { s.pause(); } catch(e){}
        }
      }
    });
    // للاطمئنان
    try{ console.debug('[slider] active index:', idx, '/', slides.length); }catch(e){}
  }

  function start(){
    if(slides.length < 2){
      // عنصر واحد: خليه ظاهر وخلاص
      slides[0].classList.add('active');
      slides[0].style.zIndex = 2;
      if(slides[0].tagName === 'VIDEO'){
        try { slides[0].muted = true; slides[0].playsInline = true; slides[0].play().catch(()=>{}); } catch(e){}
      }
      return;
    }
    show(0);
    timer = setInterval(()=>{
      i = (i + 1) % slides.length;
      show(i);
    }, 3500);
  }

  start();

  // وقف السلايدر لو التبويب مش ظاهر (اختياري)
  document.addEventListener('visibilitychange', ()=>{
    if(document.hidden && timer){ clearInterval(timer); timer=null; }
    else if(!document.hidden && !timer && slides.length>1){
      timer = setInterval(()=>{ i = (i + 1) % slides.length; show(i); }, 3500);
    }
  });
})();

/* Software open/close */
(function(){
  const btn=document.querySelector('.soft-toggle');
  const wrap=document.getElementById('soft-wrap');
  if(!btn||!wrap) return;
  btn.addEventListener('click', ()=>{
    const open = wrap.classList.toggle('open');
    wrap.hidden = !open;
    btn.setAttribute('aria-expanded', String(open));
  });
})();

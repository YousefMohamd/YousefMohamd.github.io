(function(){
  var cssPath = '/css/projects-override.css';
  var link = document.createElement('link');
  link.rel = 'stylesheet';
  link.href = cssPath + '?v=' + Date.now();
  document.head.appendChild(link);

  fetch(cssPath + '?v=' + Date.now(), {cache: "no-store"})
    .then(function(r){ return r.text(); })
    .then(function(text){
      var s = document.createElement('style');
      s.setAttribute('data-injected','projects-override');
      s.appendChild(document.createTextNode(text));
      document.head.appendChild(s);
    }).catch(function(){});
})();

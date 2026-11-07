/* A direct visit starts at the product cover; an explicit hash keeps its target. */
if('scrollRestoration' in history)history.scrollRestoration='manual';
if(!window.location.hash){
  var resetInitialScroll=function(){window.scrollTo(0,0);};
  resetInitialScroll();
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',resetInitialScroll,{once:true});
  window.addEventListener('load',resetInitialScroll,{once:true});
}

document.addEventListener('DOMContentLoaded',function(){
  var productMenu=document.querySelector('.top .vp-nav-menu, .top2 .vp-nav-menu, .vp-nav-menu');
  var languageMenu=document.querySelector('.top .vp-language-switch, .top2 .vp-language-switch, .vp-language-switch');
  if(!productMenu||!languageMenu)return;
  productMenu.addEventListener('toggle',function(){if(productMenu.open)languageMenu.open=false;});
  languageMenu.addEventListener('toggle',function(){if(languageMenu.open)productMenu.open=false;});
  document.addEventListener('click',function(event){
    if(!productMenu.contains(event.target))productMenu.open=false;
    if(!languageMenu.contains(event.target))languageMenu.open=false;
  });
  document.addEventListener('keydown',function(event){
    if(event.key==='Escape'){productMenu.open=false;languageMenu.open=false;}
  });
  languageMenu.querySelectorAll('a[href]').forEach(function(link){
    link.addEventListener('click',function(){languageMenu.open=false;});
  });
  productMenu.querySelectorAll('a[href]').forEach(function(link){
    link.addEventListener('click',function(){productMenu.open=false;});
  });
  /* The dropdown hangs from the fixed header. Close it as soon as the page
     moves, otherwise it keeps covering content such as the fishbone diagram. */
  var closeBoth=function(){
    if(productMenu.open)productMenu.open=false;
    if(languageMenu.open)languageMenu.open=false;
  };
  window.addEventListener('scroll',closeBoth,{passive:true});
  window.addEventListener('resize',closeBoth);
});

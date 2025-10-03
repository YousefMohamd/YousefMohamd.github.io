document.querySelectorAll(".snip1273.hover").forEach(function(card){
  card.addEventListener("mouseleave", function(){
    card.classList.remove("hover");
  });
});
$(".hover").mouseleave(function () {
  $(this).removeClass("hover");
});
document.querySelectorAll(".snip1273").forEach(card => {
  card.addEventListener("mouseleave", function () {
    card.classList.remove("hover");
  });
});

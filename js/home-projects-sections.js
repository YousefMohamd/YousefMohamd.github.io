document.addEventListener("DOMContentLoaded", function() {
  // Pure Vanilla JS replacement for Hover state toggles
  const snipCards = document.querySelectorAll(".snip1273, .hover");
  
  snipCards.forEach(function(card) {
    card.addEventListener("mouseleave", function() {
      card.classList.remove("hover");
    });
  });
});

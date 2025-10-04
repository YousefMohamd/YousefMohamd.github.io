// Showreel slider
(function() {
  const container = document.getElementById('showreel');
  if (!container) return;

  const slides = Array.from(container.querySelectorAll('.slide'));
  if (slides.length === 0) return;

  let currentIndex = 0;

  // Show first slide immediately
  slides[0].classList.add('active');
  
  // Preload first video if exists
  const firstVideo = slides[0].querySelector('video');
  if (firstVideo) {
    firstVideo.load();
    firstVideo.play().catch(() => {});
  }

  function showSlide(index) {
    slides.forEach((s, i) => {
      s.classList.toggle('active', i === index);
      const video = s.querySelector('video');
      if (video) {
        if (i === index) {
          video.currentTime = 0;
          video.play().catch(() => {});
        } else {
          video.pause();
        }
      }
    });
  }

  function nextSlide() {
    currentIndex = (currentIndex + 1) % slides.length;
    showSlide(currentIndex);
  }

  // Start rotation after 5 seconds
  setInterval(nextSlide, 5000);
})();

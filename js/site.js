// Showreel slider
(function() {
  const container = document.getElementById('showreel');
  if (!container) return;

  const slides = Array.from(container.querySelectorAll('.slide'));
  if (slides.length === 0) return;

  let currentIndex = 0;

  // إظهار أول شريحة فوراً
  slides[0].classList.add('active');

  // تشغيل أول فيديو لو موجود
  const firstVideo = slides[0].querySelector('video');
  if (firstVideo) {
    firstVideo.play().catch(() => {});
  }

  function showSlide(index) {
    slides.forEach((s, i) => {
      s.classList.toggle('active', i === index);
      const video = s.querySelector('video');

      if (video) {
        if (i === index) {
          // تشغيل الفيديو للشريحة النشطة فقط
          video.currentTime = 0;
          video.play().catch(() => {});
        } else {
          // إيقاف الفيديوهات في الشرائح المخفية لتوفير الأداء
          video.pause();
        }
      }
    });
  }

  function nextSlide() {
    currentIndex = (currentIndex + 1) % slides.length;
    showSlide(currentIndex);
  }

  // تغيير الشريحة كل 5 ثواني
  setInterval(nextSlide, 5000);
})();

// Facade Pattern for Vimeo videos
document.addEventListener("DOMContentLoaded", function () {
  const videoWrappers = document.querySelectorAll(".video-wrapper");

  videoWrappers.forEach((wrapper) => {
    const playButton = wrapper.querySelector(".facade-play-btn");
    const iframe = wrapper.querySelector("iframe");

    if (playButton) {
      playButton.addEventListener("click", function () {
        playButton.style.display = "none"; // Hide the play button
        wrapper.classList.add("is-playing"); // Add the playing class for visual effects

        if (iframe) {
          iframe.src = iframe.dataset.src; // Set the iframe source
        }

        wrapper.style.cursor = "default";
      });
    }
  });
});

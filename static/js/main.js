/**
 * FlaskCraft Client Asset Script
 * Handles micro-interactions, copy handlers, and scroll effects
 */
document.addEventListener("DOMContentLoaded", () => {
  // Sticky Navbar scroll effect
  const header = document.querySelector(".site-header");
  if (header) {
    window.addEventListener("scroll", () => {
      if (window.scrollY > 20) {
        header.style.boxShadow = "0 8px 30px rgba(0, 0, 0, 0.5)";
      } else {
        header.style.boxShadow = "none";
      }
    });
  }

  console.log("⚡ FlaskCraft static assets initialized successfully.");
});

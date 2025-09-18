(function () {
  function initializeMermaid() {
    if (window.mermaid && typeof window.mermaid.initialize === "function") {
      window.mermaid.initialize({ startOnLoad: true });
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initializeMermaid);
  } else {
    initializeMermaid();
  }
})();

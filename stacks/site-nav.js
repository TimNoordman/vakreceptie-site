(function () {
  function closeNav(nav, btn) {
    nav.classList.remove("is-open");
    if (btn) {
      btn.setAttribute("aria-expanded", "false");
      btn.setAttribute("aria-label", "Menu");
    }
  }

  function setup(nav) {
    if (!nav) return;
    var box = nav.querySelector(".w") || nav;
    if (!box) return;
    var btn = nav.querySelector(":scope > .w > .nav-toggle, :scope > .nav-toggle");
    if (!btn) btn = box.querySelector(".nav-toggle");
    if (!btn) {
      btn = document.createElement("button");
      btn.type = "button";
      btn.className = "nav-toggle";
      btn.setAttribute("aria-expanded", "false");
      btn.setAttribute("aria-label", "Menu");
      btn.innerHTML = "<span></span><span></span><span></span>";
      var logo = box.querySelector(".logo");
      if (logo) logo.insertAdjacentElement("afterend", btn);
      else box.appendChild(btn);
    }
    if (btn.getAttribute("data-bound") === "1") return;
    btn.setAttribute("data-bound", "1");
    btn.addEventListener("click", function (ev) {
      ev.preventDefault();
      ev.stopPropagation();
      var open = nav.classList.toggle("is-open");
      btn.setAttribute("aria-expanded", open ? "true" : "false");
      btn.setAttribute("aria-label", open ? "Menu sluiten" : "Menu");
    });
    nav.addEventListener("click", function (ev) {
      var a = ev.target && ev.target.closest ? ev.target.closest("a") : null;
      if (a && nav.contains(a)) closeNav(nav, btn);
    });
    document.addEventListener("keydown", function (ev) {
      if (ev.key === "Escape") closeNav(nav, btn);
    });
  }

  function run() {
    document.querySelectorAll("header.vr-nav, body > nav").forEach(setup);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", run);
  else run();
  window.addEventListener("load", run);
  var n = 0;
  var tick = setInterval(function () {
    run();
    if (++n > 25) clearInterval(tick);
  }, 200);
  if (window.MutationObserver) {
    new MutationObserver(run).observe(document.documentElement, { childList: true, subtree: true });
  }
})();

// Vaste WhatsApp-knop rechtsonder op elke pagina.
(function () {
  function knop() {
    if (document.getElementById("wa-vast")) return;
    var n = ["31", "6844", "05", "155"].join("");
    var a = document.createElement("a");
    a.id = "wa-vast";
    a.href = "https://wa.me/" + n + "?text=" + encodeURIComponent("PILOT: ik heb een vraag");
    a.target = "_blank";
    a.rel = "noopener";
    a.setAttribute("aria-label", "Stel je vraag via WhatsApp");
    a.innerHTML = '<svg width="26" height="26" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.45 1.32 4.95L2.05 22l5.25-1.38a9.87 9.87 0 0 0 4.74 1.21h.01c5.46 0 9.91-4.45 9.91-9.91 0-2.65-1.03-5.14-2.9-7.01A9.82 9.82 0 0 0 12.04 2zm0 1.67c2.2 0 4.26.86 5.82 2.42a8.2 8.2 0 0 1 2.41 5.83c0 4.54-3.7 8.23-8.24 8.23-1.48 0-2.93-.39-4.19-1.15l-.3-.17-3.12.82.83-3.04-.2-.32a8.19 8.19 0 0 1-1.26-4.38c0-4.54 3.7-8.24 8.25-8.24zM8.53 7.33c-.16 0-.43.06-.66.31-.22.25-.87.85-.87 2.07 0 1.22.89 2.4 1.01 2.56.12.17 1.75 2.67 4.23 3.74.59.26 1.05.41 1.41.52.59.19 1.13.16 1.56.1.48-.07 1.47-.6 1.67-1.18.21-.58.21-1.07.15-1.18-.07-.1-.23-.16-.48-.29-.25-.12-1.47-.72-1.69-.81-.23-.08-.39-.12-.56.13-.16.25-.64.81-.78.97-.15.17-.29.19-.54.06-.25-.12-1.05-.39-1.99-1.23-.74-.66-1.23-1.47-1.38-1.72-.14-.25-.01-.38.11-.5.11-.11.25-.29.37-.44.13-.14.17-.25.25-.41.08-.17.04-.31-.02-.43-.06-.13-.56-1.35-.77-1.84-.2-.48-.4-.42-.56-.43h-.48z"/></svg><span>App ons</span>';
    a.style.cssText = "position:fixed;right:max(16px,env(safe-area-inset-right));bottom:max(16px,env(safe-area-inset-bottom));z-index:60;display:inline-flex;align-items:center;gap:10px;min-height:56px;padding:0 20px 0 16px;border-radius:999px;background:#128C4B;color:#fff;font:700 17px/1 system-ui,-apple-system,'Segoe UI',Arial,sans-serif;text-decoration:none;box-shadow:0 8px 24px rgba(0,0,0,.28)";
    document.body.appendChild(a);
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", knop); else knop();
})();

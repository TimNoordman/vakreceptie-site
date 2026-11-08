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

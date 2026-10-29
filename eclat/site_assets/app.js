// Apparition douce des blocs au défilement. Sans JavaScript, tout reste visible.
(function () {
  var els = document.querySelectorAll(".reveal");
  if (!("IntersectionObserver" in window)) {
    els.forEach(function (el) { el.classList.add("in"); });
    return;
  }
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) { entry.target.classList.add("in"); io.unobserve(entry.target); }
    });
  }, { rootMargin: "0px 0px -8% 0px" });
  els.forEach(function (el) { io.observe(el); });
  // Sécurité : tout afficher après 2 s même si l'observateur ne s'est pas déclenché.
  setTimeout(function () { els.forEach(function (el) { el.classList.add("in"); }); }, 2000);
})();

// Envoie chaque visiteur vers la boutique Amazon de son pays (si un identifiant Partenaire existe).
// Pays déduit de la langue du navigateur et du fuseau horaire ; aucun cookie, aucune donnée envoyée.
(function () {
  var stores = window.PAC_STORES;
  if (!stores) return;
  var tz = "";
  try { tz = Intl.DateTimeFormat().resolvedOptions().timeZone || ""; } catch (e) {}
  var byTz = { "Europe/London": "GB", "Europe/Paris": "FR", "Europe/Berlin": "DE", "Europe/Madrid": "ES",
    "Europe/Rome": "IT", "Europe/Brussels": "BE", "Europe/Amsterdam": "NL", "America/Toronto": "CA",
    "America/Vancouver": "CA", "America/Montreal": "CA", "Australia/Sydney": "AU", "Australia/Melbourne": "AU" };
  var region = byTz[tz];
  if (!region && /^America\//.test(tz)) region = "US";
  if (!region) { var m = (navigator.language || "").split("-")[1]; if (m) region = m.toUpperCase(); }
  var store = stores[region];
  if (!store) return;
  document.querySelectorAll('a[href*="amazon."]').forEach(function (a) {
    if (a.closest(".bs-links")) return; // la page Meilleures ventes garde ses liens par pays
    try {
      var u = new URL(a.href);
      if (u.pathname !== "/s" || u.hostname === store.d) return;
      u.hostname = store.d;
      u.searchParams.set("tag", store.t);
      a.href = u.toString();
    } catch (e) {}
  });
})();

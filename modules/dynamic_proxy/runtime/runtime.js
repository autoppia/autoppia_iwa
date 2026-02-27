(function () {
  const G = (globalThis.__DYN_CONFIG__ ||= {
    seed: Math.trunc(Number(new URL(location.href).searchParams.get("seed") || 0)) % 10000,
    levels: { D1: true, D3: true, D4: true },
    siteKey: location.host,
  });

  const DEFAULTS = {
    ignore: [
      "script",
      "style",
      "link",
      "meta",
      "head",
      "[data-dyn-ignore]",
      "[data-testid]",
      "[aria-live]",
      '[aria-busy="true"]',
      'input[type="hidden"]',
      'template',
    ],
    d1: { wrapProbability: 0.15, permuteSiblings: true, spacerProbability: 0.1 },
    d3: { renameIds: true, renameNames: false },
  };

  const OVERLAYS = [
    {
      id: "cookie",
      html:
        "<div data-dyn-overlay role=\"dialog\" aria-live=\"polite\" style=\"position:fixed;bottom:20px;left:20px;right:20px;max-width:420px;margin:auto;background:#0f172a;color:#fff;border-radius:14px;padding:18px;box-shadow:0 24px 50px rgba(15,23,42,0.3);font-family:system-ui,z sans-serif;\">" +
        "<strong style=\"display:block;margin-bottom:6px;\">Heads up</strong><p style=\"margin:0 0 12px;\">We keep a short session buffer active while you finish this flow.</p>" +
        "<div style=\"display:flex;gap:8px;flex-wrap:wrap;\"><button data-dyn-dismiss style=\"flex:1;min-width:140px;padding:10px 14px;border:none;border-radius:10px;background:#22c55e;color:#0f172a;font-weight:600;\">Acknowledge</button><button style=\"flex:1;min-width:120px;padding:10px 14px;border-radius:10px;border:1px solid rgba(148,163,184,0.45);background:transparent;color:#e2e8f0;\">Policy</button></div></div>",
    },
    {
      id: "banner",
      html:
        "<div data-dyn-overlay style=\"position:fixed;top:0;left:0;right:0;padding:12px 20px;background:#f97316;color:#0f172a;font-family:system-ui,z sans-serif;font-size:14px;box-shadow:0 10px 25px rgba(15,23,42,0.2);display:flex;justify-content:space-between;gap:16px;align-items:center;\">" +
        "<span style=\"font-weight:600;\">Dynamic review in progress</span>" +
        "<button data-dyn-dismiss style=\"padding:6px 14px;border:none;border-radius:999px;background:#0f172a;color:#fff;\">Dismiss</button></div>",
    },
    {
      id: "pulse",
      html:
        "<div data-dyn-overlay role=\"dialog\" aria-live=\"assertive\" style=\"position:fixed;right:18px;bottom:18px;width:320px;background:#fff;color:#0f172a;border-radius:16px;padding:18px;box-shadow:0 35px 60px rgba(15,23,42,0.35);font-family:system-ui,z sans-serif;\">" +
        "<p style=\"margin:0 0 8px;font-weight:600;\">Session heartbeat</p>" +
        "<p style=\"margin:0 0 16px;font-size:13px;color:#475569;\">Confirm activity so automated flows keep running.</p>" +
        "<button data-dyn-dismiss style=\"padding:9px 14px;border:none;border-radius:10px;background:#2563eb;color:#fff;width:100%;\">Continue</button></div>",
    },
  ];

  let SITE = null;
  let rngSeed = Math.trunc(Number(G.seed)) + 1;
  const rand = () => {
    rngSeed = (rngSeed ^ (rngSeed << 13)) >>> 0;
    rngSeed = (rngSeed ^ (rngSeed >>> 17)) >>> 0;
    rngSeed = (rngSeed ^ (rngSeed << 5)) >>> 0;
    return (rngSeed >>> 0) / 4294967296;
  };

  const hash36 = (str, seed) => {
    let h = 2166136261 ^ Math.trunc(Number(seed));
    let i = 0;
    while (i < str.length) {
      const code = str.codePointAt(i) ?? 0;
      h ^= code;
      h = Math.imul(h, 16777619);
      i += code > 0xffff ? 2 : 1;
    }
    return (h >>> 0).toString(36);
  };

  const mapId = (orig) => `dynid-${hash36("id:" + orig, G.seed)}`;
  const mapName = (orig) => `dynname-${hash36("name:" + orig, G.seed)}`;

  const isInteractive = (el) => el.matches('input,select,textarea,button,[contenteditable="true"],a[href]');
  const inIgnore = (el, ignoreList) => ignoreList.some((sel) => el.matches(sel));

  function mergeConf(base, site) {
    if (!site) return base;
    return {
      ignore: [...base.ignore, ...(site.ignore || [])],
      d1: { ...base.d1, ...(site.d1 || {}) },
      d3: { ...base.d3, ...(site.d3 || {}) },
    };
  }

  function applyD1(root, conf) {
    const blocks = root.querySelectorAll("main, section, article, form, nav, ul, ol, aside");
    blocks.forEach((el) => {
      if (inIgnore(el, conf.ignore)) return;
      if (rand() < conf.d1.wrapProbability && !el.closest("[data-dyn-wrapper]")) {
        const wrapper = document.createElement("div");
        wrapper.dataset.dynWrapper = "";
        wrapper.setAttribute("aria-hidden", "true");
        wrapper.style.pointerEvents = "none";
        wrapper.style.display = "contents";
        el.replaceWith(wrapper);
        wrapper.appendChild(el);
      }
    });

    if (conf.d1.permuteSiblings) {
      const containers = root.querySelectorAll("main, .container, [role=\"main\"], .content, .grid, .list");
      containers.forEach((container) => {
        if (inIgnore(container, conf.ignore)) return;
        const kids = Array.from(container.children).filter((child) => !inIgnore(child, conf.ignore));
        if (kids.length > 3 && rand() < 0.2) {
          const i = Math.trunc(kids.length * rand());
          const j = Math.trunc(kids.length * rand());
          if (i !== j && !isInteractive(kids[i]) && !isInteractive(kids[j])) {
            container.insertBefore(kids[i], kids[j]);
          }
        }
      });
    }

    if (conf.d1.spacerProbability > 0) {
      const targets = root.querySelectorAll("h1,h2,h3,.card,.panel,header,footer");
      targets.forEach((target) => {
        if (inIgnore(target, conf.ignore)) return;
        if (rand() < conf.d1.spacerProbability) {
          const spacer = document.createElement("div");
          spacer.dataset.dynSpacer = "";
          spacer.setAttribute("aria-hidden", "true");
          spacer.style.height = `${Math.floor(rand() * 8) + 2}px`;
          spacer.style.pointerEvents = "none";
          target.before(spacer);
        }
      });
    }
  }

  function applyD3(root, conf) {
    if (conf.d3.renameIds) {
      root.querySelectorAll("[id]").forEach((el) => {
        if (inIgnore(el, conf.ignore)) return;
        const orig = el.getAttribute("id");
        if (!orig) return;
        const next = mapId(orig);
        if (next !== orig) el.setAttribute("id", next);
      });

      root.querySelectorAll("label[for]").forEach((label) => {
        if (inIgnore(label, conf.ignore)) return;
        const f = label.getAttribute("for");
        if (!f) return;
        label.setAttribute("for", mapId(f));
      });
    }

    if (conf.d3.renameNames) {
      root.querySelectorAll("[name]").forEach((el) => {
        if (inIgnore(el, conf.ignore)) return;
        if (!isInteractive(el)) return;
        const orig = el.getAttribute("name");
        if (!orig) return;
        const next = mapName(orig);
        if (next !== orig) el.setAttribute("name", next);
      });
    }
  }

  const overlayState = { node: null, currentId: null };

  function selectOverlay() {
    if (overlayState.currentId) {
      const match = OVERLAYS.find((item) => item.id === overlayState.currentId);
      if (match) {
        return match;
      }
    }
    const hash = Number.parseInt(hash36(`${G.siteKey}:${G.seed}:overlay`, G.seed).slice(-5), 36) || 0;
    const def = OVERLAYS[hash % OVERLAYS.length];
    overlayState.currentId = def.id;
    return def;
  }

  function mountOverlay(def) {
    const tpl = document.createElement("template");
    tpl.innerHTML = def.html.trim();
    const node = tpl.content.firstElementChild;
    if (!node) return;
    node.dataset.dynOverlayId = def.id;
    node.dataset.dynOverlaySeed = String(G.seed);
    node.style.zIndex = "2147483647";
    node.style.position = node.classList?.contains("dyn-banner") ? "fixed" : node.style.position || "fixed";
    (document.body || document.documentElement).appendChild(node);
    const dismiss = node.querySelector("[data-dyn-dismiss]");
    if (dismiss) {
      dismiss.addEventListener(
        "click",
        () => {
          node.remove();
          overlayState.node = null;
        },
        { once: true },
      );
    }
    overlayState.node = node;
  }

  function ensureOverlay() {
    if (!G.levels?.D4) return;
    if (overlayState.node && document.body?.contains(overlayState.node)) {
      return;
    }
    const def = selectOverlay();
    mountOverlay(def);
  }

  const throttle = (fn, ms = 60) => {
    let token = null;
    return () => {
      if (token) return;
      token = setTimeout(() => {
        token = null;
        fn();
      }, ms);
    };
  };

  async function maybeLoadSiteConfig() {
    try {
      // Config fetch disabled; use defaults (SITE stays null)
    } catch (error_) {
      if (globalThis.__DYN_DEBUG__ !== undefined) globalThis.console.debug(error_);
    }
  }

  function updateDynamicMap(conf) {
    globalThis.__DYNAMIC_MAP__ = {
      seed: G.seed,
      d1: { wrapProbability: conf.d1.wrapProbability },
      d3: { renameIds: conf.d3.renameIds, renameNames: conf.d3.renameNames },
      d4: {
        overlayId: overlayState.currentId,
        present: Boolean(overlayState.node && document.body?.contains(overlayState.node)),
      },
    };
  }

  function applyAll() {
    const conf = mergeConf(DEFAULTS, SITE);
    if (G.levels?.D1) applyD1(document.body, conf);
    if (G.levels?.D3) applyD3(document.body, conf);
    if (G.levels?.D4) ensureOverlay();
    updateDynamicMap(conf);
  }

  function patchHistory() {
    const again = () => setTimeout(applyAll, 0);
    ["pushState", "replaceState"].forEach((fn) => {
      const orig = history[fn];
      history[fn] = function () {
        const result = orig.apply(this, arguments);
        again();
        return result;
      };
    });
    addEventListener("popstate", again);
  }

  const run = async () => {
    await maybeLoadSiteConfig();
    patchHistory();
    applyAll();
    const mo = new MutationObserver(throttle(applyAll, 60));
    mo.observe(document.body || document.documentElement, { childList: true, subtree: true });
  };

  if (document.readyState === "complete") run();
  else globalThis.addEventListener("load", run, { once: true });
})();

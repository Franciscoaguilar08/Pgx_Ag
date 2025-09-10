// ===== Helpers =====
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);
const resultsEl = $("#results");
const banner = $("#banner");

// Toast
function toast(msg, ms = 2200) {
  const t = $("#toast");
  t.textContent = msg;
  t.style.display = "block";
  setTimeout(() => (t.style.display = "none"), ms);
}

// Banner
function showBanner(msg) {
  banner.textContent = msg;
  banner.style.display = "block";
  setTimeout(() => (banner.style.display = "none"), 6000);
}

// ===== Tabs =====
const tabButtons = $$(".tab-btn");
const tabPanes = $$(".tab-pane");
tabButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    tabButtons.forEach((b) => b.classList.remove("active"));
    tabPanes.forEach((p) => p.classList.remove("active"));
    btn.classList.add("active");
    $("#tab-" + btn.dataset.tab).classList.add("active");
  });
});

// ===== Dropzone (VCF) =====
const drop = $("#drop");
const vcfInput = $("#vcf");
const fileName = $("#filename");
if (drop && vcfInput) {
  drop.addEventListener("click", () => vcfInput.click());
  vcfInput.addEventListener("change", () => {
    const f = vcfInput.files[0];
    fileName.textContent = f ? `Archivo: ${f.name}` : "";
  });
}

// ===== Tumor suggestions (debounced) =====
const tumorInput = $("#tumor_type");
const tumorSug = $("#tumor_suggestions");
let sugTimer = null;

function clearSuggestions() {
  tumorSug.classList.remove("show");
  tumorSug.innerHTML = "";
}

function renderSuggestions(items) {
  if (!items || !items.length) return clearSuggestions();
  tumorSug.innerHTML = items
    .map((s) => `<button type="button" data-value="${s}">${s}</button>`)
    .join("");
  tumorSug.classList.add("show");
  tumorSug.querySelectorAll("button").forEach((b) =>
    b.addEventListener("click", () => {
      tumorInput.value = b.dataset.value;
      clearSuggestions();
    })
  );
}

tumorInput?.addEventListener("input", () => {
  clearTimeout(sugTimer);
  const q = (tumorInput.value || "").trim();
  if (q.length < 2) return clearSuggestions();
  sugTimer = setTimeout(async () => {
    try {
      const r = await fetch("/suggest/tumors", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: q }),
      });
      if (r.ok) {
        const d = await r.json();
        renderSuggestions(d.suggestions || []);
      }
    } catch (e) {
      // silent
    }
  }, 250);
});
document.addEventListener("click", (e) => {
  if (!tumorSug.contains(e.target) && e.target !== tumorInput) clearSuggestions();
});

// ===== Manual variants dynamic rows =====
const mvContainer = $("#manual-variants-container");
$("#add-variant")?.addEventListener("click", () => {
  const row = document.createElement("div");
  row.className = "manual-variant row";
  row.innerHTML = `
    <input type="text" placeholder="Gen (ej: EGFR)" class="gene-input">
    <input type="text" placeholder="Variante (ej: L858R)" class="variant-input">
    <button class="icon remove-variant" title="Quitar">✕</button>
  `;
  mvContainer.appendChild(row);
  row.querySelector(".remove-variant").addEventListener("click", () => row.remove());
});
mvContainer?.querySelector(".remove-variant")?.addEventListener("click", (e) => {
  const parent = e.target.closest(".manual-variant");
  if (parent && mvContainer.children.length > 1) parent.remove();
});

// ===== Biomarkers dynamic rows =====
const bmContainer = $("#biomarkers-container");
$("#add-biomarker")?.addEventListener("click", () => {
  const row = document.createElement("div");
  row.className = "biomarker row";
  row.innerHTML = `
    <select class="biomarker-name">
      <option value="">Seleccionar biomarcador</option>
      <option value="MSI-H">MSI-H</option>
      <option value="PD-L1">PD-L1</option>
      <option value="TMB-H">TMB-H</option>
      <option value="HER2">HER2</option>
    </select>
    <select class="biomarker-status">
      <option value="positive">Positivo</option>
      <option value="negative">Negativo</option>
    </select>
    <button class="icon remove-biomarker" title="Quitar">✕</button>
  `;
  bmContainer.appendChild(row);
  row.querySelector(".remove-biomarker").addEventListener("click", () => row.remove());
});
bmContainer?.querySelector(".remove-biomarker")?.addEventListener("click", (e) => {
  const parent = e.target.closest(".biomarker");
  if (parent && bmContainer.children.length > 1) parent.remove();
});

// ===== Render Results (pretty) =====
function renderResults(data) {
  if (!data) {
    resultsEl.innerHTML = "<p>No hay resultados.</p>";
    return;
  }
  let html = `<div class="result-summary"><h3>Resumen</h3><p>${data.summary || "-"}</p></div>`;

  if (data.details && data.details.length) {
    html += `<div class="result-details">`;
    data.details.forEach((d) => {
      const alt = (d.clinical_context?.alternatives || []).join(", ") || "N/A";
      html += `
        <div class="detail-card">
          <h4>${d.action || "Acción"} → <span class="drug">${d.drug || "-"}</span></h4>
          <p><strong>Variante:</strong> ${d.variant?.gene || "-"} ${d.variant?.protein_change || "-"}</p>
          <p><strong>Evidencia:</strong> ${d.study_meta?.level || "-"} (${d.study_meta?.study_type || "-"}, ${d.study_meta?.year || "-"})</p>
          <p><strong>Contexto:</strong> ${d.clinical_context?.why_now || "-"}, ${d.clinical_context?.timing || "-"}</p>
          <p><strong>Alternativas:</strong> ${alt}</p>
          <div class="badges">
            ${d.mechanistic_badge ? '<span class="badge accent2">Mecanicista</span>' : ""}
            ${d.strict_badge ? '<span class="badge accent">Strict</span>' : ""}
          </div>
          <div class="refs">
            ${(d.references || []).map(r => `<a href="${r.url}" target="_blank" rel="noopener">${r.label}</a>`).join(" · ")}
          </div>
        </div>`;
    });
    html += `</div>`;
  }

  if (data.timeline && data.timeline.length) {
    html += `<div class="timeline"><h3>Proceso</h3><ul>`;
    data.timeline.forEach((t) => {
      html += `<li><strong>${t.title}</strong>: ${t.description} <span class="badge">${(t.tags || []).join(", ")}</span></li>`;
    });
    html += `</ul></div>`;
  }

  resultsEl.innerHTML = html;
}

// ===== Buttons =====
const analyzeBtn = $("#analyze");
const demoBtn = $("#demo");
const resetBtn = $("#reset");
const exportPdfBtn = $("#export_pdf");
const exportJsonBtn = $("#export_json");
const helpBtn = $("#help_btn");
const pathologyReport = $("#pathology-report");

analyzeBtn?.addEventListener("click", async () => {
  const fd = new FormData();
  fd.append("pseudonym", $("#pseudonym").value || "PGX-USER");
  fd.append("diagnosis", $("#diagnosis").value || "");
  fd.append("tumor_type", $("#tumor_type").value || "adenocarcinoma de pulmón");
  if (vcfInput?.files?.[0]) fd.append("vcf", vcfInput.files[0]);
  if (pathologyReport?.value) fd.append("pathology_report", pathologyReport.value);

  const r = await fetch("/analyze/unified", { method: "POST", body: fd, headers: { Accept: "application/json" } });
  let d;
  try { d = await r.json(); } catch {}
  if (!r.ok) return showBanner(typeof d === "object" ? JSON.stringify(d) : "Error al analizar");
  renderResults(d);
  toast("✔ Análisis completo");
});

demoBtn?.addEventListener("click", async () => {
  const r = await fetch("/analyze_demo");
  if (!r.ok) return showBanner("Error al cargar demo");
  const d = await r.json();
  renderResults(d);
  toast("Demo cargada");
});

resetBtn?.addEventListener("click", () => {
  $("#pseudonym").value = "";
  $("#diagnosis").value = "";
  $("#tumor_type").value = "";
  if (vcfInput) vcfInput.value = "";
  if (fileName) fileName.textContent = "";
  if (pathologyReport) pathologyReport.value = "";
  resultsEl.innerHTML = "";
  banner.style.display = "none";
  toast("Reseteado");
});

exportPdfBtn?.addEventListener("click", async () => {
  const payload = {
    patient: { pseudonym: $("#pseudonym").value || "PGX-USER", tumor_type: $("#tumor_type").value || "adenocarcinoma de pulmón" },
    result: { summary: "Reporte generado", details: [] },
  };
  const r = await fetch("/export/pdf", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
  if (!r.ok) return showBanner("Error al exportar PDF");
  const b = await r.blob();
  const url = URL.createObjectURL(b);
  const a = document.createElement("a");
  a.href = url; a.download = "PGx_Report.pdf"; a.click();
  URL.revokeObjectURL(url);
  toast("PDF descargado");
});

exportJsonBtn?.addEventListener("click", async () => {
  const payload = {
    patient: { pseudonym: $("#pseudonym").value || "PGX-USER", tumor_type: $("#tumor_type").value || "adenocarcinoma de pulmón" },
    result: { summary: "Reporte generado", details: [] },
  };
  const r = await fetch("/export/json", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
  if (!r.ok) return showBanner("Error al exportar JSON");
  const b = await r.blob();
  const url = URL.createObjectURL(b);
  const a = document.createElement("a");
  a.href = url; a.download = "PGx_Report.json"; a.click();
  URL.revokeObjectURL(url);
  toast("JSON descargado");
});

helpBtn?.addEventListener("click", () => {
  toast("Guía rápida: cargá VCF o variantes, elegí tumor y 'Analizar Todo'");
});

// ===== Health badges =====
async function loadHealth() {
  try {
    const r = await fetch("/health");
    if (!r.ok) return;
    const d = await r.json();
    const src = d?.sources || {};
    const ia = !!d?.ia;

    const map = {
      CIViC: src.CIViC,
      VEP: src.VEP,
      OncoKB: src.OncoKB,
      ClinVar: src.ClinVar,
      IA: ia
    };
    Object.entries(map).forEach(([k, ok]) => {
      const el = document.querySelector(`.chip[data-key="${k}"]`);
      if (el) {
        el.classList.remove("ok", "err");
        el.classList.add(ok ? "ok" : "err");
        el.title = ok ? "Disponible" : "No disponible";
      }
    });
  } catch {}
}
loadHealth();

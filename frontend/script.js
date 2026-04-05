const form = document.getElementById("finance-form");
const button = document.getElementById("generate-button");
const statusText = document.getElementById("form-status");
const resultsEmpty = document.getElementById("results-empty");
const resultsContent = document.getElementById("results-content");
const prevStepButton = document.getElementById("prev-step-button");
const nextStepButton = document.getElementById("next-step-button");
const prevOutputButton = document.getElementById("prev-output-button");
const nextOutputButton = document.getElementById("next-output-button");
const downloadReportButton = document.getElementById("download-report-button");
const progressBar = document.getElementById("wizard-progress-bar");
const progressCopy = document.getElementById("wizard-progress-copy");
const wizardSteps = Array.from(document.querySelectorAll(".wizard-step"));
const inputNavLinks = Array.from(document.querySelectorAll(".input-nav-link"));
const outputNavLinks = Array.from(document.querySelectorAll(".output-nav-link"));
const outputSections = Array.from(document.querySelectorAll(".output-step"));
const apiBase = window.location.port === "5000" ? "" : "http://127.0.0.1:5000";
const MAX_FILE_SIZE = 5 * 1024 * 1024;
let currentStep = 0;
let currentOutputIndex = 0;
let currentPlanId = null;

function formatCurrency(value) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(value || 0);
}

function renderList(targetId, items) {
  const target = document.getElementById(targetId);
  target.innerHTML = "";

  (items || []).forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    target.appendChild(li);
  });
}

function setActiveInputNav(index) {
  inputNavLinks.forEach((link, linkIndex) => {
    link.classList.toggle("is-active", linkIndex === index);
  });
}

function setActiveOutputNav(index) {
  currentOutputIndex = Math.max(0, Math.min(index, outputSections.length - 1));

  outputSections.forEach((section, sectionIndex) => {
    section.classList.toggle("hidden-step", sectionIndex !== currentOutputIndex);
  });

  outputNavLinks.forEach((link, linkIndex) => {
    link.classList.toggle("is-active", linkIndex === currentOutputIndex);
  });

  if (prevOutputButton) {
    prevOutputButton.disabled = currentOutputIndex === 0;
  }

  if (nextOutputButton) {
    nextOutputButton.disabled = currentOutputIndex === outputSections.length - 1;
  }
}

function showStep(index) {
  currentStep = Math.max(0, Math.min(index, wizardSteps.length - 1));

  wizardSteps.forEach((step, stepIndex) => {
    step.classList.toggle("hidden-step", stepIndex !== currentStep);
  });

  prevStepButton.disabled = currentStep === 0;
  nextStepButton.disabled = currentStep === wizardSteps.length - 1;
  progressBar.style.width = `${((currentStep + 1) / wizardSteps.length) * 100}%`;
  progressCopy.textContent = `Step ${currentStep + 1} of ${wizardSteps.length}`;
  setActiveInputNav(currentStep);
}

function validatePdfInput(inputName) {
  const input = form.querySelector(`input[name="${inputName}"]`);
  const hint = document.getElementById(`${inputName}-hint`);
  const file = input?.files?.[0];

  if (!input || !hint) return true;

  if (!file) {
    hint.textContent = "Upload a PDF up to 5 MB.";
    hint.classList.remove("field-error");
    return true;
  }

  const isPdf = file.type === "application/pdf" || file.name.toLowerCase().endsWith(".pdf");
  if (!isPdf) {
    hint.textContent = "Only PDF files are allowed.";
    hint.classList.add("field-error");
    input.value = "";
    return false;
  }

  if (file.size > MAX_FILE_SIZE) {
    hint.textContent = "File is too large. Please keep it under 5 MB.";
    hint.classList.add("field-error");
    input.value = "";
    return false;
  }

  hint.textContent = `${file.name} selected successfully.`;
  hint.classList.remove("field-error");
  return true;
}

function validateUploads() {
  const form16Ok = validatePdfInput("form16File");
  const portfolioOk = validatePdfInput("portfolioStatement");
  return form16Ok && portfolioOk;
}

function renderLineChart(targetId, data) {
  const target = document.getElementById(targetId);
  if (!target || !data.length) return;

  const maxValue = Math.max(...data.map((item) => item.value), 1);
  const width = 460;
  const height = 180;
  const stepX = width / Math.max(data.length - 1, 1);

  const points = data
    .map((item, index) => {
      const x = index * stepX;
      const y = height - (item.value / maxValue) * 140 - 16;
      return `${x},${y}`;
    })
    .join(" ");

  const labels = data
    .map(
      (item, index) =>
        `<span class="chart-label" style="left:${(index / Math.max(data.length - 1, 1)) * 100}%">${item.label}</span>`
    )
    .join("");

  target.innerHTML = `
    <svg viewBox="0 0 ${width} ${height}" preserveAspectRatio="none" class="chart-svg">
      <polyline points="${points}" fill="none" stroke="#246bff" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"></polyline>
      ${data
        .map((item, index) => {
          const x = index * stepX;
          const y = height - (item.value / maxValue) * 140 - 16;
          return `<circle cx="${x}" cy="${y}" r="5" fill="#1749b7"></circle>`;
        })
        .join("")}
    </svg>
    <div class="chart-label-row">${labels}</div>
  `;
}

function renderAllocationChart(targetId, allocations) {
  const target = document.getElementById(targetId);
  if (!target) return;

  target.innerHTML = allocations
    .map(
      (item) => `
        <div class="allocation-row">
          <div class="allocation-meta">
            <span>${item.label}</span>
            <strong>${item.value}%</strong>
          </div>
          <div class="allocation-track">
            <div class="allocation-fill" style="width:${item.value}%; background:${item.color};"></div>
          </div>
        </div>
      `
    )
    .join("");
}

function renderBarChart(targetId, bars) {
  const target = document.getElementById(targetId);
  if (!target) return;

  target.innerHTML = bars
    .map(
      (item) => `
        <div class="bar-card">
          <div class="bar-track">
            <div class="bar-fill" style="height:${item.value}%;"></div>
          </div>
          <strong>${item.value}</strong>
          <span>${item.label}</span>
        </div>
      `
    )
    .join("");
}

function renderSavedPlans(plans) {
  const list = document.getElementById("saved-plans-list");
  list.innerHTML = "";

  if (!plans || !plans.length) {
    const li = document.createElement("li");
    li.textContent = "No saved plans yet. Generate one to start your history.";
    list.appendChild(li);
    return;
  }

  plans.forEach((plan) => {
    const li = document.createElement("li");
    li.textContent = `${plan.created_at} - ${plan.title} (${formatCurrency(plan.monthly_sip)} SIP)`;
    list.appendChild(li);
  });
}

function renderResults(response) {
  const {
    overview,
    fire,
    health,
    life_event: lifeEvent,
    tax,
    couple,
    portfolio,
    saved_plans: savedPlans,
    plan_id: planId,
    report_available: reportAvailable,
  } = response;
  currentPlanId = planId || null;

  document.getElementById("summary-title").textContent = overview.title;
  document.getElementById("summary-text").textContent = overview.summary;

  document.getElementById("metric-score").textContent = `${health.score}/100`;
  document.getElementById("metric-sip").textContent = formatCurrency(fire.monthly_sip);
  document.getElementById("metric-emergency").textContent = formatCurrency(fire.emergency_target);
  document.getElementById("metric-tax-saved").textContent = formatCurrency(tax.estimated_tax_saved);

  renderList("priority-actions", overview.priority_actions);
  renderList("roadmap-list", fire.monthly_roadmap);
  renderList("health-actions", health.focus_actions);
  renderList("event-actions", lifeEvent.actions);
  renderList("tax-actions", tax.actions);
  renderList("couple-actions", couple.actions);
  renderList("portfolio-actions", portfolio.actions);

  document.getElementById("fire-title").textContent = fire.headline || "FIRE roadmap";
  document.getElementById("health-title").textContent = health.headline;
  document.getElementById("event-title").textContent = lifeEvent.title;
  document.getElementById("tax-title").textContent = tax.title;
  document.getElementById("couple-title").textContent = couple.title;
  document.getElementById("portfolio-title").textContent = portfolio.title;

  document.getElementById("fire-agent-text").textContent = fire.summary;
  document.getElementById("health-agent-text").textContent = health.summary;
  document.getElementById("event-agent-text").textContent = lifeEvent.summary;
  document.getElementById("tax-agent-text").textContent = tax.summary;
  document.getElementById("couple-agent-text").textContent = couple.summary;
  document.getElementById("portfolio-agent-text").textContent = portfolio.summary;
  document.getElementById("tax-old-regime").textContent = `Old: ${formatCurrency(tax.old_regime_tax)}`;
  document.getElementById("tax-new-regime").textContent = `New: ${formatCurrency(tax.new_regime_tax)}`;

  renderLineChart("fire-chart", fire.projection_points || []);
  renderAllocationChart("allocation-chart", [
    { label: "Equity", value: fire.allocation_mix?.equity || 0, color: "#246bff" },
    { label: "Debt", value: fire.allocation_mix?.debt || 0, color: "#7fd6ff" },
    { label: "Gold / Intl", value: fire.allocation_mix?.alt || 0, color: "#1749b7" },
  ]);
  renderBarChart(
    "health-chart",
    Object.entries(health.metrics.component_scores || {}).map(([label, value]) => ({
      label,
      value,
    }))
  );
  renderSavedPlans(savedPlans);
  if (reportAvailable && currentPlanId) {
    downloadReportButton.classList.remove("hidden");
  } else {
    downloadReportButton.classList.add("hidden");
  }

  resultsEmpty.classList.add("hidden");
  resultsContent.classList.remove("hidden");
  setActiveOutputNav(0);
}

function setupOutputObserver() {
  if (!outputSections.length) return;
  setActiveOutputNav(0);
}

function showOutputSection(index) {
  const safeIndex = Math.max(0, Math.min(index, outputSections.length - 1));
  const target = outputSections[safeIndex];
  if (!target) return;

  setActiveOutputNav(safeIndex);
  requestAnimationFrame(() => {
    target.scrollIntoView({ behavior: "smooth", block: "start" });
  });
}

async function loadSavedPlans() {
  try {
    const response = await fetch(`${apiBase}/api/plans`);
    const result = await response.json();
    if (response.ok) {
      renderSavedPlans(result.plans || []);
    }
  } catch {
    // Keep silent for local-first UX.
  }
}

async function submitPlan(event) {
  event.preventDefault();

  if (!validateUploads()) {
    statusText.textContent = "Please fix the file upload issues before generating the plan.";
    return;
  }

  button.disabled = true;
  statusText.textContent = "Generating your complete financial plan...";

  try {
    const formData = new FormData(form);
    const response = await fetch(`${apiBase}/api/generate-plan`, {
      method: "POST",
      body: formData,
    });

    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.error || "Failed to generate the plan.");
    }

    renderResults(result);
    statusText.textContent = result.plan_id
      ? `Your plan is ready and saved as #${result.plan_id}.`
      : "Your plan is ready.";
    document.getElementById("output-summary").scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (error) {
    statusText.textContent = error.message;
  } finally {
    button.disabled = false;
  }
}

function downloadCurrentReport() {
  if (!currentPlanId) {
    statusText.textContent = "Generate a plan first before downloading the report.";
    return;
  }

  window.open(`${apiBase}/api/plans/${currentPlanId}/report`, "_blank");
}

prevStepButton.addEventListener("click", () => showStep(currentStep - 1));
nextStepButton.addEventListener("click", () => showStep(currentStep + 1));
prevOutputButton?.addEventListener("click", () => showOutputSection(currentOutputIndex - 1));
nextOutputButton?.addEventListener("click", () => showOutputSection(currentOutputIndex + 1));
downloadReportButton?.addEventListener("click", downloadCurrentReport);
form.addEventListener("submit", submitPlan);

inputNavLinks.forEach((link) => {
  link.addEventListener("click", (event) => {
    event.preventDefault();
    showStep(Number(link.dataset.stepTarget || 0));
    wizardSteps[currentStep].scrollIntoView({ behavior: "smooth", block: "nearest" });
  });
});

outputNavLinks.forEach((link) => {
  link.addEventListener("click", (event) => {
    event.preventDefault();
    const sectionIndex = outputSections.findIndex((section) => `#${section.id}` === link.getAttribute("href"));
    if (sectionIndex >= 0) {
      showOutputSection(sectionIndex);
    }
  });
});

["form16File", "portfolioStatement"].forEach((inputName) => {
  form.querySelector(`input[name="${inputName}"]`)?.addEventListener("change", () => validatePdfInput(inputName));
});

showStep(0);
setActiveOutputNav(0);
setupOutputObserver();
loadSavedPlans();

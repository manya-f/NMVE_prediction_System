// ============================================================================
// Sample Data for Quick Testing
// ============================================================================

const SAMPLES = {
  healthy: {
    temperature: 38.4,
    power_on_hours: 12500,
    life_used: 22,
    unsafe_shutdowns: 0,
    media_errors: 0,
  },
  wearout: {
    temperature: 42.7,
    power_on_hours: 71000,
    life_used: 93,
    unsafe_shutdowns: 1,
    media_errors: 1,
  },
  thermal: {
    temperature: 81.2,
    power_on_hours: 820,
    life_used: 47,
    unsafe_shutdowns: 0,
    media_errors: 3,
  },
  power: {
    temperature: 35.0,
    power_on_hours: 15800,
    life_used: 40,
    unsafe_shutdowns: 14,
    media_errors: 2,
  },
};

// ============================================================================
// DOM Elements
// ============================================================================

const form = document.getElementById("predictForm");
const resultContainer = document.getElementById("resultContainer");
const loadingSpinner = document.getElementById("loadingSpinner");
const sampleButtons = document.querySelectorAll(".sample-btn");

// ============================================================================
// Event Listeners
// ============================================================================

form.addEventListener("submit", handleFormSubmit);
sampleButtons.forEach((btn) => {
  btn.addEventListener("click", handleSampleClick);
});

// ============================================================================
// Form Submission Handler
// ============================================================================

async function handleFormSubmit(event) {
  event.preventDefault();

  // Gather form data
  const formData = new FormData(form);
  const payload = {};
  for (const [key, value] of formData.entries()) {
    payload[key] = isNaN(value) ? value : Number(value);
  }

  // Show loading state
  showLoading();

  try {
    const response = await fetch("/api/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await response.json();

    if (!response.ok || !data.success) {
      showError(data.error || "Prediction failed. Please try again.");
      return;
    }

    displayResults(data);
  } catch (error) {
    showError(`Network error: ${error.message}`);
  }
}

// ============================================================================
// Sample Data Handler
// ============================================================================

function handleSampleClick(event) {
  const sampleType = event.target.dataset.sample;
  const sampleData = SAMPLES[sampleType];

  if (!sampleData) return;

  // Populate form fields
  document.getElementById("temperature").value = sampleData.temperature;
  document.getElementById("power_on_hours").value = sampleData.power_on_hours;
  document.getElementById("life_used").value = sampleData.life_used;
  document.getElementById("unsafe_shutdowns").value = sampleData.unsafe_shutdowns;
  document.getElementById("media_errors").value = sampleData.media_errors;

  // Auto-submit
  form.dispatchEvent(new Event("submit"));
}

// ============================================================================
// UI Renderers
// ============================================================================

function showLoading() {
  loadingSpinner.style.display = "flex";
  resultContainer.style.display = "none";
}

function showError(message) {
  loadingSpinner.style.display = "none";
  resultContainer.style.display = "flex";
  resultContainer.innerHTML = `
    <div class="error-message">
      <strong>Error</strong>
      ${escapeHtml(message)}
    </div>
  `;
}

function displayResults(data) {
  loadingSpinner.style.display = "none";
  resultContainer.style.display = "block";
  resultContainer.innerHTML = buildResultsHTML(data);

  // Animate progress bars
  animateProgressBars();
}

function buildResultsHTML(data) {
  const healthClass = data.health === "Healthy" ? "healthy" : "failing";
  const healthIcon = data.health === "Healthy" ? "✓" : "⚠";

  const failureModes = data.failure_modes
    .map(
      (mode) => `
    <div class="failure-mode-item">
      <div class="mode-header">
        <span class="name">${escapeHtml(mode.name)}</span>
        <span class="percentage">${mode.percentage.toFixed(1)}%</span>
      </div>
      <div class="progress-bar">
        <div class="progress-fill" style="width: 0%" data-width="${mode.percentage}%"></div>
      </div>
    </div>
  `
    )
    .join("");

  return `
    <div>
      <div class="health-badge ${healthClass}">
        <span>${healthIcon}</span>
        <span>${data.health}</span>
      </div>

      <div class="predicted-mode">
        <h3>Predicted Failure Mode</h3>
        <div class="mode-name">${escapeHtml(data.mode_name)}</div>
        <div class="mode-description">${escapeHtml(data.mode_description)}</div>
      </div>

      <div class="failure-modes-section">
        <h3>All Failure Modes</h3>
        ${failureModes}
      </div>

      <div style="margin-top: 24px; padding-top: 24px; border-top: 1px solid rgba(148, 163, 184, 0.15);">
        <p style="font-size: 0.85rem; color: #94a3b8;">
          Confidence: <strong>${(data.confidence * 100).toFixed(1)}%</strong>
        </p>
      </div>
    </div>
  `;
}

function animateProgressBars() {
  const bars = document.querySelectorAll(".progress-fill");
  bars.forEach((bar) => {
    const targetWidth = bar.dataset.width;
    setTimeout(() => {
      bar.style.width = targetWidth;
    }, 50);
  });
}

// ============================================================================
// Utility Functions
// ============================================================================

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

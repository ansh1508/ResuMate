

'use strict';

document.addEventListener("DOMContentLoaded", () => {

/* ── STATE ── */
const S = {
file: null,
jd: '',
results: null,
};

/* ── SCREEN SWITCH ── */
function show(id) {
document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
const el = document.getElementById(id);
if (el) el.classList.add('active');
}

/* ── NAVIGATION ── */
const btnStart = document.getElementById('btn-start');

if (btnStart) {
  btnStart.onclick = () => {
    const user = localStorage.getItem('ara_user');

    if (!user) {
      alert("⚠️ Please sign in with Google first");
      return;
    }

    show('s-main');
  };
}

const btnBackMain = document.getElementById('btn-back-main');
if (btnBackMain) btnBackMain.onclick = () => show('s-welcome');

const btnBackRes = document.getElementById('btn-back-res');
if (btnBackRes) btnBackRes.onclick = () => show('s-main');

/* ── INPUTS ── */
const fileInput = document.getElementById('file-input');
const jdInput = document.getElementById('jd-area');
const analyzeBtn = document.getElementById('analyze-btn');

/* ── READY CHECK ── */
function checkReady() {
if (!analyzeBtn) return;
analyzeBtn.disabled = !(S.file && S.jd.length > 5);
}

/* ── FILE INPUT ── */
if (fileInput) {
fileInput.onchange = () => {
const file = fileInput.files[0];
if (!file) return;


const ext = file.name.split('.').pop().toLowerCase();
if (!['pdf', 'docx'].includes(ext)) {
  alert("Only PDF or DOCX allowed");
  return;
}

S.file = file;
checkReady();


};
}

/* ── JD INPUT ── */
if (jdInput) {
jdInput.oninput = () => {
S.jd = jdInput.value.trim();
checkReady();
};
}

/* ── ANALYZE ── */
if (analyzeBtn) {
analyzeBtn.onclick = async () => {

const user = localStorage.getItem('ara_user');

if (!user) {
  alert("⚠️ Please login first");
  return;
}

if (!S.file || !S.jd) {
  alert("Upload resume and job description");
  return;
}

show('s-loading');

try {
  const formData = new FormData();
  formData.append('resume', S.file);
  formData.append('job_description', S.jd);

  const res = await fetch('/api/analyze', {
    method: 'POST',
    body: formData
  });

  if (!res.ok) throw new Error("Server error: " + res.status);

  const data = await res.json();
  S.results = data;

  renderResults(data);
  show('s-results');

} catch (err) {
  console.error(err);
  alert("Error: " + err.message);
  show('s-main');
}


};
}

/* ── RENDER RESULTS ── */
function renderResults(r) {
const container = document.getElementById('res-layout');
if (!container) return;

const score = r.ats_score || 0;
const color = score > 75 ? "#22c55e" : score > 50 ? "#f59e0b" : "#ef4444";

const html = ` <div class="res-container">


  <!-- SCORE CARD -->
  <div class="res-card score-card">
    <h2>ATS Score</h2>
    <div class="chart-container">
  <canvas id="scoreChart"></canvas>
  <div class="chart-text">${score}</div>
</div>
    <p class="verdict">${r.verdict || ""}</p>
  </div>

  <!-- DETAILS -->
  <div class="res-card">

    <h3>Summary</h3>
    <p>${r.verdict_description || ""}</p>

    <h3>Missing Keywords</h3>
    <div class="chips">
      ${(r.missing_keywords || []).map(k => `<span class="chip">${k}</span>`).join("")}
    </div>

    <h3>Strengths</h3>
    <ul>
      ${(r.strengths || []).map(s => `<li>${s}</li>`).join("")}
    </ul>

    <h3>Suggestions</h3>
    <ul>
      ${(r.suggestions || []).map(s => `<li>${s.text}</li>`).join("")}
    </ul>

    <div style="text-align:center; margin-top:20px;">
      <button id="download-btn">Download Report</button>
    </div>

  </div>

</div>


`;

container.innerHTML = html;

// Download button
const btn = document.getElementById("download-btn");
if (btn) btn.onclick = downloadReport;

// Chart
const ctx = document.getElementById("scoreChart");

new Chart(ctx, {
type: 'doughnut',
data: {
labels: ['Match', 'Gap'],
datasets: [{
data: [score, 100 - score],
backgroundColor: [color, "#1e293b"]
}]
},
options: {
cutout: '70%',
plugins: {
legend: { display: false }
}
}
});
}

/* ── DOWNLOAD PDF ── */
function downloadReport() {
if (!S.results) return alert("No data");

const { jsPDF } = window.jspdf;
const doc = new jsPDF();

doc.setFontSize(16);
doc.text("AI Resume Analysis Report", 10, 10);

doc.setFontSize(12);
doc.text("ATS Score: " + S.results.ats_score, 10, 20);
doc.text("Verdict: " + S.results.verdict, 10, 30);

let y = 40;

doc.text("Strengths:", 10, y);
y += 10;

(S.results.strengths || []).forEach(s => {
doc.text("- " + s, 10, y);
y += 8;
});

y += 5;
doc.text("Suggestions:", 10, y);
y += 10;

(S.results.suggestions || []).forEach(s => {
doc.text("- " + s.text, 10, y);
y += 8;
});

doc.save("resume-report.pdf");
}

/* ── INIT ── */
checkReady();

console.log("✅ FINAL CLEAN APP RUNNING");

});

/* ══════════════════════════════
   GOOGLE LOGIN — Global scope
══════════════════════════════ */

// Restore user session from localStorage if exists
(function restoreSession() {
  document.addEventListener("DOMContentLoaded", () => {
  try {
    const saved = localStorage.getItem('ara_user');
    if (saved) {
      const user = JSON.parse(saved);
      applyUser(user);
    }
  } catch (e) {
    console.error("Restore error", e);
  }
});
})();

function handleGoogleLogin() {
  // Try to redirect to the backend OAuth endpoint
  // If backend isn't running, show a friendly toast and open demo mode
  const backendUrl = window.location.origin;

  // Ping health check first
  fetch(backendUrl + '/health', { signal: AbortSignal.timeout(2000) })
    .then(r => {
      if (r.ok) {
        // Backend is live — redirect to Google OAuth
        window.location.href = backendUrl + '/login';
      } else {
        showLoginUnavailable();
      }
    })
    .catch(() => {
      // Backend not reachable — show instructions
      showLoginUnavailable();
    });
}

function showLoginUnavailable() {
  showToast('Backend not running. Start the FastAPI server to enable Google login.', 'info', 4000);
}

function applyUser(user) {
  // Welcome screen pill
  const pill = document.getElementById('user-pill');
  const btn  = document.getElementById('btn-login-welcome');
  if (pill && btn) {
    document.getElementById('user-avatar').src  = user.picture || '';
    document.getElementById('user-name').textContent = user.name || user.email || '';
    btn.style.display  = 'none';
    pill.style.display = 'inline-flex';
  }
  // Main screen pill
  const pillM = document.getElementById('user-pill-main');
  const btnM  = document.getElementById('btn-login-main');
  if (pillM && btnM) {
    document.getElementById('user-avatar-main').src = user.picture || '';
    document.getElementById('user-name-main').textContent = user.name || user.email || '';
    btnM.style.display  = 'none';
    pillM.style.display = 'inline-flex';
  }
}

function handleSignOut() {
  localStorage.removeItem('ara_user');
  // Show login buttons again
  const pill  = document.getElementById('user-pill');
  const btn   = document.getElementById('btn-login-welcome');
  const pillM = document.getElementById('user-pill-main');
  const btnM  = document.getElementById('btn-login-main');
  if (pill)  pill.style.display  = 'none';
  if (btn)   btn.style.display   = 'inline-flex';
  if (pillM) pillM.style.display = 'none';
  if (btnM)  btnM.style.display  = 'inline-flex';
  showToast('Signed out successfully', 'success');
}

// Handle OAuth callback: if URL has ?user=... query param, parse and store it
(function checkOAuthReturn() {
  const params = new URLSearchParams(window.location.search);
  const userParam = params.get('user');

  if (userParam) {
    try {
      const user = JSON.parse(decodeURIComponent(userParam));

      localStorage.setItem('ara_user', JSON.stringify(user));

      // Apply AFTER slight delay (ensures DOM exists)
      setTimeout(() => {
        applyUser(user);
      }, 100);

      window.history.replaceState({}, '', window.location.pathname);

    } catch (e) {
      console.error("OAuth parse error", e);
    }
  }
})();

// Helper to show toasts (works even outside DOMContentLoaded)
function showToast(msg, type = 'info', duration = 2800) {
  const el = document.getElementById('toast');
  if (!el) return;
  el.textContent = msg;
  el.className = 'toast show ' + type;
  setTimeout(() => el.classList.remove('show'), duration);
}





"use strict";

// ---------- tabs ----------
document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
        document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
        document.querySelectorAll(".tab-content").forEach((c) => c.classList.remove("active"));
        btn.classList.add("active");
        document.getElementById("tab-" + btn.dataset.tab).classList.add("active");
    });
});

// ---------- helpers ----------
const $ = (id) => document.getElementById(id);

function setLoading(btn, loading) {
    btn.classList.toggle("loading", loading);
    btn.disabled = loading;
}

async function apiFetch(url, options) {
    const resp = await fetch(url, options);
    if (!resp.ok) {
        let detail = resp.statusText;
        try {
            const data = await resp.json();
            detail = data.detail || detail;
        } catch (_) { /* not json */ }
        throw new Error(detail);
    }
    return resp.json();
}

// ---------- sample review ----------
const btnSample = $("btn-sample");
const btnCopy = $("btn-copy");
const btnToPredict = $("btn-to-predict");
const sampleText = $("sample-text");
const sampleMeta = $("sample-meta");

btnSample.addEventListener("click", async () => {
    setLoading(btnSample, true);
    try {
        const data = await apiFetch("/api/sample");
        sampleText.textContent = data.text;
        sampleText.classList.remove("empty");
        sampleMeta.innerHTML =
            '<span class="tag">label: ' + escapeHtml(data.label) + "</span>" +
            '<span class="tag">src: ' + escapeHtml(data.src) + "</span>";
        sampleMeta.classList.remove("hidden");
        btnCopy.disabled = false;
        btnToPredict.disabled = false;
    } catch (err) {
        sampleText.textContent = "// error: " + err.message;
        sampleText.classList.add("empty");
    } finally {
        setLoading(btnSample, false);
    }
});

btnCopy.addEventListener("click", async () => {
    try {
        await navigator.clipboard.writeText(sampleText.textContent);
        btnCopy.textContent = "Скопировано ✓";
        setTimeout(() => { btnCopy.textContent = "Копировать"; }, 1500);
    } catch (_) {
        // fallback for non-secure contexts
        const range = document.createRange();
        range.selectNodeContents(sampleText);
        const sel = window.getSelection();
        sel.removeAllRanges();
        sel.addRange(range);
        document.execCommand("copy");
        sel.removeAllRanges();
    }
});

btnToPredict.addEventListener("click", () => {
    $("predict-input").value = sampleText.textContent;
    $("predict-input").focus();
});

// ---------- predict ----------
const btnPredict = $("btn-predict");
const btnClear = $("btn-clear");
const predictInput = $("predict-input");
const predictResult = $("predict-result");
const predictError = $("predict-error");

btnPredict.addEventListener("click", async () => {
    const text = predictInput.value.trim();
    if (!text) return;

    setLoading(btnPredict, true);
    predictError.classList.add("hidden");
    try {
        const data = await apiFetch("/api/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text }),
        });
        renderResult(data);
    } catch (err) {
        predictError.textContent = "> error: " + err.message;
        predictError.classList.remove("hidden");
        predictResult.classList.add("hidden");
    } finally {
        setLoading(btnPredict, false);
    }
});

btnClear.addEventListener("click", () => {
    predictInput.value = "";
    predictResult.classList.add("hidden");
    predictError.classList.add("hidden");
});

function renderResult(data) {
    const labelEl = $("predict-label");
    labelEl.textContent = data.label;
    labelEl.className = "verdict-label " + data.label;
    $("predict-score").textContent = "(" + (data.score * 100).toFixed(1) + "%)";

    const bars = $("predict-bars");
    bars.innerHTML = "";
    // sort by score desc for nicer display
    const entries = Object.entries(data.scores).sort((a, b) => b[1] - a[1]);
    for (const [name, value] of entries) {
        const row = document.createElement("div");
        row.className = "bar-row";

        const nameEl = document.createElement("span");
        nameEl.textContent = name;

        const track = document.createElement("div");
        track.className = "bar-track";
        const fill = document.createElement("div");
        fill.className = "bar-fill " + name;
        track.appendChild(fill);

        const valueEl = document.createElement("span");
        valueEl.className = "bar-value";
        valueEl.textContent = (value * 100).toFixed(1) + "%";

        row.appendChild(nameEl);
        row.appendChild(track);
        row.appendChild(valueEl);
        bars.appendChild(row);

        // trigger transition
        requestAnimationFrame(() => { fill.style.width = (value * 100) + "%"; });
    }
    predictResult.classList.remove("hidden");
}

function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
}

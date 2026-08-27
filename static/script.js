const form = document.getElementById("identify-form");
const urlInput = document.getElementById("url-input");
const submitBtn = document.getElementById("submit-btn");
const loading = document.getElementById("loading");
const resultEl = document.getElementById("result");
const errorEl = document.getElementById("error");

function show(el) {
  el.classList.remove("hidden");
}

function hide(el) {
  el.classList.add("hidden");
}

function setLoading(isLoading) {
  if (isLoading) {
    submitBtn.disabled = true;
    hide(resultEl);
    hide(errorEl);
    show(loading);
    document.body.classList.add("processing");
  } else {
    submitBtn.disabled = false;
    hide(loading);
    document.body.classList.remove("processing");
  }
}

function showResult(song) {
  resultEl.innerHTML =
    '<h2>Lagu ditemukan</h2>' +
    '<p class="song-title"></p>' +
    '<p class="song-artist"></p>' +
    '<p class="song-score"></p>';
  resultEl.querySelector(".song-title").textContent = song.title;
  resultEl.querySelector(".song-artist").textContent = song.artist;
  resultEl.querySelector(".song-score").textContent =
    "Skor kecocokan: " + Math.round(song.score * 100) + "%";
  show(resultEl);
}

function showError(message) {
  errorEl.textContent = message;
  show(errorEl);
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const url = urlInput.value.trim();
  if (!url) {
    return;
  }

  setLoading(true);
  try {
    const response = await fetch("/api/identify", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    });
    const data = await response.json();

    if (response.ok && data.status === "success") {
      showResult(data.song);
    } else {
      showError(data.message || "Terjadi kesalahan. Silakan coba lagi.");
    }
  } catch (err) {
    showError("Tidak dapat terhubung ke server. Silakan coba lagi.");
  } finally {
    setLoading(false);
  }
});
document.getElementById("findBtn").addEventListener("click", function () {
  const errorText = document.getElementById("errorInput").value.trim();

  if (!errorText) {
    alert("Paste an error first!");
    return;
  }

  const query = encodeURIComponent(
    errorText + " fix site:stackoverflow.com OR site:github.com OR site:reddit.com"
  );

  const url = `https://www.google.com/search?q=${query}`;
  window.open(url, "_blank");
});

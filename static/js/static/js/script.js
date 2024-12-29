const toggleMenuButton = document.querySelector(".toggle-btn");

toggleMenuButton.addEventListener("click", () => {
  const sidebar = document.getElementById("sidebar");
  const isExpanded = sidebar.classList.contains("expand");

  sidebar.classList.toggle("expand");
  toggleMenuButton.innerHTML = isExpanded ? "☰" : "✖";
});

const yearDropdown = document.getElementById("id_ano_letivo");

yearDropdown.addEventListener("change", () => {
  const form = document.getElementById("id_boletim_form");

  const confirmChange = confirm(
    "Você tem certeza de que deseja alterar o ano letivo?"
  );
  if (confirmChange) {
    form.submit();
  }
});

document.addEventListener("keydown", (event) => {
  if (event.key.toLowerCase() === "m") {
    document.getElementById("sidebar").classList.toggle("expand");
  }
});

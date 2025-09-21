// Dummy login (you can replace with real backend later)
function loginUser(event) {
  event.preventDefault();
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  if (username === "player" && password === "1234") {
    localStorage.setItem("loggedIn", "true");
    window.location.href = "index.html";
  } else {
    document.getElementById("error-msg").innerText = "Invalid login! Try player / 1234";
  }
}

// Check if logged in before showing game
if (window.location.pathname.includes("index.html")) {
  if (localStorage.getItem("loggedIn") !== "true") {
    window.location.href = "login.html";
  }
}

// Logout function
function logout() {
  localStorage.removeItem("loggedIn");
  window.location.href = "login.html";
}

// Simple Game Code (Move a square with arrow keys)
const canvas = document.getElementById("gameCanvas");
if (canvas) {
  const ctx = canvas.getContext("2d");
  let x = 50, y = 50, size = 30;

  function drawPlayer() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "lime";
    ctx.fillRect(x, y, size, size);
  }

  function movePlayer(e) {
    if (e.key === "ArrowUp") y -= 10;
    if (e.key === "ArrowDown") y += 10;
    if (e.key === "ArrowLeft") x -= 10;
    if (e.key === "ArrowRight") x += 10;
    drawPlayer();
  }

  document.addEventListener("keydown", movePlayer);
  drawPlayer();
}

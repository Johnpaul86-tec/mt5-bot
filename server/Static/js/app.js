function startBot() {
    document.getElementById("status").innerText = "Running";
    alert("Bot Started (agent must be running)");
}

function stopBot() {
    document.getElementById("status").innerText = "Stopped";
    alert("Bot Stopped");
}
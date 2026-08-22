document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("ticket-form");
  const alertBox = document.getElementById("form-alert");
  const successCard = document.getElementById("success-card");
  const submitBtn = document.getElementById("submit-btn");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    alertBox.classList.add("hidden");

    const payload = {
      requester_name: document.getElementById("requester_name").value.trim(),
      requester_email: document.getElementById("requester_email").value.trim(),
      title: document.getElementById("title").value.trim(),
      category: document.getElementById("category").value,
      priority: document.getElementById("priority").value,
      description: document.getElementById("description").value.trim(),
    };

    submitBtn.disabled = true;
    submitBtn.textContent = "Submitting...";

    try {
      const res = await fetch("/api/tickets", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();

      if (!res.ok) {
        const errors = data.errors || {};
        const msg = Object.values(errors).join(" ") || "Something went wrong. Please check your inputs.";
        alertBox.textContent = msg;
        alertBox.className = "alert alert-error";
        submitBtn.disabled = false;
        submitBtn.textContent = "Submit Ticket";
        return;
      }

      form.classList.add("hidden");
      document.getElementById("ticket-id").textContent = "#" + data.id;
      document.getElementById("ticket-link").href = "/ticket/" + data.id;
      successCard.classList.remove("hidden");
    } catch (err) {
      alertBox.textContent = "Network error. Please try again.";
      alertBox.className = "alert alert-error";
      submitBtn.disabled = false;
      submitBtn.textContent = "Submit Ticket";
    }
  });
});
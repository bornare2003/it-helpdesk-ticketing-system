const state = {
  page: 1,
  perPage: 10,
  filters: { search: "", category: "All", priority: "All", status: "All", sort: "created_desc" },
};

const tbody = document.getElementById("tickets-tbody");
const pagination = document.getElementById("pagination");
const modal = document.getElementById("ticket-modal");
const modalBody = document.getElementById("modal-body");

function debounce(fn, delay) {
  let t;
  return (...args) => {
    clearTimeout(t);
    t = setTimeout(() => fn(...args), delay);
  };
}

function statusClass(status) {
  return "status-" + status.replace(" ", "-").toLowerCase();
}
function priorityClass(priority) {
  return "priority-" + priority.toLowerCase();
}

async function loadStats() {
  const res = await fetch("/api/stats");
  const data = await res.json();
  document.getElementById("stat-total").textContent = data.total;
  document.getElementById("stat-open").textContent = data.by_status["Open"] || 0;
  document.getElementById("stat-progress").textContent = data.by_status["In Progress"] || 0;
  document.getElementById("stat-resolved").textContent = data.by_status["Resolved"] || 0;
}

function buildQuery() {
  const params = new URLSearchParams();
  params.set("page", state.page);
  params.set("per_page", state.perPage);
  params.set("sort", state.filters.sort);
  if (state.filters.search) params.set("search", state.filters.search);
  if (state.filters.category !== "All") params.set("category", state.filters.category);
  if (state.filters.priority !== "All") params.set("priority", state.filters.priority);
  if (state.filters.status !== "All") params.set("status", state.filters.status);
  return params.toString();
}

async function loadTickets() {
  tbody.innerHTML = `<tr><td colspan="8" class="loading-row">Loading tickets...</td></tr>`;
  const res = await fetch(`/api/tickets?${buildQuery()}`);
  const data = await res.json();
  renderTable(data.tickets);
  renderPagination(data.page, data.pages);
}

function renderTable(tickets) {
  if (!tickets.length) {
    tbody.innerHTML = `<tr><td colspan="8" class="empty-row">No tickets found.</td></tr>`;
    return;
  }
  tbody.innerHTML = tickets.map((t) => `
    <tr data-id="${t.id}">
      <td>#${t.id}</td>
      <td class="row-title" data-action="view">${escapeHtml(t.title)}</td>
      <td>${escapeHtml(t.requester_name)}</td>
      <td><span class="badge category-badge">${t.category}</span></td>
      <td><span class="badge ${priorityClass(t.priority)}">${t.priority}</span></td>
      <td>
        <select class="status-select" data-action="status">
          ${STATUSES.map((s) => `<option value="${s}" ${s === t.status ? "selected" : ""}>${s}</option>`).join("")}
        </select>
      </td>
      <td>${new Date(t.created_at).toLocaleDateString()}</td>
      <td><button class="btn btn-danger btn-sm" data-action="delete">Delete</button></td>
    </tr>
  `).join("");

  tbody.querySelectorAll('[data-action="view"]').forEach((el) => {
    el.addEventListener("click", () => openModal(el.closest("tr").dataset.id));
  });
  tbody.querySelectorAll('[data-action="status"]').forEach((el) => {
    el.addEventListener("change", (e) => updateStatus(el.closest("tr").dataset.id, e.target.value));
  });
  tbody.querySelectorAll('[data-action="delete"]').forEach((el) => {
    el.addEventListener("click", () => deleteTicket(el.closest("tr").dataset.id));
  });
}

function renderPagination(page, pages) {
  if (pages <= 1) {
    pagination.innerHTML = "";
    return;
  }
  let html = "";
  html += `<button ${page <= 1 ? "disabled" : ""} data-page="${page - 1}">Prev</button>`;
  for (let i = 1; i <= pages; i++) {
    html += `<button class="${i === page ? "active" : ""}" data-page="${i}">${i}</button>`;
  }
  html += `<button ${page >= pages ? "disabled" : ""} data-page="${page + 1}">Next</button>`;
  pagination.innerHTML = html;
  pagination.querySelectorAll("button[data-page]").forEach((btn) => {
    btn.addEventListener("click", () => {
      state.page = parseInt(btn.dataset.page, 10);
      loadTickets();
    });
  });
}

async function updateStatus(id, status) {
  await fetch(`/api/tickets/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status }),
  });
  loadStats();
}

async function deleteTicket(id) {
  if (!confirm(`Delete ticket #${id}? This cannot be undone.`)) return;
  await fetch(`/api/tickets/${id}`, { method: "DELETE" });
  loadTickets();
  loadStats();
}

async function openModal(id) {
  const res = await fetch(`/api/tickets/${id}`);
  const t = await res.json();
  modalBody.innerHTML = `
    <h2>#${t.id} — ${escapeHtml(t.title)}</h2>
    <p class="ticket-meta">
      <span class="badge category-badge">${t.category}</span>
      <span class="badge ${priorityClass(t.priority)}">${t.priority}</span>
      <span class="badge ${statusClass(t.status)}">${t.status}</span>
    </p>
    <p class="ticket-desc">${escapeHtml(t.description)}</p>
    <hr>
    <p><strong>Requester:</strong> ${escapeHtml(t.requester_name)} (${escapeHtml(t.requester_email)})</p>
    <p><strong>Created:</strong> ${new Date(t.created_at).toLocaleString()}</p>
    <p><strong>Updated:</strong> ${new Date(t.updated_at).toLocaleString()}</p>
  `;
  modal.classList.remove("hidden");
}

document.getElementById("modal-close").addEventListener("click", () => modal.classList.add("hidden"));
modal.addEventListener("click", (e) => { if (e.target === modal) modal.classList.add("hidden"); });

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}

document.getElementById("filter-search").addEventListener("input", debounce((e) => {
  state.filters.search = e.target.value.trim();
  state.page = 1;
  loadTickets();
}, 350));

["category", "priority", "status", "sort"].forEach((key) => {
  document.getElementById(`filter-${key}`).addEventListener("change", (e) => {
    state.filters[key] = e.target.value;
    state.page = 1;
    loadTickets();
  });
});

loadStats();
loadTickets();
setInterval(loadStats, 30000);

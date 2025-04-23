// ───────────────────────────────────────────────
// CSRF SETUP FOR HTMX REQUESTS
// ───────────────────────────────────────────────
document.body.addEventListener('htmx:configRequest', (event) => {
    const token = document.querySelector('meta[name="csrf-token"]').content;
    if (token) {
      event.detail.headers['X-CSRFToken'] = token;
    }
  });
  
  // ───────────────────────────────────────────────
  // GLOBAL STATE
  // ───────────────────────────────────────────────
  const teamId = document.body.dataset.teamId;
  const recentlyUpdatedTasks = new Set();
  
  // ───────────────────────────────────────────────
  // ANIMATION HELPERS
  // ───────────────────────────────────────────────
  function animateFadeIn(el) {
    el.classList.add("opacity-0", "translate-y-2");
    requestAnimationFrame(() => {
      el.classList.remove("opacity-0", "translate-y-2");
      el.classList.add("transition", "duration-300", "ease-out");
    });
  }
  
  function animateFadeOut(el, callback) {
    el.classList.add("transition", "duration-300", "ease-in", "opacity-0", "-translate-y-2");
    setTimeout(callback, 300);
  }
  
  function animateStatusFlash(el) {
    el.classList.add("ring-2", "ring-green-400", "transition");
    setTimeout(() => el.classList.remove("ring-2", "ring-green-400"), 300);
  }
  
  // ───────────────────────────────────────────────
  // WEBSOCKET: TASK CHANNEL
  // ───────────────────────────────────────────────
  if (teamId) {
    const socket = new WebSocket(`ws://${window.location.host}/ws/tasks/${teamId}/`);
  
    socket.onmessage = (e) => {
      const data = JSON.parse(e.data);
      const taskId = data.task_id;
      const taskElement = document.getElementById(`task-${taskId}`);
  
      if (recentlyUpdatedTasks.has(String(taskId))) return;
  
      switch (data.action) {
        case "create":
          const ul = document.querySelector("ul");
          const temp = document.createElement("div");
          temp.innerHTML = data.task_html;
          const newTask = temp.firstElementChild;
          animateFadeIn(newTask);
          ul.appendChild(newTask);
          break;
  
        case "update":
          if (taskElement) {
            const temp = document.createElement("div");
            temp.innerHTML = data.task_html;
            const updatedTask = temp.firstElementChild;
            animateStatusFlash(taskElement);
            taskElement.outerHTML = updatedTask.outerHTML;
          }
          break;
  
        case "delete":
          if (taskElement) {
            animateFadeOut(taskElement, () => taskElement.remove());
          }
          break;
  
        default:
          console.warn("Unknown task action:", data.action);
      }
    };
  
    socket.onopen = () => console.log("✅ WebSocket connected");
    socket.onclose = () => console.warn("❌ WebSocket disconnected");
    socket.onerror = (e) => console.error("WebSocket error:", e);
  }
  
  // ───────────────────────────────────────────────
  // WEBSOCKET: USER NOTIFICATIONS
  // ───────────────────────────────────────────────
  if (teamId) {
    const userSocket = new WebSocket(`ws://${window.location.host}/ws/user/`);
  
    userSocket.onmessage = (e) => {
      const data = JSON.parse(e.data);
      if (data.type === "invite_event" && data.action === "new_invite") {
        const container = document.getElementById("notification-area");
        if (!container) return;
  
        const div = document.createElement("div");
        div.className = "notification bg-blue-100 border border-blue-400 p-3 rounded relative text-sm";
        div.innerHTML = `
          📩 <strong>New Invite</strong> to <em>${data.team_name}</em> from <strong>${data.invited_by}</strong>
          — <a href="/invites/" class="underline text-blue-600">View</a>
          <button class="absolute top-1 right-2 text-gray-600" onclick="this.parentElement.remove()">×</button>
        `;
  
        container.prepend(div);
        setTimeout(() => div.remove(), 8000);
      }
    };
  
    userSocket.onopen = () => console.log("✅ WebSocket (user) connected");
    userSocket.onclose = () => console.warn("❌ WebSocket (user) disconnected");
    userSocket.onerror = (e) => console.error("WebSocket (user) error:", e);
  }
  
  // ───────────────────────────────────────────────
  // TASK STATUS UPDATE HANDLER
  // ───────────────────────────────────────────────
  function updateStatus(select) {
    const form = select.closest("form");
    const url = form.action;
    const taskId = form.dataset.taskId;
  
    recentlyUpdatedTasks.add(taskId);
    setTimeout(() => recentlyUpdatedTasks.delete(taskId), 1000);
  
    fetch(url, {
      method: "POST",
      headers: {
        "X-CSRFToken": document.querySelector('meta[name="csrf-token"]').content,
      },
      body: new FormData(form),
    }).catch(err => console.error("Status update error:", err));
  }
  
  // ───────────────────────────────────────────────
  // TASK DELETION HANDLER
  // ───────────────────────────────────────────────
  function handleDelete(form) {
    const taskId = form.dataset.taskId;
    if (!confirm("Are you sure?")) return false;
  
    recentlyUpdatedTasks.add(taskId);
    setTimeout(() => recentlyUpdatedTasks.delete(taskId), 1000);
  
    const url = form.action;
    const formData = new URLSearchParams();
    formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);
  
    fetch(url, {
      method: "POST",
      headers: {
        "X-CSRFToken": document.querySelector('meta[name="csrf-token"]').content,
      },
      body: formData,
    }).then(res => {
      if (!res.ok) throw new Error("Failed to delete task");
      const taskElement = document.getElementById(`task-${taskId}`);
      if (taskElement) animateFadeOut(taskElement, () => taskElement.remove());
    }).catch(err => console.error("Delete error:", err));
  
    return false;
  }
  
  // ───────────────────────────────────────────────
  // TOGGLE TASK DESCRIPTION
  // ───────────────────────────────────────────────
  function toggleDetails(taskId) {
    const details = document.getElementById(`details-${taskId}`);
    const link = document.getElementById(`toggle-link-${taskId}`);
    const isVisible = details.classList.contains("max-h-[500px]");
  
    if (isVisible) {
      details.classList.remove("max-h-[500px]", "opacity-100", "scale-y-100");
      details.classList.add("max-h-0", "opacity-0", "scale-y-95");
      link.textContent = "📄 View Details";
    } else {
      details.classList.remove("max-h-0", "opacity-0", "scale-y-95");
      details.classList.add("max-h-[500px]", "opacity-100", "scale-y-100");
      link.textContent = "🔽 Hide Details";
    }
  }
  
  // ───────────────────────────────────────────────
  // FORM HANDLERS: CREATE + EDIT
  // ───────────────────────────────────────────────
  document.addEventListener("DOMContentLoaded", () => {
    const createForm = document.getElementById("create-task-form");
    if (createForm) {
      createForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const formData = new FormData(createForm);
        fetch(createForm.action, {
          method: "POST",
          headers: {
            "X-CSRFToken": document.querySelector('meta[name="csrf-token"]').content,
          },
          body: formData,
        }).then(res => {
          if (!res.ok) throw new Error("Failed to create task");
          createForm.reset();
        }).catch(console.error);
      });
    }
  
    const editForm = document.getElementById("edit-task-form");
    if (editForm) {
      editForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const taskId = editForm.dataset.taskId;
        const formData = new FormData(editForm);
  
        recentlyUpdatedTasks.add(taskId);
        setTimeout(() => recentlyUpdatedTasks.delete(taskId), 1000);
  
        fetch(editForm.action, {
          method: "POST",
          headers: {
            "X-CSRFToken": document.querySelector('meta[name="csrf-token"]').content,
          },
          body: formData,
        }).then(res => {
          if (!res.ok) throw new Error("Failed to edit task");
          window.location.href = "/";
        }).catch(console.error);
      });
    }
  });
  
  // ───────────────────────────────────────────────
  // MOBILE NAV: SLIDE TOGGLE
  // ───────────────────────────────────────────────
  document.addEventListener('DOMContentLoaded', () => {
    const toggle = document.getElementById('menu-toggle');
    const navLinks = document.getElementById('mobile-nav-links');
  
    if (toggle && navLinks) {
      let isOpen = false;
  
      toggle.addEventListener('click', () => {
        if (!isOpen) {
          navLinks.style.display = 'flex';
          navLinks.style.overflow = 'hidden';
          navLinks.style.height = '0px';
          navLinks.style.opacity = '0';
          navLinks.style.transform = 'translateY(-10px)';
          navLinks.style.transition = 'height 0.3s ease, opacity 0.3s ease, transform 0.3s ease';
  
          requestAnimationFrame(() => {
            navLinks.style.height = navLinks.scrollHeight + 'px';
            navLinks.style.opacity = '1';
            navLinks.style.transform = 'translateY(0)';
          });
  
          isOpen = true;
        } else {
          navLinks.style.height = '0px';
          navLinks.style.opacity = '0';
          navLinks.style.transform = 'translateY(-10px)';
          setTimeout(() => navLinks.style.display = 'none', 300);
          isOpen = false;
        }
      });
    }
  });
  
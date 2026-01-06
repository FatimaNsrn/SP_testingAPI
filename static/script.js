const API_URL = "/assignments";

/* ---------------- FETCH & RENDER ---------------- */

function fetchAssignments() {
    fetch(API_URL)
        .then(res => res.json())
        .then(data => renderAssignments(data));
}

function renderAssignments(data) {
    const pendingList = document.getElementById("pendingList");
    const completedList = document.getElementById("completedList");

    pendingList.innerHTML = "";
    completedList.innerHTML = "";

    data.forEach(item => {
        const li = document.createElement("li");

        li.innerHTML = `
            <span>
                <strong>${item.title}</strong> (${item.course})<br>
                Deadline: ${item.deadline} | Priority: ${item.priority}
            </span>
        `;

        const actions = document.createElement("div");
        actions.className = "actions";

        if (item.status === "pending") {
            actions.innerHTML = `
                <button onclick="editAssignment(${item.id})">✏️</button>
                <button onclick="markCompleted(${item.id})">✅</button>
                <button onclick="deleteAssignment(${item.id})">🗑</button>
            `;
            li.appendChild(actions);
            pendingList.appendChild(li);
        } else {
            actions.innerHTML = `
                <button onclick="deleteAssignment(${item.id})">🗑</button>
            `;
            li.appendChild(actions);
            completedList.appendChild(li);
        }
    });
}

/* ---------------- UI CONTROL ---------------- */

function toggleSection(section) {
    document.getElementById("pending").classList.add("hidden");
    document.getElementById("completed").classList.add("hidden");

    document.getElementById(section).classList.remove("hidden");
}

/* ---------------- API ACTIONS ---------------- */

/* CREATE */
function createAssignment() {
    const data = {
        course: course.value,
        title: title.value,
        description: description.value,
        deadline: deadline.value,
        priority: priority.value
    };

    fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    })
    .then(res => {
        if (res.status === 201) window.location.href = "/";
        else return res.json();
    })
    .then(err => {
        if (err) document.getElementById("message").innerText = err.error;
    });
}

/* UPDATE → MARK COMPLETED */
function markCompleted(id) {
    fetch(`${API_URL}/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: "completed" })
    })
    .then(() => fetchAssignments());
}

/* DELETE */
function deleteAssignment(id) {
    fetch(`${API_URL}/${id}`, { method: "DELETE" })
        .then(() => fetchAssignments());
}

function editAssignment(id) {
    window.location.href = `/edit/${id}`;
}

/* SEARCH */
function searchAssignments() {
    const course = document.getElementById("searchCourse").value;

    fetch(`/assignments?course=${encodeURIComponent(course)}`)
        .then(res => res.json())
        .then(data => {
            document.querySelector(".list").classList.remove("hidden");
            renderAssignments(data);
        });
}


function updateAssignment(id) {
    const data = {
        course: document.getElementById("course").value,
        title: document.getElementById("title").value,
        description: document.getElementById("description").value,
        deadline: document.getElementById("deadline").value,
        priority: document.getElementById("priority").value
    };

    fetch(`/assignments/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    })
    .then(res => {
        if (res.status === 200) {
            window.location.href = "/";
        } else {
            alert("Update failed");
        }
    });
}


/* ---------------- INIT ---------------- */

window.onload = fetchAssignments;

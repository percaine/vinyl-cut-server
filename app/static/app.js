const statusBox = document.getElementById('status-box');
const deviceList = document.getElementById('device-list');
const jobsList = document.getElementById('jobs-list');
const uploadForm = document.getElementById('upload-form');
const jobForm = document.getElementById('job-form');
const uploadResult = document.getElementById('upload-result');
const jobDevice = document.getElementById('job-device');
const jobFilename = document.getElementById('job-filename');

let ws = null;
const wsQueue = [];

function connectWebSocket() {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  ws = new WebSocket(`${protocol}//${window.location.host}/ws`);
  ws.onopen = () => {
    console.log('WebSocket connected');
    while (wsQueue.length > 0) {
      const msg = wsQueue.shift();
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(msg);
      }
    }
  };
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.jobs) {
      updateJobsDisplay(data.jobs);
    }
    if (data.devices) {
      updateDevicesDisplay(data.devices);
    }
  };
  ws.onclose = () => {
    console.log('WebSocket closed. Reconnecting in 3s...');
    setTimeout(connectWebSocket, 3000);
  };
}

async function loadStatus() {
  try {
    const response = await fetch('/api/status');
    const data = await response.json();
    statusBox.innerHTML = `
      <strong>Status:</strong> ${data.status}<br>
      <strong>Version:</strong> ${data.version}<br>
      <strong>Connected Devices:</strong> ${data.device_count}
    `;
  } catch (err) {
    statusBox.textContent = 'Error loading status';
  }
}

function updateDevicesDisplay(devices) {
  deviceList.innerHTML = '';
  jobDevice.innerHTML = '';
  devices.forEach((device) => {
    const item = document.createElement('li');
    item.innerHTML = `
      <strong>${device.name}</strong><br>
      <small>${device.kind} | ${device.status}</small>
    `;
    deviceList.appendChild(item);

    const option = document.createElement('option');
    option.value = device.id;
    option.textContent = `${device.name} (${device.kind})`;
    jobDevice.appendChild(option);
  });
}

function updateJobsDisplay(jobs) {
  jobsList.innerHTML = '';

  if (!jobs.length) {
    jobsList.innerHTML = '<div class="job-card">No jobs yet.</div>';
    return;
  }

  jobs.forEach((job) => {
    const card = document.createElement('div');
    card.className = 'job-card';
    const statusColor = job.status === 'completed' ? '#22c55e' : job.status === 'failed' ? '#ef4444' : '#2563eb';
    card.style.borderLeft = `4px solid ${statusColor}`;

    const logsHtml = job.logs.slice(-3).map(log => `<div style="font-size:0.85em; color:#94a3b8; margin-top:0.2rem;">${escapeHtml(log)}</div>`).join('');

    card.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <div>
          <strong>${escapeHtml(job.filename)}</strong>
          <div style="font-size:0.9em; color:#9ca3af; margin-top:0.2rem;">${job.id}</div>
        </div>
        <div style="text-align:right;">
          <span style="font-weight:bold; color:${statusColor};">${job.status}</span>
        </div>
      </div>
      <div class="progress-bar"><span class="progress-fill" style="width:${job.progress}%"></span></div>
      <div style="font-size:0.9em; color:#cbd5e1;">${job.progress}%</div>
      ${logsHtml}
      <div style="margin-top:0.6rem; display:flex; gap:0.4rem;">
        ${job.status === 'queued' || job.status === 'preparing' ? `<button class="btn-start" data-id="${job.id}">Start</button>` : ''}
        ${job.status === 'cutting' || job.status === 'preparing' ? `<button class="btn-cancel" data-id="${job.id}">Cancel</button>` : ''}
      </div>
    `;
    jobsList.appendChild(card);
  });
}

function escapeHtml(text) {
  const map = {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'};
  return text.replace(/[&<>"']/g, m => map[m]);
}

uploadForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const formData = new FormData(uploadForm);
  try {
    const response = await fetch('/api/upload', {
      method: 'POST',
      body: formData,
    });
    const result = await response.json();
    uploadResult.textContent = `✓ Uploaded: ${result.filename}`;
    jobFilename.value = result.filename;
    uploadForm.reset();
  } catch (err) {
    uploadResult.textContent = `✗ Upload failed: ${err}`;
  }
});

jobForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const formData = new FormData();
  formData.append('filename', jobFilename.value);
  formData.append('device_id', jobDevice.value);
  formData.append('speed', document.getElementById('job-speed').value);
  formData.append('pressure', document.getElementById('job-pressure').value);
  formData.append('tool', document.getElementById('job-tool').value);

  try {
    const response = await fetch('/api/jobs', {
      method: 'POST',
      body: formData,
    });
    const data = await response.json();
    uploadResult.textContent = `✓ Job queued: ${data.job.id}`;
    jobForm.reset();
  } catch (err) {
    uploadResult.textContent = `✗ Failed to queue job: ${err}`;
  }
});

jobsList.addEventListener('click', async (event) => {
  const btn = event.target.closest('button');
  if (!btn) return;
  const id = btn.dataset.id;

  if (btn.classList.contains('btn-start')) {
    try {
      await fetch(`/api/jobs/${id}/start`, { method: 'POST' });
    } catch (err) {
      console.error('Failed to start job:', err);
    }
  }

  if (btn.classList.contains('btn-cancel')) {
    try {
      await fetch(`/api/jobs/${id}/cancel`, { method: 'POST' });
    } catch (err) {
      console.error('Failed to cancel job:', err);
    }
  }
});

loadStatus();
connectWebSocket();
setInterval(loadStatus, 10000);

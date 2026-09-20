body {
  margin: 0;
  font-family: Arial, sans-serif;
  background: #0f172a;
  color: #e2e8f0;
}

.container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

header {
  margin-bottom: 2rem;
}

h1, h2 {
  margin-top: 0;
}

.panel {
  background: #111827;
  border: 1px solid #374151;
  border-radius: 12px;
  padding: 1rem 1.2rem;
  margin-bottom: 1rem;
}

.status-box {
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 8px;
  padding: 0.8rem;
}

.list, .jobs-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.list li, .job-card {
  background: #0b1220;
  border: 1px solid #334155;
  border-radius: 8px;
  margin-top: 0.6rem;
  padding: 0.8rem;
}

form {
  display: grid;
  gap: 0.8rem;
}

label {
  display: grid;
  gap: 0.3rem;
}

input, select, button {
  padding: 0.7rem 0.8rem;
  border-radius: 8px;
  border: 1px solid #475569;
  background: #0f172a;
  color: #e2e8f0;
}

button {
  background: #2563eb;
  border: none;
  cursor: pointer;
  width: fit-content;
}

button.secondary {
  background: #374151;
}

.message {
  margin-top: 0.8rem;
  color: #bfdbfe;
}

.job-card {
  display: grid;
  gap: 0.4rem;
}

.progress-bar {
  width: 100%;
  height: 16px;
  background: #1f2937;
  border-radius: 999px;
  overflow: hidden;
}

.progress-fill {
  display: block;
  height: 100%;
  background: linear-gradient(90deg, #22c55e, #84cc16);
}

@media (min-width: 700px) {
  form {
    grid-template-columns: repeat(2, minmax(200px, 1fr));
  }
}

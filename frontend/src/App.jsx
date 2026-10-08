import { useCallback, useEffect, useState } from "react";
import { api } from "./api.js";

const STATUSES = ["applied", "interview", "offer", "rejected"];
const EMPTY = { company: "", role: "", status: "applied", notes: "" };

export default function App() {
  const [jobs, setJobs] = useState([]);
  const [stats, setStats] = useState(null);
  const [filter, setFilter] = useState("");
  const [form, setForm] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    try {
      const [list, summary] = await Promise.all([api.list(filter), api.stats()]);
      setJobs(list);
      setStats(summary);
      setError("");
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [filter]);

  useEffect(() => { load(); }, [load]);

  function openForm(job) {
    setError("");
    setForm(job);
  }

  async function save(e) {
    e.preventDefault();
    const { id, ...payload } = form;
    try {
      await (id ? api.update(id, payload) : api.create(payload));
      setForm(null);
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  async function remove(id) {
    try {
      await api.remove(id);
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="app">
      <header>
        <div>
          <h1>PlaceTrack</h1>
          <p>Track every job application in one place</p>
        </div>
        <button className="primary" onClick={() => openForm(EMPTY)}>+ Add application</button>
      </header>

      {error && !form && <div className="error">{error}</div>}

      <section className="cards">
        {["total", ...STATUSES].map((key) => (
          <div className={`card ${key}`} key={key}>
            <span>{key}</span>
            <strong>{stats ? stats[key] : "–"}</strong>
          </div>
        ))}
      </section>

      <div className="filters">
        {["", ...STATUSES].map((s) => (
          <button key={s} className={filter === s ? "chip active" : "chip"} onClick={() => setFilter(s)}>
            {s || "all"}
          </button>
        ))}
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr><th>Company</th><th>Role</th><th>Status</th><th>Applied</th><th>Notes</th><th></th></tr>
          </thead>
          <tbody>
            {loading && <tr><td colSpan="6">Loading…</td></tr>}
            {!loading && jobs.length === 0 && <tr><td colSpan="6">No applications yet.</td></tr>}
            {jobs.map((j) => (
              <tr key={j.id}>
                <td>{j.company}</td>
                <td>{j.role}</td>
                <td><span className={`badge ${j.status}`}>{j.status}</span></td>
                <td>{j.applied_on}</td>
                <td>{j.notes}</td>
                <td className="actions">
                  <button onClick={() => openForm(j)}>Edit</button>
                  <button className="danger" onClick={() => remove(j.id)}>Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {form && (
        <div className="overlay" onClick={() => setForm(null)}>
          <form className="modal" onClick={(e) => e.stopPropagation()} onSubmit={save}>
            <h2>{form.id ? "Edit application" : "New application"}</h2>
            {error && <div className="error">{error}</div>}
            <label>Company<input required maxLength={120} value={form.company} onChange={(e) => setForm({ ...form, company: e.target.value })} /></label>
            <label>Role<input required maxLength={120} value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })} /></label>
            <label>Status
              <select value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })}>
                {STATUSES.map((s) => <option key={s}>{s}</option>)}
              </select>
            </label>
            <label>Notes<textarea value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} /></label>
            <div className="modal-actions">
              <button type="button" onClick={() => setForm(null)}>Cancel</button>
              <button className="primary" type="submit">Save</button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}

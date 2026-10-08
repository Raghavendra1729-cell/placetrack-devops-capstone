async function request(path, options) {
  const res = await fetch(path, { headers: { "Content-Type": "application/json" }, ...options });
  if (!res.ok) throw new Error(`Request failed (${res.status})`);
  return res.status === 204 ? null : res.json();
}

export const api = {
  list: (status) => request(`/api/jobs${status ? `?status=${status}` : ""}`),
  stats: () => request("/api/jobs/stats"),
  create: (job) => request("/api/jobs", { method: "POST", body: JSON.stringify(job) }),
  update: (id, job) => request(`/api/jobs/${id}`, { method: "PUT", body: JSON.stringify(job) }),
  remove: (id) => request(`/api/jobs/${id}`, { method: "DELETE" }),
};

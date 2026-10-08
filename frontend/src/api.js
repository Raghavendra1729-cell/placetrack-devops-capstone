async function request(path, options) {
  let res;
  try {
    res = await fetch(path, { headers: { "Content-Type": "application/json" }, ...options });
  } catch {
    throw new Error("Could not reach the API");
  }
  if (res.status === 422) throw new Error("Company and role are required (up to 120 characters)");
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

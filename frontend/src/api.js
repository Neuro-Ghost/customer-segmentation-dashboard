const API_BASE_URL = "http://127.0.0.1:8000"; // backend URL

export async function fetchClusters(file) {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE_URL}/predict`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    throw new Error("Failed to fetch clusters");
  }
  return await res.json();
}

export async function healthCheck() {
  const res = await fetch(`${API_BASE_URL}/health`);
  return res.json();
}

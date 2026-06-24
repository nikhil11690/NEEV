// NEEV — shared backend config
const NEEV_API = "https://neev-amiu.onrender.com";

async function neevFetch(path, options = {}) {
  const res = await fetch(`${NEEV_API}${path}`, options);
  if (!res.ok) {
    let detail = "";
    try { detail = JSON.stringify(await res.json()); } catch (e) {}
    throw new Error(`${res.status} ${res.statusText} ${detail}`);
  }
  return res.json();
}
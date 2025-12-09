const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:5000";

/**
 * Transforme "media/p2/xxx.jpg" en "http://localhost:5000/media/p2/xxx.jpg".
 * Gère aussi "/media/..." et les URLs déjà absolues.
 */
export function toMediaUrl(path?: string): string {
  if (!path) return "/assets/images/placeholder.jpg";
  if (/^https?:\/\//i.test(path)) return path;        // déjà absolu
  if (path.startsWith("/assets/")) return path;       // asset front

  // match "media/{pid}/{filename}" ou "/media/{pid}/{filename}"
  const m = path.match(/^\/?media\/([^/]+)\/(.+)$/);
  if (!m) return "/assets/images/placeholder.jpg";

  const pid = encodeURIComponent(m[1]);
  const filename = encodeURIComponent(m[2]);
  const base = API_BASE.replace(/\/+$/, "");
  return `${base}/media/${pid}/${filename}`;
}

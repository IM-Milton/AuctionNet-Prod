// src/services/categoryService.ts

const API =  "http://localhost:5000";

export type CategoriesResponse = { categories: string[] };

export async function getCategories(): Promise<string[]> {
  const r = await fetch(`${API}/api/categories`);
  if (!r.ok) throw new Error(await r.text());
  const data = (await r.json()) as CategoriesResponse;
  return data.categories ?? [];
}

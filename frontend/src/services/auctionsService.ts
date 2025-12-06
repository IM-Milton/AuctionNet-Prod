// src/services/auctionService.ts
import type { Auction, AuctionsResponse } from "../models/auction";

const API =  "http://localhost:5000";

type AuctionQuery = {
  status?: "scheduled" | "running" | "closed";
  category?: string;
  search?: string;
};

export async function getAllAuctions(
  query: AuctionQuery = {}
): Promise<Auction[]> {
  const params = new URLSearchParams();

  if (query.status) params.append("status", query.status);
  if (query.category) params.append("category", query.category);
  if (query.search) params.append("search", query.search);

  const qs = params.toString();
  const url = qs ? `${API}/api/auctions?${qs}` : `${API}/api/auctions`;

  const r = await fetch(url);
  if (!r.ok) throw new Error(await r.text());

  const data = (await r.json()) as AuctionsResponse;
  return data.auctions ?? [];
}

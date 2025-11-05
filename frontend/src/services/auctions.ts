import type { Auction, AuctionsResponse } from "../models/auction";

const API = ""; 

export async function getAllAuctions(): Promise<Auction[]> {
  const r = await fetch(`${API}/api/auctions`);
  if (!r.ok) throw new Error(await r.text());
  const data = (await r.json()) as AuctionsResponse;
  return data.auctions ?? [];
}

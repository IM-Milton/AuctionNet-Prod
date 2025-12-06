import { Product } from "./product";

export type Auction = {
  id: string;
  product_id: string;
  start_price: number;
  current_price: number;
  min_increment: number;
  start_at: string;
  end_at: string;
  status: "scheduled" | "running" | "closed";
  current_bid_id: string | null;
  product?: Product;
};

export type AuctionsResponse = { auctions: Auction[] };

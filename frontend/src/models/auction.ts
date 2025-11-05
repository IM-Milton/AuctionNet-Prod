export type Auction = {
  product_id: string;
  start_price: number;
  start_at: string;
  end_at: string;
  min_increment: number;
  product?: {
    title?: string;
    images?: string[];
  };
};

export type AuctionsResponse = { auctions: Auction[] };
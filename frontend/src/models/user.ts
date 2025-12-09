import { Product } from "./product";

export type User = {
  id: string;
  email: string;
  balance: number;
  held: number;
 purchases: Product[]
};
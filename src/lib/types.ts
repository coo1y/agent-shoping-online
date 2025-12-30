export interface BackendProduct {
  product_id?: string;
  id?: string;
  name: string;
  brand: string;
  category: string;
  price_cents?: number;
  price?: number;
  stock?: number;
  description?: string;
  specs?: Record<string, string | number>;
  popularity?: number;
  image_url?: string;
}

export interface Product {
  product_id: string;
  name: string;
  brand: string;
  category: string;
  price_cents: number;
  currency: string;
  aliases: string[];
  specs: Record<string, string | number>;
  rating: number;
  popularity: number;
  image_url: string;
  is_active: boolean;
  // Derived or optional for compatibility/UI logic
  id: string; // mapped from product_id for compatibility
  price: number; // mapped from price_cents / 100
  stock: number; // mocked for now
  description: string; // mocked or from specs
  is_featured: boolean; // mocked based on popularity
}

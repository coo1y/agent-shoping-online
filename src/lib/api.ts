import "server-only";

import type { Product, BackendProduct } from "@/lib/types";

const BACKEND_URL =
  process.env.BACKEND_URL ?? process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://127.0.0.1:8000";

const API_BASE_URL = `${BACKEND_URL.replace(/\/$/, "")}/api`;

export type { Product };

export async function getProducts(category?: string): Promise<Product[]> {
  const url = new URL(`${API_BASE_URL}/products/`);
  if (category) {
    url.searchParams.append("category", category);
  }
  
  try {
    const res = await fetch(url.toString(), { cache: 'no-store' });
    if (!res.ok) throw new Error("Failed to fetch products");
    const products = await res.json();
    
    // Map backend response to frontend interface if needed, or assume backend returns this shape
    // For now, let's assume we need to transform if the backend returns the raw SQL shape
    return products.map((p: BackendProduct) => ({
      ...p,
      product_id: p.product_id || p.id || '',
      id: p.product_id || p.id || '',
      price_cents: p.price_cents ?? Math.round((p.price ?? 0) * 100),
      price: p.price_cents ? p.price_cents / 100 : (p.price ?? 0),
      stock: p.stock ?? 100, // Use real stock if available, else mock
      description: p.specs ? `${p.brand || ''} ${p.name} with ${Object.entries(p.specs).map(([k,v]) => `${k}: ${v}`).join(', ')}` : (p.description ?? ''),
      specs: p.specs ?? {},
      popularity: p.popularity ?? 0,
      image_url: p.image_url || '/images/products/placeholder.jpg',
      is_featured: (p.popularity ?? 0) > 100,
      // Add missing required Product properties with defaults
      currency: 'USD',
      aliases: [],
      rating: 0,
      is_active: true
    }));
  } catch (error) {
    console.error("Error fetching products:", error);
    return [];
  }
}

export async function getProduct(id: string): Promise<Product | null> {
  try {
    const fetchUrl = `${API_BASE_URL}/products/${id}`;
    console.log(`[API] Fetching product from: ${fetchUrl}`);
    
    const res = await fetch(fetchUrl, { cache: 'no-store' });
    console.log(`[API] Response status: ${res.status}`);
    
    if (!res.ok) {
        if (res.status === 404) {
            console.log(`[API] Product ${id} not found (404)`);
            return null;
        }
        const text = await res.text();
        console.error(`[API] Failed to fetch product. Status: ${res.status}, Body: ${text}`);
        throw new Error("Failed to fetch product");
    }
    const p: BackendProduct = await res.json();
    console.log(`[API] Successfully fetched product: ${p.name}`);
    return {
      ...p,
      product_id: p.product_id || p.id || '',
      id: p.product_id || p.id || '',
      price_cents: p.price_cents ?? Math.round((p.price ?? 0) * 100),
      price: p.price_cents ? p.price_cents / 100 : (p.price ?? 0),
      stock: p.stock ?? 50, // Use real stock if available, else mock
      description: p.specs ? `${p.brand || ''} ${p.name}` : (p.description ?? ''),
      specs: p.specs ?? {},
      popularity: p.popularity ?? 0,
      image_url: p.image_url || '/images/products/placeholder.jpg',
      is_featured: (p.popularity ?? 0) > 100,
      // Add missing required Product properties with defaults
      currency: 'USD',
      aliases: [],
      rating: 0,
      is_active: true
    };
  } catch (error) {
    console.error(`[API] Error fetching product ${id}:`, error);
    return null;
  }
}

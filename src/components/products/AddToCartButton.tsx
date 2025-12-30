"use client";

import { Button } from "@/components/ui/button";
import { useCart } from "@/components/providers/CartProvider";
import { Product } from "@/lib/types";
import { ShoppingCart } from "lucide-react";

interface AddToCartButtonProps {
  product: Product;
  size?: "default" | "sm" | "lg" | "icon";
  className?: string;
}

export function AddToCartButton({ product, size = "default", className }: AddToCartButtonProps) {
  const { addItem } = useCart();

  return (
    <Button 
      size={size} 
      className={className} 
      onClick={(e) => {
        e.preventDefault(); // Prevent navigation if inside a link
        addItem(product);
      }}
      disabled={product.stock <= 0}
    >
      <ShoppingCart className="mr-2 h-4 w-4" />
      {product.stock > 0 ? "Add to Cart" : "Out of Stock"}
    </Button>
  );
}

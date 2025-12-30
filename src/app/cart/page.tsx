"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import { Trash2, Plus, Minus, ArrowRight, ShoppingBag } from "lucide-react";
import { useCart } from "@/components/providers/CartProvider";
import { toast } from "sonner";

export default function CartPage() {
  const { items, removeItem, updateQuantity, subtotal, totalItems, clearCart } = useCart();
  const tax = subtotal * 0.1; // 10% tax example
  const total = subtotal + tax;

  const handleCheckout = () => {
    clearCart();
    toast.success("Payment successful! Thank you for your purchase.", {
      style: {
        backgroundColor: "#22c55e",
        color: "white",
        border: "none"
      }
    });
  };

  if (items.length === 0) {
      return (
          <div className="container mx-auto px-4 py-20 flex flex-col items-center justify-center text-center gap-4">
              <div className="h-20 w-20 bg-muted rounded-full flex items-center justify-center">
                  <ShoppingBag className="h-10 w-10 text-muted-foreground" />
              </div>
              <h1 className="text-2xl font-bold">Your cart is empty</h1>
              <p className="text-muted-foreground">Looks like you haven&apos;t added anything to your cart yet.</p>
              <Button asChild className="mt-4">
                  <Link href="/shop">Start Shopping</Link>
              </Button>
          </div>
      )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold tracking-tight mb-8">Shopping Cart ({totalItems} items)</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">
        {/* Cart Items List */}
        <div className="lg:col-span-2 space-y-4">
            {items.map((item) => (
                <Card key={item.id}>
                    <CardContent className="p-4 flex gap-4 sm:gap-6 items-start sm:items-center">
                        <div className="h-24 w-24 sm:h-32 sm:w-32 bg-muted rounded-md flex-shrink-0 flex items-center justify-center text-muted-foreground text-xs text-center p-2 overflow-hidden relative">
                            {item.image_url ? (
                                <img src={item.image_url} alt={item.name} className="object-cover w-full h-full" />
                            ) : (
                                <span>No Image</span>
                            )}
                        </div>
                        <div className="flex-1 grid gap-1">
                            <h3 className="font-semibold text-lg leading-none">
                                <Link href={`/shop/${item.id}`} className="hover:underline">
                                    {item.name}
                                </Link>
                            </h3>
                            <p className="text-sm text-muted-foreground capitalize">Category: {item.category}</p>
                            <div className="flex items-center justify-between mt-2 sm:mt-0 sm:hidden">
                                <p className="font-bold">${item.price.toFixed(2)}</p>
                            </div>
                        </div>
                        <div className="hidden sm:block text-right">
                             <p className="font-bold text-lg">${(item.price * item.quantity).toFixed(2)}</p>
                             {item.quantity > 1 && (
                                 <p className="text-sm text-muted-foreground">${item.price.toFixed(2)} each</p>
                             )}
                        </div>
                        <div className="flex flex-col sm:flex-row items-end sm:items-center gap-4 ml-auto">
                            <div className="flex items-center border rounded-md">
                                <Button
                                    variant="ghost"
                                    size="icon"
                                    className="h-8 w-8 rounded-r-none"
                                    onClick={() => updateQuantity(item.id, item.quantity - 1)}
                                    disabled={item.quantity <= 1}
                                >
                                    <Minus className="h-3 w-3" />
                                </Button>
                                <span className="w-8 text-center text-sm">{item.quantity}</span>
                                <Button
                                    variant="ghost"
                                    size="icon"
                                    className="h-8 w-8 rounded-l-none"
                                    onClick={() => updateQuantity(item.id, item.quantity + 1)}
                                >
                                    <Plus className="h-3 w-3" />
                                </Button>
                            </div>
                            <Button
                                variant="ghost"
                                size="icon"
                                className="text-destructive hover:text-destructive hover:bg-destructive/10"
                                onClick={() => removeItem(item.id)}
                            >
                                <Trash2 className="h-4 w-4" />
                            </Button>
                        </div>
                    </CardContent>
                </Card>
            ))}
        </div>

        {/* Order Summary */}
        <div className="lg:col-span-1">
            <Card className="sticky top-24">
                <CardHeader>
                    <CardTitle>Order Summary</CardTitle>
                </CardHeader>
                <CardContent className="grid gap-4">
                    <div className="flex items-center justify-between text-sm">
                        <span className="text-muted-foreground">Subtotal</span>
                        <span>${subtotal.toFixed(2)}</span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                        <span className="text-muted-foreground">Shipping</span>
                        <span className="text-green-600">Free</span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                        <span className="text-muted-foreground">Tax (10%)</span>
                        <span>${tax.toFixed(2)}</span>
                    </div>
                    <Separator />
                    <div className="flex items-center justify-between font-bold text-lg">
                        <span>Total</span>
                        <span>${total.toFixed(2)}</span>
                    </div>
                    
                    <div className="space-y-2 pt-4">
                        <div className="flex gap-2">
                            <Input placeholder="Coupon code" />
                            <Button variant="outline">Apply</Button>
                        </div>
                    </div>
                </CardContent>
                <CardFooter>
                    <Button className="w-full" size="lg" onClick={handleCheckout}>
                        Checkout <ArrowRight className="ml-2 h-4 w-4" />
                    </Button>
                </CardFooter>
            </Card>
        </div>
      </div>
    </div>
  );
}

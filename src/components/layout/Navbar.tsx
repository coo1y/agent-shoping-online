"use client";

import Link from "next/link";
import { ShoppingCart, Search, Menu, User, Phone } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { useCart } from "@/components/providers/CartProvider";
import { Badge } from "@/components/ui/badge";

export function Navbar() {
  const { totalItems } = useCart();

  return (
    <div className="flex flex-col w-full z-50 sticky top-0">
      {/* Top Main Header - Dark Background */}
      <header className="w-full bg-[#0047AB] text-white border-b border-blue-700">
        <div className="container mx-auto px-4 h-20 flex items-center justify-between gap-4">
          
          {/* Mobile Menu Trigger */}
          <Sheet>
            <SheetTrigger asChild>
              <Button variant="ghost" size="icon" className="md:hidden text-white hover:bg-white/10 hover:text-white">
                <Menu className="h-6 w-6" />
                <span className="sr-only">Toggle Menu</span>
              </Button>
            </SheetTrigger>
            <SheetContent side="left" className="w-[300px] border-r-primary">
              <nav className="flex flex-col gap-6 mt-6">
                <Link href="/" className="font-bold text-2xl tracking-tight text-primary">
                  TechShop
                </Link>
                <div className="flex flex-col gap-4">
                  <Link href="/shop" className="text-lg font-medium hover:text-primary transition-colors">
                    All Products
                  </Link>
                  <Link href="/shop?category=phones" className="text-lg font-medium hover:text-primary transition-colors">
                    Phones
                  </Link>
                  <Link href="/shop?category=notebooks" className="text-lg font-medium hover:text-primary transition-colors">
                    Notebooks
                  </Link>
                  <Link href="/shop?category=accessories" className="text-lg font-medium hover:text-primary transition-colors">
                    Accessories
                  </Link>
                </div>
              </nav>
            </SheetContent>
          </Sheet>

          {/* Logo */}
          <Link href="/" className="flex items-center gap-2 mr-4">
            <span className="font-extrabold text-2xl tracking-tight text-white">Tech<span className="text-primary">Shop.</span></span>
          </Link>

          {/* Search Bar - Centered */}
          <div className="hidden md:flex flex-1 max-w-2xl mx-auto relative">
             <div className="relative w-full flex">
                <Input
                  placeholder="Search products..."
                  className="w-full pl-4 pr-12 h-11 rounded-r-none rounded-l-md bg-white text-black border-none focus-visible:ring-0"
                />
                <Button className="h-11 rounded-l-none rounded-r-md bg-primary hover:bg-primary/90 text-primary-foreground px-6">
                    <Search className="h-5 w-5" />
                </Button>
             </div>
          </div>

          {/* Icons */}
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="icon" className="md:hidden text-white hover:bg-white/10 hover:text-white">
              <Search className="h-6 w-6" />
            </Button>
            
            <Button variant="ghost" size="icon" className="text-white hover:bg-white/10 hover:text-white relative" asChild>
                <Link href="/cart">
                    <ShoppingCart className="h-6 w-6" />
                    <span className="sr-only">Cart</span>
                    {totalItems > 0 && (
                        <Badge className="absolute -top-1 -right-1 h-5 w-5 p-0 flex items-center justify-center text-[11px] rounded-full bg-primary text-primary-foreground border-2 border-[#222]">
                            {totalItems}
                        </Badge>
                    )}
                </Link>
            </Button>
            
            <Button variant="ghost" size="icon" className="text-white hover:bg-white/10 hover:text-white hidden sm:flex">
                <User className="h-6 w-6" />
                <span className="sr-only">Profile</span>
            </Button>
          </div>
        </div>
      </header>

      {/* Secondary Navigation Bar - Yellow */}
      <div className="w-full bg-primary text-primary-foreground shadow-md hidden md:block">
        <div className="container mx-auto px-4 h-12 flex items-center justify-between">
            <nav className="flex items-center gap-8 text-sm font-bold uppercase tracking-wide">
                <Link href="/" className="hover:text-white transition-colors">Home</Link>
                <Link href="/shop" className="hover:text-white transition-colors">Shop</Link>
                <Link href="/shop?category=phones" className="hover:text-white transition-colors">Phones</Link>
                <Link href="/shop?category=notebooks" className="hover:text-white transition-colors">Notebooks</Link>
                <Link href="/shop?category=accessories" className="hover:text-white transition-colors">Accessories</Link>
            </nav>
            
            <div className="flex items-center gap-2 text-sm font-semibold opacity-90">
                <Phone className="h-4 w-4" />
                <span>Call Us: +1 234 567 890</span>
            </div>
        </div>
      </div>
    </div>
  );
}

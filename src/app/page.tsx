import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardTitle } from "@/components/ui/card";
import { Laptop, Smartphone, Headphones, Zap, Monitor, Watch, Camera } from "lucide-react";
import { getProducts } from "@/lib/api";

export default async function Home() {
  const products = await getProducts();
  const featuredProducts = products.filter(p => p.is_featured).slice(0, 8);
  // Fallback if no featured products (e.g. empty DB)
  const displayProducts = featuredProducts.length > 0 ? featuredProducts : products.slice(0, 8);

  return (
    <div className="flex flex-col gap-16 pb-20 bg-[#f9f9f9]">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-muted/30 py-20 sm:py-28">
        <div className="container mx-auto px-4 flex flex-col md:flex-row items-center justify-between gap-12 relative z-10">
          <div className="flex flex-col items-start text-left gap-6 max-w-2xl">
            <div className="inline-flex items-center text-sm font-bold tracking-widest text-primary uppercase">
              <Zap className="mr-2 h-4 w-4" /> New Arrival 2025
            </div>
            
            <h1 className="text-5xl font-black tracking-tight sm:text-7xl text-[#222]">
              New Tech <br/>
              <span className="text-primary">Collection</span>
            </h1>
            
            <p className="max-w-[500px] text-muted-foreground text-xl leading-relaxed">
              Get the best tech gear at unbeatable prices. Shop the latest laptops, phones, and accessories today.
            </p>
            
            <div className="flex gap-4 mt-2">
              <Button asChild size="lg" className="h-12 px-8 text-base font-bold uppercase tracking-wide shadow-md hover:shadow-lg transition-all">
                <Link href="/shop">Shop Now</Link>
              </Button>
            </div>
          </div>

          {/* Abstract placeholder for hero image if we don't have a real one */}
          <div className="w-full md:w-1/2 aspect-[4/3] bg-gray-100 rounded-3xl flex items-center justify-center relative shadow-2xl overflow-hidden group">
              <img 
                src="/images/products/macbook-bg.jpg" 
                alt="MacBook Pro M3 Max"
                className="absolute inset-0 w-full h-full object-cover object-center transition-transform duration-700 group-hover:scale-105"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent pointer-events-none"></div>
              
              <div className="relative z-10 bg-white/90 backdrop-blur-md p-8 rounded-2xl shadow-xl max-w-xs transform rotate-3 hover:rotate-0 transition-transform duration-500 border border-white/50">
                  <p className="font-bold text-lg text-[#222]">Apple MacBook Pro</p>
                  <p className="text-sm text-muted-foreground">M3 Max Chip</p>
                  <div className="mt-4 flex items-center justify-between">
                      <span className="font-bold text-primary text-xl">$2,499</span>
                      <Button size="sm" className="rounded-full">Buy</Button>
                  </div>
              </div>
          </div>
        </div>
      </section>

      {/* Top Categories */}
      <section className="container mx-auto px-4">
        <div className="flex flex-col items-center text-center gap-2 mb-12">
            <h2 className="text-2xl font-bold tracking-tight text-[#222] uppercase border-b-2 border-primary pb-2">Top Categories</h2>
        </div>
        
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-6">
          <Link href="/shop?category=phones" className="group flex flex-col items-center gap-3">
             <div className="h-24 w-24 rounded-full bg-white shadow-md flex items-center justify-center group-hover:bg-primary group-hover:text-white transition-all duration-300 border border-gray-100">
                <Smartphone className="h-10 w-10" />
             </div>
             <span className="font-semibold text-sm uppercase tracking-wide">Phones</span>
          </Link>
          <Link href="/shop?category=notebooks" className="group flex flex-col items-center gap-3">
             <div className="h-24 w-24 rounded-full bg-white shadow-md flex items-center justify-center group-hover:bg-primary group-hover:text-white transition-all duration-300 border border-gray-100">
                <Laptop className="h-10 w-10" />
             </div>
             <span className="font-semibold text-sm uppercase tracking-wide">Laptops</span>
          </Link>
          <Link href="/shop?category=accessories" className="group flex flex-col items-center gap-3">
             <div className="h-24 w-24 rounded-full bg-white shadow-md flex items-center justify-center group-hover:bg-primary group-hover:text-white transition-all duration-300 border border-gray-100">
                <Headphones className="h-10 w-10" />
             </div>
             <span className="font-semibold text-sm uppercase tracking-wide">Audios</span>
          </Link>
          <Link href="/shop?category=accessories" className="group flex flex-col items-center gap-3">
             <div className="h-24 w-24 rounded-full bg-white shadow-md flex items-center justify-center group-hover:bg-primary group-hover:text-white transition-all duration-300 border border-gray-100">
                <Monitor className="h-10 w-10" />
             </div>
             <span className="font-semibold text-sm uppercase tracking-wide">Monitors</span>
          </Link>
          <Link href="/shop?category=accessories" className="group flex flex-col items-center gap-3">
             <div className="h-24 w-24 rounded-full bg-white shadow-md flex items-center justify-center group-hover:bg-primary group-hover:text-white transition-all duration-300 border border-gray-100">
                <Watch className="h-10 w-10" />
             </div>
             <span className="font-semibold text-sm uppercase tracking-wide">Wearables</span>
          </Link>
          <Link href="/shop?category=accessories" className="group flex flex-col items-center gap-3">
             <div className="h-24 w-24 rounded-full bg-white shadow-md flex items-center justify-center group-hover:bg-primary group-hover:text-white transition-all duration-300 border border-gray-100">
                <Camera className="h-10 w-10" />
             </div>
             <span className="font-semibold text-sm uppercase tracking-wide">Cameras</span>
          </Link>
        </div>
      </section>

      {/* Featured Products */}
      <section className="container mx-auto px-4">
        <div className="flex items-center justify-between mb-8 border-b pb-4">
            <h2 className="text-2xl font-bold tracking-tight text-[#222] uppercase">Popular Products</h2>
            <div className="flex gap-4 text-sm font-medium text-muted-foreground">
                <Link href="/shop" className="hover:text-primary transition-colors">Best Seller</Link>
                <Link href="/shop" className="hover:text-primary transition-colors">Latest</Link>
            </div>
        </div>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {displayProducts.length === 0 ? (
                 <div className="col-span-full text-center py-20 bg-white rounded-lg border border-dashed">
                    <p className="text-muted-foreground text-lg">No products found. Please seed the database.</p>
                 </div>
            ) : (
                displayProducts.map((product) => (
                    <Link key={product.id} href={`/shop/${product.id}`} className="group h-full">
                        <Card className="flex flex-col h-full border-none shadow-sm hover:shadow-xl transition-all duration-300 bg-white rounded-lg overflow-hidden group-hover:-translate-y-1">
                            <div className="aspect-square relative p-6 flex items-center justify-center bg-gray-50 group-hover:bg-white transition-colors">
                                {product.image_url ? (
                                    <img 
                                        src={product.image_url} 
                                        alt={product.name}
                                        className="object-contain w-full h-full mix-blend-multiply group-hover:scale-110 transition-transform duration-500"
                                    />
                                ) : (
                                    <div className="flex items-center justify-center text-muted-foreground">
                                        No Image
                                    </div>
                                )}
                                {product.is_featured && (
                                    <div className="absolute top-3 left-3 bg-[#222] text-white text-[10px] font-bold px-2 py-1 uppercase tracking-wider">
                                        Hot
                                    </div>
                                )}
                            </div>
                            <CardContent className="p-5 flex-1 flex flex-col text-center">
                                <p className="text-xs text-muted-foreground uppercase tracking-wide mb-2">{product.category}</p>
                                <CardTitle className="line-clamp-1 text-base font-bold text-[#222] group-hover:text-primary transition-colors mb-2">{product.name}</CardTitle>
                                <div className="mt-auto pt-2">
                                    <span className="font-bold text-lg text-primary">${product.price.toFixed(2)}</span>
                                </div>
                            </CardContent>
                            <CardFooter className="p-4 pt-0">
                                <Button className="w-full font-bold uppercase tracking-wide rounded-none opacity-0 group-hover:opacity-100 transition-opacity">
                                    Add To Cart
                                </Button>
                            </CardFooter>
                        </Card>
                    </Link>
                ))
            )}
        </div>
        
        <div className="flex justify-center mt-12 sm:hidden">
            <Button variant="outline" asChild className="w-full">
                <Link href="/shop">View All Products</Link>
            </Button>
        </div>
      </section>

      {/* Promo Banner */}
      <section className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-[#f0f0f0] p-8 rounded-lg flex items-center justify-between group cursor-pointer hover:shadow-md transition-shadow">
                <div>
                    <p className="text-primary font-bold uppercase tracking-wide text-sm mb-2">JBL Speakers</p>
                    <h3 className="text-2xl font-black text-[#222] mb-4">Enhance Your <br/>Listening Experience</h3>
                    <span className="underline decoration-2 underline-offset-4 font-bold text-sm group-hover:text-primary transition-colors">Shop Now</span>
                </div>
                <div className="h-32 w-32 bg-gray-300 rounded-full flex items-center justify-center">
                    <Headphones className="h-16 w-16 text-gray-500" />
                </div>
            </div>
            <div className="bg-[#f0f0f0] p-8 rounded-lg flex items-center justify-between group cursor-pointer hover:shadow-md transition-shadow">
                <div>
                    <p className="text-primary font-bold uppercase tracking-wide text-sm mb-2">New Cameras</p>
                    <h3 className="text-2xl font-black text-[#222] mb-4">Capture Every <br/>Moment</h3>
                    <span className="underline decoration-2 underline-offset-4 font-bold text-sm group-hover:text-primary transition-colors">Shop Now</span>
                </div>
                <div className="h-32 w-32 bg-gray-300 rounded-full flex items-center justify-center">
                    <Camera className="h-16 w-16 text-gray-500" />
                </div>
            </div>
        </div>
      </section>
    </div>
  );
}

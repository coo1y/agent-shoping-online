import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { Filter, SlidersHorizontal, Search } from "lucide-react";
import { getProducts } from "@/lib/api";

interface ShopPageProps {
  searchParams: Promise<{
    category?: string;
  }>;
}

export default async function ShopPage(props: ShopPageProps) {
  const searchParams = await props.searchParams;
  const products = await getProducts(searchParams.category);

  return (
    <div className="bg-[#f9f9f9] min-h-screen pb-20">
      {/* Page Header */}
      <div className="bg-white border-b border-gray-200 py-12 mb-8">
        <div className="container mx-auto px-4">
            <h1 className="text-4xl font-black tracking-tight text-[#222] uppercase mb-2">Shop Collection</h1>
            <p className="text-muted-foreground text-lg max-w-2xl">
                Find the best deals on premium electronics.
            </p>
        </div>
      </div>

      <div className="container mx-auto px-4">
        {/* Mobile Filter & Sort */}
        <div className="flex flex-col gap-4 md:hidden mb-6">
            <div className="flex items-center justify-between gap-3">
                <Sheet>
                    <SheetTrigger asChild>
                        <Button variant="outline" size="sm" className="h-10 flex-1">
                            <Filter className="mr-2 h-4 w-4" /> Filters
                        </Button>
                    </SheetTrigger>
                    <SheetContent side="left" className="w-[300px]">
                        {/* Mobile Filter Content */}
                        <div className="flex flex-col gap-6 py-6">
                            <div className="space-y-4">
                                <h3 className="font-bold text-lg uppercase tracking-wide border-b pb-2">Categories</h3>
                                <div className="flex flex-col gap-3">
                                    <Link href="/shop?category=phones" className="flex items-center gap-3 p-2 rounded-lg hover:bg-muted transition-colors">
                                        <input type="checkbox" checked={searchParams.category === 'phones'} readOnly className="rounded border-gray-300 h-4 w-4 accent-primary" /> 
                                        <span className="font-medium">Phones</span>
                                    </Link>
                                    <Link href="/shop?category=notebooks" className="flex items-center gap-3 p-2 rounded-lg hover:bg-muted transition-colors">
                                        <input type="checkbox" checked={searchParams.category === 'notebooks'} readOnly className="rounded border-gray-300 h-4 w-4 accent-primary" />
                                        <span className="font-medium">Notebooks</span>
                                    </Link>
                                    <Link href="/shop?category=accessories" className="flex items-center gap-3 p-2 rounded-lg hover:bg-muted transition-colors">
                                        <input type="checkbox" checked={searchParams.category === 'accessories'} readOnly className="rounded border-gray-300 h-4 w-4 accent-primary" />
                                        <span className="font-medium">Accessories</span>
                                    </Link>
                                    <Link href="/shop" className="text-sm text-primary hover:underline pt-2 pl-2">
                                        Reset Filters
                                    </Link>
                                </div>
                            </div>
                        </div>
                    </SheetContent>
                </Sheet>
                
                <div className="flex items-center gap-2 bg-white p-1 rounded-md border flex-1">
                    <span className="text-sm text-muted-foreground whitespace-nowrap pl-3 font-medium">Sort:</span>
                    <select className="h-8 bg-transparent text-sm font-medium focus:outline-none cursor-pointer w-full">
                        <option value="featured">Featured</option>
                        <option value="newest">Newest</option>
                        <option value="price-asc">Price: Low to High</option>
                        <option value="price-desc">Price: High to Low</option>
                    </select>
                </div>
            </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-[260px_1fr] gap-10">
            {/* Sidebar Filters (Desktop) */}
            <div className="hidden md:block space-y-8 sticky top-36 self-start h-fit bg-white p-6 rounded-lg shadow-sm border border-gray-100">
            <div className="space-y-4">
                <h3 className="font-black text-lg flex items-center gap-2 uppercase tracking-wide text-[#222]">
                    <SlidersHorizontal className="h-5 w-5 text-primary" /> Filters
                </h3>
                <Separator className="bg-gray-100" />
            </div>
            
            <div className="space-y-4">
                <h4 className="font-bold text-sm uppercase tracking-wider text-muted-foreground">Categories</h4>
                <div className="flex flex-col gap-2">
                    <Link href="/shop?category=phones" className="flex items-center gap-3 p-2 -mx-2 rounded-md hover:bg-gray-50 transition-colors group cursor-pointer">
                        <div className={`h-4 w-4 rounded border flex items-center justify-center transition-colors ${searchParams.category === 'phones' ? 'bg-primary border-primary' : 'border-gray-300 group-hover:border-primary'}`}>
                            {searchParams.category === 'phones' && <div className="h-2 w-2 bg-black rounded-sm" />}
                        </div>
                        <span className={`text-sm font-medium ${searchParams.category === 'phones' ? 'text-black' : 'text-gray-600 group-hover:text-black'}`}>Phones</span>
                    </Link>
                    <Link href="/shop?category=notebooks" className="flex items-center gap-3 p-2 -mx-2 rounded-md hover:bg-gray-50 transition-colors group cursor-pointer">
                        <div className={`h-4 w-4 rounded border flex items-center justify-center transition-colors ${searchParams.category === 'notebooks' ? 'bg-primary border-primary' : 'border-gray-300 group-hover:border-primary'}`}>
                            {searchParams.category === 'notebooks' && <div className="h-2 w-2 bg-black rounded-sm" />}
                        </div>
                        <span className={`text-sm font-medium ${searchParams.category === 'notebooks' ? 'text-black' : 'text-gray-600 group-hover:text-black'}`}>Notebooks</span>
                    </Link>
                    <Link href="/shop?category=accessories" className="flex items-center gap-3 p-2 -mx-2 rounded-md hover:bg-gray-50 transition-colors group cursor-pointer">
                        <div className={`h-4 w-4 rounded border flex items-center justify-center transition-colors ${searchParams.category === 'accessories' ? 'bg-primary border-primary' : 'border-gray-300 group-hover:border-primary'}`}>
                            {searchParams.category === 'accessories' && <div className="h-2 w-2 bg-black rounded-sm" />}
                        </div>
                        <span className={`text-sm font-medium ${searchParams.category === 'accessories' ? 'text-black' : 'text-gray-600 group-hover:text-black'}`}>Accessories</span>
                    </Link>
                    {searchParams.category && (
                        <Link href="/shop" className="text-xs text-primary hover:underline pt-2 font-bold uppercase">
                            Clear Filters
                        </Link>
                    )}
                </div>
            </div>
            
            <Separator className="bg-gray-100" />
            
            <div className="space-y-4">
                <h4 className="font-bold text-sm uppercase tracking-wider text-muted-foreground">Price Range</h4>
                <div className="grid grid-cols-2 gap-3">
                    <div className="space-y-1.5">
                        <Label htmlFor="min-price" className="text-xs font-bold text-gray-500">MIN</Label>
                        <Input id="min-price" type="number" placeholder="0" className="h-9 bg-gray-50 border-gray-200" />
                    </div>
                    <div className="space-y-1.5">
                        <Label htmlFor="max-price" className="text-xs font-bold text-gray-500">MAX</Label>
                        <Input id="max-price" type="number" placeholder="9999" className="h-9 bg-gray-50 border-gray-200" />
                    </div>
                </div>
                <Button className="w-full font-bold uppercase tracking-wide" size="sm">Filter</Button>
            </div>
            </div>

            {/* Product Grid */}
            <div className="flex flex-col gap-6">
                <div className="hidden md:flex items-center justify-between bg-white p-4 rounded-lg border border-gray-100 shadow-sm">
                    <span className="font-bold text-gray-500 text-sm">{products.length} Products Found</span>
                    <div className="flex items-center gap-2">
                        <span className="text-sm font-bold text-gray-500 mr-2">Sort By:</span>
                        <select className="h-9 rounded-md border border-gray-200 bg-gray-50 px-3 text-sm font-medium focus:outline-none">
                            <option value="featured">Featured</option>
                            <option value="newest">Newest</option>
                            <option value="price-asc">Price: Low to High</option>
                            <option value="price-desc">Price: High to Low</option>
                        </select>
                    </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                    {products.length === 0 ? (
                        <div className="col-span-full flex flex-col items-center justify-center py-20 text-center bg-white rounded-xl border border-dashed border-gray-300">
                            <div className="bg-gray-100 h-16 w-16 rounded-full flex items-center justify-center mb-4">
                                <Search className="h-8 w-8 text-gray-400" />
                            </div>
                            <h3 className="text-xl font-bold mb-2">No products found</h3>
                            <p className="text-muted-foreground mb-6 max-w-sm">We couldn&apos;t find any products matching your current filters.</p>
                            <Button asChild variant="outline">
                                <Link href="/shop">Clear Filters</Link>
                            </Button>
                        </div>
                    ) : (
                        products.map((product) => (
                            <Link key={product.id} href={`/shop/${product.id}`} className="group">
                                <Card className="flex flex-col h-full border-none shadow-sm hover:shadow-xl transition-all duration-300 hover:-translate-y-1 bg-white rounded-lg overflow-hidden group">
                                    <div className="aspect-[4/3] relative bg-gray-50 overflow-hidden flex items-center justify-center p-6">
                                        {product.image_url ? (
                                            <img 
                                                src={product.image_url} 
                                                alt={product.name}
                                                className="object-contain w-full h-full mix-blend-multiply group-hover:scale-110 transition-transform duration-500 ease-out"
                                            />
                                        ) : (
                                            <div className="absolute inset-0 flex items-center justify-center text-muted-foreground bg-gray-100">
                                                No Image
                                            </div>
                                        )}
                                        {product.is_featured && (
                                            <div className="absolute top-3 left-3 bg-[#222] text-white text-[10px] font-bold px-2 py-1 uppercase tracking-wider shadow-sm">
                                                Hot
                                            </div>
                                        )}
                                    </div>
                                    <CardHeader className="p-5 pb-2">
                                        <p className="text-xs text-muted-foreground uppercase tracking-wide font-medium mb-1">{product.category}</p>
                                        <CardTitle className="line-clamp-1 text-base font-bold text-[#222] group-hover:text-primary transition-colors">{product.name}</CardTitle>
                                    </CardHeader>
                                    <CardContent className="p-5 pt-0 flex-1">
                                        <p className="text-sm text-gray-500 line-clamp-2 leading-relaxed">
                                            {product.description}
                                        </p>
                                    </CardContent>
                                    <CardFooter className="p-5 pt-0 flex items-center justify-between mt-auto">
                                        <span className="font-bold text-lg text-primary">${product.price.toFixed(2)}</span>
                                        <Button size="sm" className="rounded-none font-bold uppercase tracking-wide opacity-0 group-hover:opacity-100 transition-all transform translate-y-2 group-hover:translate-y-0">
                                            Add
                                        </Button>
                                    </CardFooter>
                                </Card>
                            </Link>
                        ))
                    )}
                </div>
            </div>
        </div>
      </div>
    </div>
  );
}

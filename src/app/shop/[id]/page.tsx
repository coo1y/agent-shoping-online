import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";
import { getProduct } from "@/lib/api";
import { AddToCartButton } from "@/components/products/AddToCartButton";
import { Separator } from "@/components/ui/separator";

export const dynamic = 'force-dynamic';
export const dynamicParams = true;

type Props = {
  params: Promise<{ id: string }>;
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
};

export default async function ProductDetailPage(props: Props) {
  const params = await props.params;
  const id = params.id;
  
  console.log(`[ProductPage] Rendering for ID: ${id}`);

  const product = await getProduct(id);

  if (!product) {
    return (
      <div className="container mx-auto px-4 py-20 text-center">
        <div className="inline-block bg-red-100 text-red-800 px-4 py-2 rounded-full font-bold mb-6">
            DEBUG: CONNECTION FAILED
        </div>
        <h1 className="text-3xl font-bold text-[#222] mb-4">Product Not Found</h1>
        <div className="bg-gray-100 p-6 rounded-lg max-w-2xl mx-auto text-left">
            <p className="mb-2"><strong>Requested ID:</strong> {id}</p>
            <p className="mb-4"><strong>Troubleshooting:</strong></p>
            <ul className="list-disc pl-5 space-y-2 mb-6">
                <li>Ensure backend is running on port 8000</li>
                <li>Ensure you have seeded the database</li>
                <li>Try refreshing this page</li>
            </ul>
            <div className="text-center">
                <Button asChild>
                    <Link href="/shop">Back to Shop</Link>
                </Button>
            </div>
        </div>
      </div>
    );
  }

  // If product exists, render the full UI
  return (
    <div className="bg-[#f9f9f9] min-h-screen py-12">
      <div className="container mx-auto px-4">
        {/* System Status Indicator - Temporary for debugging */}
        <div className="fixed bottom-4 right-4 bg-green-500 text-white text-xs font-bold px-3 py-1 rounded-full shadow-lg z-50 flex items-center gap-2">
            <span className="w-2 h-2 bg-white rounded-full animate-pulse"></span>
            System Online
        </div>

        <nav className="flex items-center text-sm text-muted-foreground mb-8">
            <Link href="/shop" className="hover:text-primary transition-colors flex items-center gap-1 font-medium">
                <ArrowLeft className="h-4 w-4" /> Back to Shop
            </Link>
            <span className="mx-2 text-gray-300">/</span>
            <span className="capitalize text-[#222] font-bold">{product.name}</span>
        </nav>

        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 md:p-10">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-12 lg:gap-16">
                <div className="space-y-4">
                    <div className="aspect-[4/3] bg-gray-50 rounded-lg flex items-center justify-center overflow-hidden relative group border border-gray-100">
                        {product.image_url ? (
                            <img 
                                src={product.image_url} 
                                alt={product.name} 
                                className="object-contain w-full h-full mix-blend-multiply p-8" 
                            />
                        ) : (
                            <span className="text-muted-foreground">No Image</span>
                        )}
                    </div>
                </div>

                <div className="flex flex-col gap-8">
                    <div className="relative">
                        <h1 className="text-3xl md:text-4xl font-black tracking-tight text-[#222] mb-3">{product.name}</h1>
                        <div className="relative inline-block mt-4">
                            {/* Decorative background */}
                            <div 
                                className="absolute inset-0 z-0 rounded-2xl"
                                style={{
                                    backgroundImage: `url(${product.image_url})`,
                                    backgroundSize: 'cover',
                                    backgroundPosition: 'center',
                                    width: '140%',
                                    height: '140%',
                                    top: '-20%',
                                    left: '-20%',
                                    filter: 'blur(12px)',
                                    opacity: 0.8,
                                }}
                            />
                            {/* Fallback/Base color to ensure visibility */}
                            <div className="absolute inset-0 z-[-1] bg-gradient-to-br from-blue-50 to-purple-50 rounded-2xl transform scale-125" />
                            
                            {/* Price text */}
                            <div className="relative z-10">
                                <p className="text-5xl font-black text-primary px-8 py-4 bg-white/90 rounded-2xl shadow-xl border border-white/50 backdrop-blur-sm">
                                    ${product.price.toFixed(2)}
                                </p>
                            </div>
                        </div>
                    </div>

                    <Separator />

                    <div className="space-y-4">
                        <h3 className="font-bold">Specs:</h3>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
                            {product.specs && Object.entries(product.specs).map(([key, value]) => (
                                <div key={key} className="flex justify-between border-b pb-1">
                                    <span className="font-medium capitalize text-gray-600">{key.replace(/_/g, ' ')}:</span>
                                    <span>{String(value)}</span>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="pt-4">
                        <AddToCartButton product={product} size="lg" className="w-full sm:w-auto text-base font-bold uppercase" />
                    </div>
                </div>
            </div>
        </div>
      </div>
    </div>
  );
}

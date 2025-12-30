import Link from "next/link"
import { Github, Twitter, Instagram } from "lucide-react"

export function Footer() {
  return (
    <footer className="bg-[#222222] text-white pt-16 pb-8 border-t-4 border-primary">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-12">
          <div className="md:col-span-2 space-y-4 pr-8">
            <h3 className="font-extrabold text-2xl tracking-tight text-white">Tech<span className="text-primary">Shop.</span></h3>
            <p className="text-gray-400 max-w-sm leading-relaxed text-sm">
              Your one-stop destination for premium electronics. We bring you the latest gadgets with unbeatable deals and top-notch customer service.
            </p>
          </div>
          
          <div className="space-y-4">
            <h4 className="font-bold text-sm uppercase tracking-wider text-primary">Shop</h4>
            <ul className="space-y-2 text-sm text-gray-300">
              <li><Link href="/shop" className="hover:text-primary transition-colors">All Products</Link></li>
              <li><Link href="/shop?category=notebooks" className="hover:text-primary transition-colors">Notebooks</Link></li>
              <li><Link href="/shop?category=phones" className="hover:text-primary transition-colors">Phones</Link></li>
              <li><Link href="/shop?category=accessories" className="hover:text-primary transition-colors">Accessories</Link></li>
            </ul>
          </div>
          
          <div className="space-y-4">
            <h4 className="font-bold text-sm uppercase tracking-wider text-primary">Company</h4>
            <ul className="space-y-2 text-sm text-gray-300">
              <li><Link href="#" className="hover:text-primary transition-colors">About Us</Link></li>
              <li><Link href="#" className="hover:text-primary transition-colors">Terms of Service</Link></li>
              <li><Link href="#" className="hover:text-primary transition-colors">Privacy Policy</Link></li>
              <li><Link href="#" className="hover:text-primary transition-colors">Contact Support</Link></li>
            </ul>
          </div>
        </div>
        
        <div className="pt-8 border-t border-gray-800 flex flex-col md:flex-row items-center justify-between gap-4">
          <p className="text-center text-xs text-gray-500 md:text-left">
            © {new Date().getFullYear()} TechShop. All rights reserved.
          </p>
          
          <div className="flex items-center gap-4">
            <Link href="#" className="text-gray-400 hover:text-primary transition-colors bg-gray-800 p-2 rounded-full hover:bg-gray-700">
              <Github className="h-4 w-4" />
              <span className="sr-only">GitHub</span>
            </Link>
            <Link href="#" className="text-gray-400 hover:text-primary transition-colors bg-gray-800 p-2 rounded-full hover:bg-gray-700">
              <Twitter className="h-4 w-4" />
              <span className="sr-only">Twitter</span>
            </Link>
            <Link href="#" className="text-gray-400 hover:text-primary transition-colors bg-gray-800 p-2 rounded-full hover:bg-gray-700">
              <Instagram className="h-4 w-4" />
              <span className="sr-only">Instagram</span>
            </Link>
          </div>
        </div>
      </div>
    </footer>
  )
}

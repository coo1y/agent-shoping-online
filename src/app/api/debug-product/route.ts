
import { NextResponse } from 'next/server';
import { getProduct } from '@/lib/api';

const BACKEND_URL =
  process.env.BACKEND_URL ?? process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://127.0.0.1:8000";

export const dynamic = 'force-dynamic';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const id = searchParams.get('id');

  if (!id) {
    return NextResponse.json({ error: 'Missing id parameter' }, { status: 400 });
  }

  try {
    console.log(`[DebugRoute] Fetching product ${id}...`);
    const product = await getProduct(id);
    
    if (product) {
      return NextResponse.json({ 
        status: 'success', 
        message: 'Product found', 
        product 
      });
    } else {
      return NextResponse.json({ 
        status: 'error', 
        message: 'Product not found (getProduct returned null)',
        backend_url: `${BACKEND_URL.replace(/\/$/, "")}/api/products/${id}`
      }, { status: 404 });
    }
  } catch (error: any) {
    return NextResponse.json({ 
      status: 'error', 
      message: error.message,
      stack: error.stack
    }, { status: 500 });
  }
}

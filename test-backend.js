
async function testConnection() {
    const url = 'http://127.0.0.1:8000/api/products/PHN-APL-IPH15P';
    console.log(`Testing connection to: ${url}`);
    
    try {
        const res = await fetch(url);
        console.log(`Status: ${res.status}`);
        if (res.ok) {
            const data = await res.json();
            console.log('Success! Data received:');
            console.log('Name:', data.name);
            console.log('ID:', data.product_id);
        } else {
            console.log('Failed status:', res.statusText);
        }
    } catch (error) {
        console.error('Connection failed:', error.message);
        if (error.cause) console.error('Cause:', error.cause);
    }
}

testConnection();

import mongoose from "mongoose";

const MONGODB_URI = process.env.MONGO_URI as string;

if(!MONGODB_URI) throw new Error("Please define the MONGO_URI environment variable inside .env.local");

let isConnected = false;

export async function connectDB(){
    if(isConnected) return;
    try {
        const db = await mongoose.connect(MONGODB_URI);
        isConnected = true;
        console.log("MongoDB Connected: ",db.connection.host);
    }catch (err){
        // Provide a clearer, actionable message for common DNS / SRV failures
        console.log("DB Connection error: ", err);

        try {
            const safeUri = MONGODB_URI
                ? MONGODB_URI.replace(/(mongodb\+srv:\/\/)([^@\s]+@)?([^/\s]+)/, '$1$2<host>')
                : '<not set>';
            console.log(`Current MONGO_URI (masked): ${safeUri}`);
        } catch (_) {
            // ignore masking errors
        }

        // Common helpful hint for ENOTFOUND / querySrv failures
        // This usually means the SRV DNS lookup failed (e.g. bad host, placeholder like 'xxxxx', or network/DNS issues).
        // If you're using an Atlas connection string (mongodb+srv://...), ensure the host is correct and your network/DNS can resolve it.
        if ((err as any)?.code === 'ENOTFOUND' || (err as any)?.message?.includes('querySrv')) {
            console.log('\nHint: DNS lookup for the SRV record failed.');
            console.log(" - Verify your MONGO_URI in .env.local and replace any 'xxxxx' placeholders with your actual cluster host.");
            console.log(" - If using mongodb+srv://, ensure your network/DNS allows SRV lookups (some corporate networks block them).");
            console.log(" - You can test SRV resolution with: dig +short SRV _mongodb._tcp.<your-cluster-host>");
            console.log(" - Alternatively try a standard connection string (mongodb://host:port) to bypass SRV while debugging.");
        }

        throw err;
    }
}


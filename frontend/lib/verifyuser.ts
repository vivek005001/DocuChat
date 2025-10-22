import jwt from "jsonwebtoken";
import {cookies} from "next/headers";

const JWT_SECRET = process.env.JWT_SECRET as string;

export async function verifyUser(){
    try{
        console.log("JWT_SECRET exists:", !!JWT_SECRET);
        
        const cookieStore = await cookies();
        const token = cookieStore.get("token")?.value;
        console.log("Token exists:", !!token);
        
        if(!token) {
            console.log("No token found in cookies");
            return null;
        }

        const decoded = jwt.verify(token, JWT_SECRET) as {id:string};
        console.log("Token verified successfully, user ID:", decoded.id);
        return decoded.id;
    } catch(err){
        console.error("Token verification error:", err);
        return null;
    }

}
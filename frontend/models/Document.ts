import { timeStamp } from "console";
import mongoose, {Schema, Document as DocType, mongo} from "mongoose";

export interface IDocument extends DocType {
    user: mongoose.Schema.Types.ObjectId;
    filename : string;
    filepath: string;
    mimetype: string;
    uploadedAt : Date;
    vectorId?: string; // ID reference in the vector store
}


const documentSchema = new Schema<IDocument>({
    user : {type: mongoose.Schema.Types.ObjectId, ref: "User", required: true},
    filename: {type: String, required:true},
    filepath: {type: String, required:true},
    mimetype: {type: String, required:true},
    uploadedAt: {type: Date, default: Date.now},
    vectorId: {type: String}, // Document ID in vector store
}, 

    {timestamps: true}

);
const Document = mongoose.models.Document || mongoose.model<IDocument> ("Document", documentSchema);

export default Document;
import { getUser } from "../../lib/db";

export default async function handler(req, res) {
    if (req.method === "POST") {
        const { username, password } = req.body;
        const user = await getUser(username, password);

        if (user) {
            res.status(200).json({ message: "Login successful" });
        } else {
            res.status(401).json({ message: "Invalid username or password" });
        }
    } else {
        res.status(405).json({ message: "Method not allowed" });
    }
}

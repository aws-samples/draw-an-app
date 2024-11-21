"use client";
import { useState } from "react";
import styles from "./OrderForm.module.css";

export default function OrderForm({ onSubmit }) {
    const [formData, setFormData] = useState({
        name: "",
        email: ""
    });

    const handleSubmit = (e) => {
        e.preventDefault();
        onSubmit(formData);
    };

    return (
        <form className={styles.form} onSubmit={handleSubmit}>
            <input
                type="text"
                placeholder="Name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
            />
            <input
                type="email"
                placeholder="Email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                required
            />
            <button type="submit">Submit</button>
        </form>
    );
}

"use client";
import { useState } from "react";
import styles from "./page.module.css";
import OrderForm from "./components/OrderForm";
import OrderDetails from "./components/OrderDetails";
import ThankYou from "./components/ThankYou";

export default function Home() {
    const [step, setStep] = useState(1);
    const [order, setOrder] = useState(null);

    const handleSubmit = async (formData) => {
        try {
            const response = await fetch("/api/orders", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(formData),
            });
            const data = await response.json();
            setOrder(data);
            setStep(2);
        } catch (error) {
            console.error("Error creating order:", error);
        }
    };

    const handleEdit = async (orderId, updates) => {
        try {
            const response = await fetch(`/api/orders/${orderId}`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(updates),
            });
            const data = await response.json();
            setOrder(data);
        } catch (error) {
            console.error("Error updating order:", error);
        }
    };

    const handleCancel = async (orderId) => {
        try {
            await fetch(`/api/orders/${orderId}`, {
                method: "DELETE",
            });
            setStep(1);
            setOrder(null);
        } catch (error) {
            console.error("Error canceling order:", error);
        }
    };

    return (
        <div className={styles.page}>
            <main className={styles.main}>
                {step === 1 && <OrderForm onSubmit={handleSubmit} />}
                {step === 2 && (
                    <OrderDetails
                        order={order}
                        onEdit={handleEdit}
                        onCancel={handleCancel}
                        onContinue={() => setStep(3)}
                    />
                )}
                {step === 3 && <ThankYou />}
            </main>
        </div>
    );
}

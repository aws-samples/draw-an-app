"use client";
import { useState } from "react";
import styles from "./page.module.css";
import LoginForm from "./components/LoginForm";
import OrderConfirm from "./components/OrderConfirm";
import OrderDetails from "./components/OrderDetails";
import ThankYou from "./components/ThankYou";

export default function Home() {
    const [screen, setScreen] = useState("login");
    const [order, setOrder] = useState(null);

    const handleLogin = async (name, pwd) => {
        const res = await fetch("/api/login", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({name, pwd})
        });
        if(res.ok) {
            setScreen("orderConfirm");
        }
    };

    const handleOrder = async (details) => {
        const res = await fetch("/api/order", {
            method: "POST", 
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(details)
        });
        const data = await res.json();
        setOrder(data);
        setScreen("orderDetails");
    };

    const handlePrint = async () => {
        await fetch(`/api/order/${order.id}/print`, {method: "POST"});
    };

    const handleCancel = async () => {
        await fetch(`/api/order/${order.id}/cancel`, {method: "POST"});
        setScreen("thankYou");
    };

    return (
        <div className={styles.container}>
            {screen === "login" && <LoginForm onSubmit={handleLogin} />}
            {screen === "orderConfirm" && <OrderConfirm onSubmit={handleOrder} />}
            {screen === "orderDetails" && 
                <OrderDetails 
                    order={order}
                    onPrint={handlePrint}
                    onCancel={handleCancel}
                />}
            {screen === "thankYou" && <ThankYou />}
        </div>
    );
}

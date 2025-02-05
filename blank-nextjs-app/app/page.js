"use client"

import { useState } from "react";
import LoginForm from "./components/LoginForm";
import OrderForm from "./components/OrderForm";
import OrderSummary from "./components/OrderSummary";
import ThankYou from "./components/ThankYou";

export default function Home() {
  const [step, setStep] = useState("login");
  const [orders, setOrders] = useState([]);

  const handleLogin = (data) => {
    setStep("order");
  };

  const handleOrderSubmit = (orderData) => {
    if (orderData) {
      setOrders([...orders, orderData]);
    } else {
      setStep("summary");
    }
  };

  const handleEdit = () => {
    setStep("order");
  };

  const handleConfirm = () => {
    setStep("thank-you");
  };

  return (
    <main>
      {step === "login" && <LoginForm onLogin={handleLogin} />}
      {step === "order" && <OrderForm onSubmit={handleOrderSubmit} />}
      {step === "summary" && (
        <OrderSummary 
          orders={orders}
          onEdit={handleEdit}
          onConfirm={handleConfirm}
        />
      )}
      {step === "thank-you" && <ThankYou />}
    </main>
  );
}
"use client"

import { useState } from 'react';
import OrderForm from './components/OrderForm';
import OrderConfirmation from './components/OrderConfirmation';
import OrderDetails from './components/OrderDetails';
import ThankYou from './components/ThankYou';
import styles from './page.module.css';

export default function Home() {
  const [step, setStep] = useState(1);
  const [order, setOrder] = useState(null);

  const handleFormSubmit = async (data) => {
    // Simulate API call
    const mockOrder = {
      id: 'ORD-' + Math.random().toString(36).substr(2, 9),
      value: 1000,
      count: 10,
      delivery: '10th Dec'
    };
    setOrder(mockOrder);
    setStep(2);
  };

  const renderStep = () => {
    switch(step) {
      case 1:
        return <OrderForm onSubmit={handleFormSubmit} />;
      case 2:
        return <OrderConfirmation order={order} onNext={() => setStep(3)} />;
      case 3:
        return (
          <OrderDetails 
            order={order}
            onContinue={() => setStep(4)}
            onCancel={() => setStep(1)}
          />
        );
      case 4:
        return <ThankYou />;
      default:
        return <OrderForm onSubmit={handleFormSubmit} />;
    }
  };

  return (
    <div className={styles.container}>
      <main className={styles.main}>
        {renderStep()}
      </main>
    </div>
  );
}
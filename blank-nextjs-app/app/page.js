"use client";

import { useState } from 'react';
import styles from './page.module.css';

export default function Home() {
    const [step, setStep] = useState(1);
    const [formData, setFormData] = useState({
        name: '',
        password: ''
    });

    const handleSubmit = (e) => {
        e.preventDefault();
        setStep(2);
    };

    const handleConfirm = () => {
        setStep(4);
    };

    const handleDetails = () => {
        setStep(3);
    };

    const renderStep = () => {
        switch(step) {
            case 1:
                return (
                    <div className={styles.formCard}>
                        <h2>Login</h2>
                        <form onSubmit={handleSubmit}>
                            <input 
                                type="text" 
                                placeholder="Name"
                                value={formData.name}
                                onChange={(e) => setFormData({...formData, name: e.target.value})}
                                required
                            />
                            <input 
                                type="password" 
                                placeholder="Password"
                                value={formData.password}
                                onChange={(e) => setFormData({...formData, password: e.target.value})}
                                required
                            />
                            <button type="submit">Submit</button>
                        </form>
                    </div>
                );
            case 2:
                return (
                    <div className={styles.formCard}>
                        <h2>Thank you for logging in!</h2>
                        <div className={styles.orderSummary}>
                            <p>Your order:</p>
                            <p>Value: $1000</p>
                        </div>
                        <button onClick={handleDetails}>Check Order Details</button>
                    </div>
                );
            case 3:
                return (
                    <div className={styles.formCard}>
                        <h2>Order Details</h2>
                        <div className={styles.orderDetails}>
                            <p>Order ID: 12345</p>
                            <p>Value: $1000</p>
                            <p>Count: 10</p>
                            <p>Delivery: 10th Dec</p>
                        </div>
                        <div className={styles.buttonGroup}>
                            <button onClick={handleConfirm} className={styles.confirmBtn}>Confirm</button>
                            <button onClick={() => setStep(2)} className={styles.cancelBtn}>Cancel</button>
                        </div>
                    </div>
                );
            case 4:
                return (
                    <div className={styles.formCard}>
                        <h2>Thank You!</h2>
                        <p>Your order has been confirmed.</p>
                    </div>
                );
        }
    };

    return (
        <div className={styles.container}>
            {renderStep()}
        </div>
    );
}

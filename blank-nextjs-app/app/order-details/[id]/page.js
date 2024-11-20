'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import styles from './page.module.css';

export default function OrderDetails({ params }) {
    const router = useRouter();
    const [orderDetails] = useState({
        orderId: params.id,
        value: 4000,
        count: 10,
        delivery: '10th Dec'
    });

    const handleConfirm = async () => {
        const response = await fetch('/api/orders', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(orderDetails)
        });
        if (response.ok) {
            router.push('/thank-you');
        }
    };

    return (
        <div className={styles.detailsContainer}>
            <h2>Order Details</h2>
            <div className={styles.details}>
                <p>Order ID: {orderDetails.orderId}</p>
                <p>Value: ${orderDetails.value}</p>
                <p>Count: {orderDetails.count}</p>
                <p>Delivery: {orderDetails.delivery}</p>
            </div>
            <div className={styles.buttons}>
                <button onClick={handleConfirm}>Confirm</button>
                <button onClick={() => router.back()}>Cancel</button>
            </div>
        </div>
    );
}
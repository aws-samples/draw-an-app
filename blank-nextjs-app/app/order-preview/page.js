'use client';
import { useEffect, useState } from 'react';
import Link from 'next/link';
import styles from './page.module.css';

export default function OrderPreview() {
    const [orderValue, setOrderValue] = useState(0);

    useEffect(() => {
        // Simulate fetching order value
        setOrderValue(4000);
    }, []);

    return (
        <div className={styles.previewContainer}>
            <h2>Thanks for logging in</h2>
            <p>Your order value: ${orderValue}</p>
            <Link href="/order-details/123" className={styles.checkOrder}>
                Check order id
            </Link>
        </div>
    );
}
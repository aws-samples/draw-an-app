"use client"

import styles from './OrderConfirmation.module.css';

export default function OrderConfirmation({ order, onNext }) {
  return (
    <div className={styles.confirmation}>
      <h2>Thank you for logging in</h2>
      <div className={styles.orderSummary}>
        <p>Your Order:</p>
        <p>Order value: ${order.value}</p>
      </div>
      <button onClick={onNext} className={styles.button}>Check Order Details</button>
    </div>
  );
}
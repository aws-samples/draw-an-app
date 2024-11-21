"use client";
import styles from "./OrderConfirm.module.css";

export default function OrderConfirm({onSubmit}) {
    return (
        <div className={styles.container}>
            <h2>Thank you for logging in</h2>
            <p>Your order:</p>
            <button onClick={() => onSubmit({value: 4000, count: 10, delivery: "10 days"})}>Confirm Order</button>
        </div>
    );
}

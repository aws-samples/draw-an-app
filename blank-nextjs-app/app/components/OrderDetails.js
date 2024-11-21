"use client";
import styles from "./OrderDetails.module.css";

export default function OrderDetails({order, onPrint, onCancel}) {
    return (
        <div className={styles.container}>
            <h3>Order Details</h3>
            <div className={styles.details}>
                <p>Order ID: {order.id}</p>
                <p>Value: ${order.value}</p>
                <p>Count: {order.count}</p>
                <p>Delivery: {order.delivery}</p>
            </div>
            <div className={styles.buttons}>
                <button onClick={onPrint}>Print</button>
                <button onClick={onCancel}>Cancel</button>
            </div>
        </div>
    );
}

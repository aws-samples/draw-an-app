export default function OrderDetails({ order, onEdit, onCancel, onContinue }) {
    return (
        <div className={styles.orderDetails}>
            <h2>Order Details</h2>
            <div className={styles.details}>
                <p>Order ID: {order.id}</p>
                <p>Value: ${order.value}</p>
                <p>Count: {order.count}</p>
                <p>Delivery: {order.delivery} hrs</p>
            </div>
            <div className={styles.actions}>
                <button onClick={() => onEdit(order.id, order)}>Edit</button>
                <button onClick={() => onCancel(order.id)}>Cancel</button>
                <button onClick={onContinue}>Continue</button>
            </div>
        </div>
    );
}

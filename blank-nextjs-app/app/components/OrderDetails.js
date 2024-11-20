export default function OrderDetails({ order, onContinue, onCancel }) {
  return (
    <div className="order-details">
      <h2>Order Details</h2>
      <div className="details-container">
        <p>Order ID: {order.id}</p>
        <p>Value: ${order.value}</p>
        <p>Count: {order.count}</p>
        <p>Delivery: {order.delivery}</p>
      </div>
      <div className="button-group">
        <button onClick={onContinue}>Continue</button>
        <button onClick={onCancel}>Cancel</button>
      </div>
      <style jsx>{`
        .order-details {
          padding: 20px;
          border-radius: 8px;
          background: white;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .details-container {
          margin: 20px 0;
        }
        .button-group {
          display: flex;
          gap: 10px;
          justify-content: center;
        }
        button {
          padding: 8px 16px;
          border-radius: 4px;
          border: none;
          cursor: pointer;
        }
      `}</style>
    </div>
  );
}
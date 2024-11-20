export default function ThankYou() {
  return (
    <div className="thank-you">
      <h2>Thank You!</h2>
      <p>Your order has been processed successfully.</p>
      <style jsx>{`
        .thank-you {
          text-align: center;
          padding: 40px;
        }
        h2 {
          color: #2ecc71;
          margin-bottom: 16px;
        }
      `}</style>
    </div>
  );
}
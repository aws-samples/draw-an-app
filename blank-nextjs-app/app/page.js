'use client';
import styles from './page.module.css';
import { useState } from 'react';

export default function Home() {
  const [formData, setFormData] = useState({
    name: '',
    division: ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('/api/submit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });
      const data = await response.json();
      if (data.success) {
        alert('Data submitted successfully!');
        setFormData({ name: '', division: '' });
      } else {
        alert('Error: ' + data.message);
      }
    } catch (error) {
      alert('Error submitting form');
    }
  };

  return (
    <div className={styles.container}>
      <form className={styles.form} onSubmit={handleSubmit}>
        <div className={styles.formGroup}>
          <label className={styles.label}>NAME</label>
          <input
            type="text"
            className={styles.input}
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            required
          />
        </div>
        <div className={styles.formGroup}>
          <label className={styles.label}>Division</label>
          <input
            type="text"
            className={styles.input}
            value={formData.division}
            onChange={(e) => setFormData({ ...formData, division: e.target.value })}
            required
          />
        </div>
        <button type="submit" className={styles.submitButton}>SUBMIT</button>
      </form>
    </div>
  );
}
import Link from 'next/link';
import styles from './page.module.css';

export default function Home() {
    return (
        <div className={styles.page}>
            <main className={styles.main}>
                <h1>Welcome to Order System</h1>
                <Link href="/login" className={styles.loginButton}>
                    Start Ordering
                </Link>
            </main>
        </div>
    );
}
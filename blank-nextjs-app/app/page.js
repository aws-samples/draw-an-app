import Image from "next/image";
import styles from "./page.module.css";

export default function Home() {
    return (
        <div className={styles.page}>
            <main className={styles.main}>
                <div style={{ display: 'flex', flexDirection: 'row', alignItems: 'center' }}>
                    <Image
                        src="/board.png"
                        alt="board.png"
                        width={250}
                        height={400}
                        priority
                    />
                    <p style={{ fontSize: '3rem', margin: '50px' }}>
                        Draw an app
                    </p>
                </div>
            </main>
            <footer className={styles.footer}>

            </footer>
        </div>
    );
}

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
                    <div>
                        <p style={{ fontSize: '3rem', marginLeft: '50px' }}>
                            Draw an app
                        </p>
                        <p style={{ fontSize: '1rem', marginLeft: '50px', paddingBottom: '100px' }}>
                            - Sketch to reality
                        </p>
                    </div>
                </div>
            </main>
            <footer className={styles.footer}>

            </footer>
        </div>
    );
}

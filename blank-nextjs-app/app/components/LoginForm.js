"use client";
import styles from "./LoginForm.module.css";

export default function LoginForm({onSubmit}) {
    const handleSubmit = (e) => {
        e.preventDefault();
        const name = e.target.name.value;
        const pwd = e.target.pwd.value;
        onSubmit(name, pwd);
    };

    return (
        <form className={styles.form} onSubmit={handleSubmit}>
            <input type="text" name="name" placeholder="Name" required />
            <input type="password" name="pwd" placeholder="Password" required />
            <button type="submit">Submit</button>
        </form>
    );
}

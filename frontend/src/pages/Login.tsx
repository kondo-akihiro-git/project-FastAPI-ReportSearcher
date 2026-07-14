// frontend/src/pages/Login.tsx
import { useNavigate } from "react-router-dom";
import { Button, Container, Snackbar, TextField, Typography } from "@mui/material";
import { useState } from "react";


const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;
const isLocal = window.location.origin === import.meta.env.VITE_LOCALHOST_URL;

export default function Login() {
  const navigate = useNavigate();
  const [basicUsername, setBasicUsername] = useState(isLocal ? import.meta.env.VITE_BASIC_LOGIN_USERNAME : "");
  const [basicPassword, setBasicPassword] = useState(isLocal ? import.meta.env.VITE_BASIC_LOGIN_PASSWORD : "");
  const [portalUsername, setPortalUsername] = useState(isLocal ? import.meta.env.VITE_PORTAL_LOGIN_USERNAME : "");
  const [portalPassword, setPortalPassword] = useState(isLocal ? import.meta.env.VITE_PORTAL_LOGIN_PASSWORD : "");
  const [open, setOpen] = useState(false);

  const login = async () => {
    const res = await fetch(
      `${BACKEND_URL}/login`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          basic_username: basicUsername,
          basic_password: basicPassword,
          portal_username: portalUsername,
          portal_password: portalPassword
        })
      }
    );


    const data = await res.json();
    if (data.message === "login-test") {
      setOpen(true);

      setTimeout(() => {
        navigate("/search");
      }, 1000);
    }
  };


  return (
    <Container maxWidth="sm" sx={{ mt: 8 }}>
      <Typography variant="h4" gutterBottom>
        社内ポータル ログイン
      </Typography>


      <TextField
        label="Basic認証ID"
        fullWidth
        margin="normal"
        value={basicUsername}
        onChange={(e) => setBasicUsername(e.target.value)}
      />


      <TextField
        label="Basic認証Password"
        type="password"
        fullWidth
        margin="normal"
        value={basicPassword}
        onChange={(e) => setBasicPassword(e.target.value)}
      />


      <TextField
        label="ポータルID"
        fullWidth
        margin="normal"
        value={portalUsername}
        onChange={(e) => setPortalUsername(e.target.value)}
      />


      <TextField
        label="ポータルPassword"
        type="password"
        fullWidth
        margin="normal"
        value={portalPassword}
        onChange={(e) => setPortalPassword(e.target.value)}
      />


      <Button
        variant="contained"
        fullWidth
        sx={{ mt: 3 }}
        onClick={login}
      >
        保存
      </Button>


      <Snackbar
        open={open}
        autoHideDuration={3000}
        message="ログインしました"
      />

    </Container>
  );
}
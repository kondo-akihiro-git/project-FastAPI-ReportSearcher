// frontend/src/pages/Login.tsx
import { useNavigate } from "react-router-dom";
import { Box, Button, Container, LinearProgress, Snackbar, TextField, Typography } from "@mui/material";
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
  const [errorMessage, setErrorMessage] = useState("");
  const [loading, setLoading] = useState(false);

  // ログイン情報を保存してスクレイピング画面へ遷移する
  const login = async () => {
    setErrorMessage("");
    setLoading(true);

    try {
      const res = await fetch(`${BACKEND_URL}/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          basic_username: basicUsername,
          basic_password: basicPassword,
          portal_username: portalUsername,
          portal_password: portalPassword,
        }),
      });
      if (!res.ok) {
        const data = await res.json();
        setErrorMessage(data.detail ?? "ログインに失敗しました");
        return;
      }
      setOpen(true);
      setTimeout(() => {
        navigate("/scrape");
      }, 1000);
    } finally {
      setLoading(false);
    }
  };


  return (
    <Container maxWidth={false} sx={{ mt: 8, px: { xs: 2, sm: 4 } }}>
      <Typography variant="h4" gutterBottom>
        週報検索システム
      </Typography>
      <Typography color="text.secondary" sx={{ mb: 3 }}>
        ログインすると週報データを自動で集め、キーワード検索できるようになります。
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
      {errorMessage && (
        <Typography color="error.main" sx={{ mt: 2 }}>
          {errorMessage}
        </Typography>
      )}
      <Button
        variant="contained"
        fullWidth
        sx={{ mt: 3 }}
        onClick={login}
        disabled={loading}
      >
        {loading ? "ログイン中..." : "ログイン"}
      </Button>
      {loading && (
        <Box sx={{ mt: 3 }}>
          <LinearProgress />
        </Box>
      )}
      <Snackbar
        open={open}
        autoHideDuration={3000}
        message="ログインしました"
      />
    </Container>
  );
}
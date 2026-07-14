// frontend/src/pages/Login.tsx
import { useNavigate } from "react-router-dom";
import { Button, Container, TextField, Typography } from "@mui/material";

export default function Login() {
  const navigate = useNavigate();

  const login = async () => {
    const res = await fetch("http://127.0.0.1:8000/login", {
      method: "POST",
    });

    const data = await res.json();

    if (data.message === "login-test") {
      navigate("/search");
    }
  };

  return (
    <Container maxWidth="sm" sx={{ mt: 8 }}>
      <Typography variant="h4" gutterBottom>
        社内ポータル ログイン
      </Typography>

      <TextField
        fullWidth
        label="ユーザーID"
        margin="normal"
      />

      <TextField
        fullWidth
        label="パスワード"
        type="password"
        margin="normal"
      />

      <Button
        variant="contained"
        fullWidth
        sx={{ mt: 3 }}
        onClick={login}
      >
        保存
      </Button>
    </Container>
  );
}
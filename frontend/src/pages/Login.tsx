// frontend/src/pages/Login.tsx
import { Container, Typography, TextField, Button } from "@mui/material";

export default function Login() {
  return (
    <Container maxWidth="sm" sx={{ mt: 8 }}>
      <Typography variant="h4" gutterBottom>
        社内ポータル ログイン
      </Typography>

      <TextField
        label="ユーザーID"
        fullWidth
        margin="normal"
      />

      <TextField
        label="パスワード"
        type="password"
        fullWidth
        margin="normal"
      />

      <Button
        variant="contained"
        fullWidth
        sx={{ mt: 3 }}
      >
        保存
      </Button>
    </Container>
  );
}
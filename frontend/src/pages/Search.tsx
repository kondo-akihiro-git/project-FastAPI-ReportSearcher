// frontend/src/pages/Search.tsx
import { useState } from "react";
import {
  Button,
  Container,
  TextField,
  Typography,
} from "@mui/material";

export default function Search() {
  const [result, setResult] = useState("");

  const search = async () => {
    const res = await fetch("http://127.0.0.1:8000/search");

    const data = await res.json();

    setResult(data.message);
  };

  return (
    <Container maxWidth="md" sx={{ mt: 8 }}>
      <Typography variant="h4" gutterBottom>
        週報検索
      </Typography>

      <TextField
        fullWidth
        label="キーワード"
      />

      <Button
        variant="contained"
        sx={{ mt: 2 }}
        onClick={search}
      >
        検索
      </Button>

      <Typography sx={{ mt: 4 }}>
        {result}
      </Typography>
    </Container>
  );
}
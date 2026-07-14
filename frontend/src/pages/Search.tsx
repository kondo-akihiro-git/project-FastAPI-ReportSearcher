// frontend/src/pages/Search.tsx
import {
  Container,
  Typography,
  TextField,
  Button,
  Divider,
  List,
  ListItem,
  ListItemText,
} from "@mui/material";

export default function Search() {
  return (
    <Container maxWidth="md" sx={{ mt: 8 }}>
      <Typography variant="h4" gutterBottom>
        週報検索
      </Typography>

      <TextField
        label="キーワード"
        fullWidth
        margin="normal"
      />

      <Button
        variant="contained"
        sx={{ mt: 2, mb: 4 }}
      >
        検索
      </Button>

      <Typography variant="body2" gutterBottom>
        最終取得日時：2026/07/14 20:00
      </Typography>

      <Divider sx={{ my: 3 }} />

      <Typography variant="h6" gutterBottom>
        検索結果
      </Typography>

      <List>
        <ListItem divider>
          <ListItemText
            primary="React導入について"
            secondary="2026/07/13"
          />
        </ListItem>

        <ListItem divider>
          <ListItemText
            primary="FastAPIのAPI設計"
            secondary="2026/07/12"
          />
        </ListItem>

        <ListItem>
          <ListItemText
            primary="AWS Lambdaの調査"
            secondary="2026/07/11"
          />
        </ListItem>
      </List>
    </Container>
  );
}
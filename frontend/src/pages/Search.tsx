// frontend/src/pages/Search.tsx
import { useState } from "react";
import {
  Box,
  Button,
  Card,
  CardActionArea,
  CardContent,
  Container,
  Pagination,
  TextField,
  Typography,
} from "@mui/material";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;
const PAGE_SIZE = 5;

type Snippet = {
  prefix: string;
  match: string;
  suffix: string;
};

type ReportResult = {
  year_month: string;
  week_num: number;
  member_no: string;
  section: string;
  snippet: Snippet | null;
  url: string;
};

type SearchResponse = {
  items: ReportResult[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
};

export default function Search() {
  const [keyword, setKeyword] = useState("");
  const [results, setResults] = useState<ReportResult[]>([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [searched, setSearched] = useState(false);
  const [loading, setLoading] = useState(false);

  const fetchResults = async (targetPage: number) => {
    if (!keyword) return;

    setLoading(true);
    try {
      const params = new URLSearchParams({
        keyword,
        page: String(targetPage),
        page_size: String(PAGE_SIZE),
      });
      const res = await fetch(`${BACKEND_URL}/search?${params.toString()}`);
      const data: SearchResponse = await res.json();

      setResults(data.items);
      setTotalPages(data.total_pages);
      setPage(data.page);
      setSearched(true);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    fetchResults(1);
  };

  const handlePageChange = (_: React.ChangeEvent<unknown>, value: number) => {
    fetchResults(value);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <Container maxWidth={false} sx={{ mt: 8, px: { xs: 2, sm: 4 } }}>
      <Typography variant="h4" gutterBottom>
        週報検索
      </Typography>
      <Typography color="text.secondary" sx={{ mb: 2 }}>
        週報の中から関連する部分を一覧表示します。
      </Typography>
      <Box sx={{ display: "flex", gap: 1.5, alignItems: "flex-start" }}>
        <TextField
          fullWidth
          label="キーワード"
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSearch()}
        />
        <Button
          variant="contained"
          onClick={handleSearch}
          disabled={loading || !keyword}
          sx={{ height: 56, px: 4, flexShrink: 0 }}
        >
          検索
        </Button>
      </Box>

      <Box sx={{ mt: 4 }}>
        {results.length > 0 ? (
          <>
            {results.map((report, index) => (
              <Card key={index} sx={{ mt: 1.5 }}>
                <CardActionArea onClick={() => window.open(report.url, "_blank")}>
                  <CardContent sx={{ py: 1.2, "&:last-child": { pb: 1.2 } }}>
                    <Typography variant="subtitle1">
                      {report.year_month} 第{report.week_num}週 【{report.section}】
                    </Typography>

                    <Typography
                      variant="body2"
                      sx={{ mt: 0.5, color: "action.disabled" }}
                      noWrap
                    >
                      {report.snippet && (
                        <>
                          {report.snippet.prefix}
                          <Box
                            component="span"
                            sx={{
                              textDecoration: "underline",
                              fontWeight: "bold",
                              color: "text.secondary",
                            }}
                          >
                            {report.snippet.match}
                          </Box>
                          {report.snippet.suffix}
                        </>
                      )}
                    </Typography>
                  </CardContent>
                </CardActionArea>
              </Card>
            ))}

            {totalPages > 1 && (
              <Box sx={{ display: "flex", justifyContent: "center", mt: 3 }}>
                <Pagination
                  count={totalPages}
                  page={page}
                  onChange={handlePageChange}
                  color="primary"
                />
              </Box>
            )}
          </>
        ) : (
          searched &&
          !loading && (
            <Typography sx={{ mt: 4 }}>結果が見つかりませんでした。</Typography>
          )
        )}
      </Box>
    </Container>
  );
}
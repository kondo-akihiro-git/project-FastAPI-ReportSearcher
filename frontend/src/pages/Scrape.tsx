// frontend/src/pages/Scrape.tsx
import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Box,
  Button,
  Container,
  LinearProgress,
  Typography,
} from "@mui/material";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

type ScrapeStatus = {
  running: boolean;
  completed: boolean;
  success: boolean;
  log: string[];
};

export default function Scrape() {
  const navigate = useNavigate();

  const [status, setStatus] = useState<ScrapeStatus | null>(null);
  const [checking, setChecking] = useState(true);

  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const fetchStatus = async () => {
    const res = await fetch(`${BACKEND_URL}/scrape/status`);
    const data: ScrapeStatus = await res.json();
    setStatus(data);
    return data;
  };

  const startPolling = () => {
    if (pollingRef.current) return;

    pollingRef.current = setInterval(async () => {
      const data = await fetchStatus();

      if (!data.running && data.completed) {
        stopPolling();
      }
    }, 2000);
  };

  const stopPolling = () => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
      pollingRef.current = null;
    }
  };

  useEffect(() => {

    const checkExistingReports = async () => {

      const res = await fetch(
        `${BACKEND_URL}/scrape/check`
      );

        const data = await res.json();

      if (data.completed) {
        navigate("/search");
        return;
      }


      setChecking(false);


      const status = await fetchStatus();

      if (status.running) {
        startPolling();
      }
    };


    checkExistingReports();

    return () => stopPolling();

  }, []);


  const handleStart = async () => {
    const res = await fetch(
      `${BACKEND_URL}/scrape/start`,
      {
        method: "POST",
      }
    );

    const data: {
      status: "started" | "already_running";
    } = await res.json();


    if (data.status === "already_running") {
      startPolling();
      return;
    }


    await fetchStatus();
    startPolling();
  };


  const isRunning = status?.running ?? false;
  const isCompleted = status?.completed ?? false;
  const isSuccess = status?.success ?? false;


  // 取得済み確認中画面
  if (checking) {
    return (
      <Container maxWidth="md" sx={{ mt: 8 }}>
        <Typography variant="h4" gutterBottom>
          過去の週報を確認中
        </Typography>

        <Typography color="text.secondary">
          取得済みの週報データが存在するか確認しています。
        </Typography>

        <Box sx={{ mt: 3 }}>
          <LinearProgress />
        </Box>
      </Container>
    );
  }


  return (
    <Container maxWidth="md" sx={{ mt: 8 }}>
      <Typography variant="h4" gutterBottom>
        過去の週報を取得
      </Typography>


      <Typography color="text.secondary" sx={{ mb: 3 }}>
        検索を利用する前に、社内ポータルから週報データを取得しておく必要があります。
        取得には数分〜数十分かかる場合があります。
      </Typography>


      <Button
        variant="contained"
        onClick={handleStart}
        disabled={isRunning}
      >
        {isRunning ? "取得中..." : "取得を開始する"}
      </Button>


      {isRunning && (
        <Box sx={{ mt: 3 }}>
          <LinearProgress />
        </Box>
      )}


      {isCompleted && (
        <Box sx={{ mt: 3 }}>
          {isSuccess ? (
            <>
              <Typography color="success.main" sx={{ mb: 2 }}>
                取得が完了しました。検索画面に進めます。
              </Typography>

              <Button
                variant="contained"
                color="success"
                onClick={() => navigate("/search")}
              >
                検索画面へ進む
              </Button>
            </>
          ) : (
            <Typography color="error.main">
              取得中にエラーが発生しました。時間をおいて再度お試しください。
            </Typography>
          )}
        </Box>
      )}
    </Container>
  );
}
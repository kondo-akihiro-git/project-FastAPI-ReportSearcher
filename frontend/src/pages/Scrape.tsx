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
const MIN_CHECKING_MS = 3000; // 確認中画面を最低限表示する時間

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

  // スクレイピング状態を取得する
  const fetchStatus = async () => {
    const res = await fetch(`${BACKEND_URL}/scrape/status`);
    const data: ScrapeStatus = await res.json();
    setStatus(data);
    return data;
  };


  // スクレイピング状態の定期取得を開始する
  const startPolling = () => {
    if (pollingRef.current) return;
    pollingRef.current = setInterval(async () => {
      const data = await fetchStatus();
      if (!data.running && data.completed) {
        stopPolling();
      }
    }, 2000);
  };


  // スクレイピング状態の定期取得を停止する
  const stopPolling = () => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
      pollingRef.current = null;
    }
  };

  useEffect(() => {

    // 初回表示時に取得済み週報と実行状態を確認する（確認中画面は最低MIN_CHECKING_MSは表示する）
    const checkExistingReports = async () => {
      const startedAt = Date.now();
      const res = await fetch(`${BACKEND_URL}/scrape/check`);
      const data = await res.json();

      const elapsed = Date.now() - startedAt;
      const remaining = MIN_CHECKING_MS - elapsed;
      if (remaining > 0) {
        await new Promise((resolve) => setTimeout(resolve, remaining));
      }

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


  // スクレイピングを開始する
  const handleStart = async () => {
    const res = await fetch(`${BACKEND_URL}/scrape/start`, { method: "POST" });
    const data: { status: "started" | "already_running"; } = await res.json();
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
      <Container maxWidth={false} sx={{ mt: 8, px: { xs: 2, sm: 4 } }}>
        <Typography variant="h4" gutterBottom>
          過去の週報を確認中
        </Typography>
        <Typography color="text.secondary">
          すでに週報が集められているかどうかを確認しています。少しお待ちください。
        </Typography>
        <Box sx={{ mt: 3 }}>
          <LinearProgress />
        </Box>
      </Container>
    );
  }


  return (
    <Container maxWidth={false} sx={{ mt: 8, px: { xs: 2, sm: 4 } }}>
      <Typography variant="h4" gutterBottom>
        過去の週報を取得
      </Typography>

      {!isCompleted && (
        <>
          <Typography color="text.secondary" sx={{ mb: 3 }}>
            検索する前に週報データを収集できるか確認します。確認完了まで３分程度かかります。
          </Typography>
          <Button
            variant="contained"
            fullWidth
            onClick={handleStart}
            disabled={isRunning}
          >
            {isRunning ? "取得中..." : "取得を開始する"}
          </Button>
        </>
      )}
      {isRunning && !isCompleted && (
        <Box sx={{ mt: 3 }}>
          <LinearProgress />
        </Box>
      )}

      {isCompleted && (
        <Box>
          {isSuccess ? (
            <>
              <Typography color="success.main" sx={{ mb: 2 }}>
                検索可能と確認しました。検索画面はこちらです。
              </Typography>
              <Button
                variant="contained"
                color="success"
                fullWidth
                onClick={() => navigate("/search")}
              >
                検索画面へ進む
              </Button>
            </>
          ) : (
            <>
              <Typography color="error.main" sx={{ mb: 2 }}>
                取得中にエラーが発生しました。時間をおいて再度お試しください。
              </Typography>
              <Button variant="contained" fullWidth onClick={handleStart}>
                再度取得する
              </Button>
            </>
          )}
        </Box>
      )}
    </Container>
  );
}
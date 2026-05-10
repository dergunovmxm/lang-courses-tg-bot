import React, { useState, useEffect } from "react";
import { Typography, Space, Alert } from "antd";
import GrowthTimelineChart from "../../components/GrowthTimelineChart";
import type { Daily, Growth, Overview, Timeline } from "../../models/dashboard";
import Loader from "../../components/Loader";
import DailyStats from "../../components/DailyStats";
import OverviewStats from "../../components/OverviewStats";
import { LineChartOutlined } from "@ant-design/icons";
import GrowthStats from "../../components/GrowthStats";

const { Title } = Typography;

const Dashboard: React.FC = () => {
  const [timelineData, setTimelineData] = useState<Timeline[]>();
  const [overviewData, setOverviewData] = useState<Overview>();
  const [dailyData, setDailyData] = useState<Daily>();
  const [growthData, setGrowthData] = useState<Growth>();
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(
        // TODO: ПРОВЕРИТЬ
        // Было в ветке main
        // "http://localhost:3001/api/dashboard/summary",

        // Пришло из ветки task_level
        `${import.meta.env.VITE_API_URL || "http://localhost:3001"}/api/dashboard/summary`,
        {
          headers: {
            "Content-Type": "application/json",
          },
        },
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();

      if (result.success) {
        setTimelineData(result.data.timeline);
        setDailyData(result.data.daily);
        setOverviewData(result.data.overview);
        setGrowthData(result.data.growth);

        console.log("data", result.data);
      } else {
        throw new Error(result.message || "Failed to fetch data");
      }
    } catch (err) {
      console.error("Error fetching timeline data:", err);
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Функция для перезагрузки данных
  const handleRetry = () => {
    fetchData();
  };

  if (!timelineData || !overviewData || !growthData || !dailyData) return null;
  return (
    <Space direction="vertical" size="large" style={{ width: "100%" }}>
      <Title level={2}>
        <LineChartOutlined /> Дашборд
      </Title>

      {/* Показать ошибку если есть */}
      {error && (
        <Alert
          message="Ошибка загрузки данных"
          description={error}
          type="error"
          showIcon
          closable
          onClose={() => setError(null)}
          action={
            <button
              onClick={handleRetry}
              style={{
                backgroundColor: "#1890ff",
                color: "white",
                border: "none",
                padding: "4px 8px",
                borderRadius: "4px",
                cursor: "pointer",
              }}
            >
              Повторить
            </button>
          }
        />
      )}

      {loading ? <Loader /> : <GrowthTimelineChart data={timelineData} />}
      {loading ? <Loader /> : <OverviewStats data={overviewData} />}
      {loading ? <Loader /> : <GrowthStats data={growthData} />}
      {loading ? <Loader /> : <DailyStats data={dailyData} />}
    </Space>
  );
};

export default Dashboard;

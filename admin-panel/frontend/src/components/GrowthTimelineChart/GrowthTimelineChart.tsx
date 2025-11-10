import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { Card, Space, Statistic, Typography } from "antd";
import { RiseOutlined } from "@ant-design/icons";
import type { Timeline } from "../../models/dashboard";

const { Title } = Typography;

type GrowthTimelineChartProps = {
  data: Timeline[];
};

const GrowthTimelineChart: React.FC<GrowthTimelineChartProps> = ({ data }) => {
  if (!data) return null;
  // Форматируем данные для графика
  const chartData = data.map((item) => ({
    name: item.month,
    growth: item.count,
    fullDate: item.period.start,
  }));

  // Вычисляем общую статистику
  const totalGrowth = data.reduce((sum, item) => sum + item.count, 0);
  const growthMonths = data.filter((item) => item.count > 0).length;

  return (
    <Space direction="vertical" size="large" style={{ width: "100%" }}>
      <Title level={3}>График роста</Title>

      {/* Статистические карточки */}
      <div style={{ display: "flex", gap: "16px", marginBottom: "24px" }}>
        <Card style={{ flex: 1 }}>
          <Statistic
            title="Общее"
            value={totalGrowth}
            prefix={<RiseOutlined />}
            valueStyle={{ color: "#3f8600" }}
          />
        </Card>
        <Card style={{ flex: 1 }}>
          <Statistic
            title="Активные месяцы роста"
            value={growthMonths}
            valueStyle={{ color: "#1890ff" }}
          />
        </Card>
        <Card style={{ flex: 1 }}>
          <Statistic
            title="Всего месяцев отслеживания"
            value={data.length}
            valueStyle={{ color: "#722ed1" }}
          />
        </Card>
      </div>

      {/* График */}
      <Card
        title="Динамика роста"
        style={{ marginBottom: "24px" }}
        extra={<span style={{ color: "#52c41a" }}>Хронология</span>}
      >
        <ResponsiveContainer width="100%" height={300}>
          <LineChart
            data={chartData}
            margin={{
              top: 5,
              right: 30,
              left: 20,
              bottom: 5,
            }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="name"
              angle={-45}
              textAnchor="end"
              height={80}
              interval={0}
            />
            <YAxis />
            <Tooltip
              formatter={(value) => [`${value} единиц`, "Рост"]}
              labelFormatter={(label, payload) => {
                if (payload && payload[0]) {
                  return `Месяц: ${label}`;
                }
                return label;
              }}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="growth"
              stroke="#1890ff"
              strokeWidth={3}
              activeDot={{ r: 8 }}
              name="Количество"
            />
          </LineChart>
        </ResponsiveContainer>
      </Card>

      {/* Таблица данных */}
      <Card title="Детальные данные роста">
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ backgroundColor: "#fafafa" }}>
                <th
                  style={{
                    padding: "12px",
                    border: "1px solid #f0f0f0",
                    textAlign: "left",
                  }}
                >
                  Месяц
                </th>
                <th
                  style={{
                    padding: "12px",
                    border: "1px solid #f0f0f0",
                    textAlign: "center",
                  }}
                >
                  Количество
                </th>
                <th
                  style={{
                    padding: "12px",
                    border: "1px solid #f0f0f0",
                    textAlign: "left",
                  }}
                >
                  Начало периода
                </th>
                <th
                  style={{
                    padding: "12px",
                    border: "1px solid #f0f0f0",
                    textAlign: "left",
                  }}
                >
                  Конец периода
                </th>
              </tr>
            </thead>
            <tbody>
              {data.map((item, index) => (
                <tr key={index}>
                  <td style={{ padding: "12px", border: "1px solid #f0f0f0" }}>
                    {item.month}
                  </td>
                  <td
                    style={{
                      padding: "12px",
                      border: "1px solid #f0f0f0",
                      textAlign: "center",
                      color: item.count > 0 ? "#52c41a" : "#000000",
                    }}
                  >
                    {item.count}
                  </td>
                  <td style={{ padding: "12px", border: "1px solid #f0f0f0" }}>
                    {new Date(item.period.start).toLocaleDateString("ru-RU")}
                  </td>
                  <td style={{ padding: "12px", border: "1px solid #f0f0f0" }}>
                    {new Date(item.period.end).toLocaleDateString("ru-RU")}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </Space>
  );
};

export default GrowthTimelineChart;

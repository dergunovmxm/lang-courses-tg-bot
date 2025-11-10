import React from "react";
import {
  Card,
  Statistic,
  Row,
  Col,
  Progress,
  Tag,
  Space,
  Typography,
} from "antd";
import { UserAddOutlined, TrophyOutlined } from "@ant-design/icons";
import type { Growth } from "../../models/dashboard";
import { getGrowthConfig } from "./helpers";

const { Text, Title } = Typography;

interface GrowthStatsProps {
  data: Growth;
}

const GrowthStats: React.FC<GrowthStatsProps> = ({ data }) => {
  if (!data) return null;

  const {
    newUsersLast30Days,
    previousPeriodUsers,
    growthRate,
    growthPercentage,
  } = data;
  const growthConfig = getGrowthConfig(growthRate);

  return (
    <Space direction="vertical" size="large" style={{ width: "100%" }}>
      {/* Основные метрики роста */}

      <Title level={3}>Динамика роста</Title>

      <Row gutter={16}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Новых пользователей за 30 дней"
              value={newUsersLast30Days}
              prefix={<UserAddOutlined />}
              valueStyle={{ color: "#1890ff" }}
            />
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="За предыдущий период"
              value={previousPeriodUsers}
              prefix={<UserAddOutlined />}
              valueStyle={{ color: "#722ed1" }}
            />
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Темп роста"
              value={growthRate}
              prefix={growthConfig.icon}
              valueStyle={{ color: growthConfig.color }}
              suffix={<Text type="secondary">пользователей</Text>}
            />
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Процент роста"
              value={growthPercentage}
              precision={2}
              prefix={growthConfig.arrow}
              suffix="%"
              valueStyle={{ color: growthConfig.color }}
            />
          </Card>
        </Col>
      </Row>

      {/* Визуализация роста */}
      <Row gutter={16}>
        <Col xs={24} lg={12}>
          <Card title="Динамика роста">
            <Space direction="vertical" style={{ width: "100%" }} size="middle">
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <Text>Статус роста:</Text>
                <Tag color={growthConfig.color} icon={growthConfig.icon}>
                  {growthConfig.status.toUpperCase()}
                </Tag>
              </div>

              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <Text>Предыдущий период: {previousPeriodUsers}</Text>
                <Text strong>Текущий период: {newUsersLast30Days}</Text>
              </div>

              <Progress
                percent={Math.min(growthPercentage, 100)}
                strokeColor={growthConfig.color}
                status={growthConfig.progressStatus}
                format={(percent) => `${percent?.toFixed(1)}% роста`}
              />

              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  fontSize: "12px",
                }}
              >
                <Text type="secondary">
                  +{previousPeriodUsers} пользователей
                </Text>
                <Text type="secondary">
                  +{newUsersLast30Days} пользователей
                </Text>
              </div>
            </Space>
          </Card>
        </Col>

        <Col xs={24} lg={12}>
          <Card title="Сравнение периодов">
            <Space direction="vertical" style={{ width: "100%" }} size="large">
              <div>
                <Text strong>Изменение:</Text>
                <div style={{ marginTop: 8 }}>
                  <Text>
                    {growthRate >= 0 ? "Увеличение на " : "Снижение на "}
                    <Text strong style={{ color: growthConfig.color }}>
                      {Math.abs(growthRate)} пользователей
                    </Text>
                  </Text>
                </div>
              </div>

              <div>
                <Text strong>Эффективность роста:</Text>
                <div style={{ marginTop: 8 }}>
                  <Progress
                    type="circle"
                    percent={Math.min(growthPercentage, 200)}
                    width={80}
                    strokeColor={growthConfig.color}
                    format={(percent) => (
                      <div style={{ textAlign: "center" }}>
                        <div style={{ fontSize: "12px" }}>Рост</div>
                        <div style={{ fontSize: "14px", fontWeight: "bold" }}>
                          {percent}%
                        </div>
                      </div>
                    )}
                  />
                </div>
              </div>

              {growthPercentage >= 100 && (
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <TrophyOutlined style={{ color: "#ffc53d" }} />
                  <Text strong type="warning">
                    Отличные результаты! Рост превысил 100%
                  </Text>
                </div>
              )}
            </Space>
          </Card>
        </Col>
      </Row>

      {/* Сводная информация */}
      <Card
        size="small"
        style={{
          backgroundColor: growthPercentage > 0 ? "#f6ffed" : "#fff2f0",
          border: `1px solid ${growthPercentage > 0 ? "#b7eb8f" : "#ffccc7"}`,
        }}
      >
        <Row gutter={16} align="middle">
          <Col flex="auto">
            <Space direction="vertical" size="small">
              <Title level={5} style={{ margin: 0 }}>
                {growthPercentage > 0
                  ? "📈 Положительная динамика"
                  : "📊 Стабильные показатели"}
              </Title>
              <Text type="secondary">
                {growthPercentage > 0
                  ? `Количество новых пользователей увеличилось на ${growthPercentage}% по сравнению с предыдущим периодом`
                  : "Показатели роста требуют внимания"}
              </Text>
            </Space>
          </Col>
          <Col>
            <Tag
              color={
                growthPercentage > 50
                  ? "green"
                  : growthPercentage > 0
                  ? "blue"
                  : "orange"
              }
              style={{ fontSize: "14px", padding: "4px 8px" }}
            >
              {growthPercentage > 50
                ? "Высокий рост"
                : growthPercentage > 0
                ? "Умеренный рост"
                : "Требует улучшения"}
            </Tag>
          </Col>
        </Row>
      </Card>
    </Space>
  );
};

export default GrowthStats;

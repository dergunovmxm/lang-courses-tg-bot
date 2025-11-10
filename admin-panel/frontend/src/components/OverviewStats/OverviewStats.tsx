import React from "react";
import { Card, Statistic, Row, Col, Tag, Space, Typography } from "antd";
import {
  UserOutlined,
  CalendarOutlined,
  SyncOutlined,
} from "@ant-design/icons";
import type { Overview } from "../../models/dashboard";
import { formatDate, formatDateTime } from "./helpers";

const { Text, Title } = Typography;

type OverviewStatsProps = {
  data: Overview;
};

const OverviewStats: React.FC<OverviewStatsProps> = ({
  data,
}: OverviewStatsProps) => {
  // Определяем цвет и иконку для роста
  const {
    totalUsers,
    currentMonthUsers,
    previousMonthUsers,
    // growthRate,
    // growthPercentage,
    currentMonthStart,
    currentMonthEnd,
    previousMonthStart,
    previousMonthEnd,
    lastUpdated,
  } = data;

  //TODO мб пригодиться
  // const growthConfig = getGrowthConfig(growthRate);

  return (
    <Space direction="vertical" size="large" style={{ width: "100%" }}>
      <Title level={3}>Динамика</Title>
      <Row gutter={16}>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="Всего пользователей"
              value={totalUsers}
              prefix={<UserOutlined />}
              valueStyle={{ color: "#1890ff" }}
            />
          </Card>
        </Col>

        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="Текущий месяц"
              value={currentMonthUsers}
              prefix={<CalendarOutlined />}
              valueStyle={{ color: "#52c41a" }}
            />
          </Card>
        </Col>

        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="Прошлый месяц"
              value={previousMonthUsers}
              prefix={<CalendarOutlined />}
              valueStyle={{ color: "#faad14" }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col xs={24}>
          <Card title="Информация о периодах">
            <Space direction="vertical" style={{ width: "100%" }} size="small">
              <div>
                <Text strong>Текущий месяц:</Text>
                <br />
                <Text type="secondary">
                  {formatDate(currentMonthStart)} -{" "}
                  {formatDate(currentMonthEnd)}
                </Text>
              </div>

              <div>
                <Text strong>Прошлый месяц:</Text>
                <br />
                <Text type="secondary">
                  {formatDate(previousMonthStart)} -{" "}
                  {formatDate(previousMonthEnd)}
                </Text>
              </div>
            </Space>
          </Card>
        </Col>
      </Row>

      <Card
        title={
          <Space>
            <SyncOutlined />
            Обновление данных
          </Space>
        }
        size="small"
      >
        <Space direction="vertical">
          <Text>
            Последнее обновление:{" "}
            <Text strong>{formatDateTime(lastUpdated)}</Text>
          </Text>
          <Text type="secondary" style={{ fontSize: "12px" }}>
            Данные обновляются автоматически
          </Text>
        </Space>
      </Card>

      <Card size="small">
        <Row gutter={16} align="middle">
          <Col flex="auto">
            <Title level={5} style={{ margin: 0 }}>
              Статистика пользователей
            </Title>
            <Text type="secondary">
              {currentMonthUsers} новых пользователей в текущем месяце
            </Text>
          </Col>
          <Col>
            <Tag
              color={currentMonthUsers > previousMonthUsers ? "green" : "blue"}
            >
              {currentMonthUsers > previousMonthUsers
                ? "📈 Растет"
                : "📊 Стабильно"}
            </Tag>
          </Col>
        </Row>
      </Card>
    </Space>
  );
};

export default OverviewStats;

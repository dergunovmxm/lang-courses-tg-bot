import React from "react";
import { Card, Statistic, Table, Space, Col, Row, Typography } from "antd";
import { CalendarOutlined, UserAddOutlined } from "@ant-design/icons";
import { columns } from "./const";
import type { Daily } from "../../models/dashboard";

interface RegistrationDataProps {
  data: Daily;
}

const { Title } = Typography;

const DailyStats: React.FC<RegistrationDataProps> = ({ data }) => {
  const { period, startDate, endDate, dailyRegistrations, totalInPeriod } =
    data;

  // Преобразуем данные для таблицы
  const tableData = Object.entries(dailyRegistrations).map(
    ([date, count], index) => ({
      key: index,
      date,
      registrations: count,
    })
  );

  return (
    <Space direction="vertical" size="large" style={{ width: "100%" }}>
      {/* Карточки со статистикой */}
      <Title level={3}>Дневная статистика</Title>

      <Row gutter={16}>
        <Col span={8}>
          <Card>
            <Statistic
              title="Период (дни)"
              value={period}
              prefix={<CalendarOutlined />}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="Всего регистраций"
              value={totalInPeriod}
              prefix={<UserAddOutlined />}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="Дней с регистрациями"
              value={Object.keys(dailyRegistrations).length}
            />
          </Card>
        </Col>
      </Row>

      {/* Информация о периоде */}
      <Card title="Информация о периоде">
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          <div>
            <strong>Начало периода:</strong>{" "}
            {new Date(startDate).toLocaleString("ru-RU")}
          </div>
          <div>
            <strong>Конец периода:</strong>{" "}
            {new Date(endDate).toLocaleString("ru-RU")}
          </div>
        </div>
      </Card>

      {/* Таблица ежедневных регистраций */}
      <Card title="Ежедневные регистрации">
        <Table
          columns={columns}
          dataSource={tableData}
          pagination={false}
          locale={{
            emptyText: "Нет данных о регистрациях за выбранный период",
          }}
        />
      </Card>

      {/* Сводка */}
      <Card title="Сводка">
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          <div>
            <strong>Среднее в день:</strong>{" "}
            {(totalInPeriod / period).toFixed(2)} регистраций
          </div>
          <div>
            <strong>Активность:</strong>{" "}
            {((Object.keys(dailyRegistrations).length / period) * 100).toFixed(
              1
            )}
            %
          </div>
        </div>
      </Card>
    </Space>
  );
};

export default DailyStats;

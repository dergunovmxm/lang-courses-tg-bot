import { Button, Space, Table, Typography } from "antd";
import { useState, useEffect } from "react";
import type { Task } from "../../models/tasks";
import { PlusCircleOutlined, ReloadOutlined } from "@ant-design/icons";
import { columns } from "./const";

const { Title } = Typography;

const Tasks = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch("http://localhost:3001/api/tasks", {
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();

      if (result.success) {
        setTasks(result.data || []);
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
    fetchTasks();
  }, []);

  return (
    <Space direction="vertical" size="large" style={{ width: "100%" }}>
      <Title level={2}>Задания</Title>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <Button
          type="primary"
          icon={<PlusCircleOutlined />}
          loading={loading}
          onClick={fetchTasks}
        >
          Добавить
        </Button>
        <Button type="primary" icon={<ReloadOutlined />} loading={loading}>
          Обновить
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={tasks}
        rowKey="id"
        loading={loading}
        scroll={{ x: 1920 }}
        pagination={{
          pageSize: 10,
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total, range) =>
            `Показано ${range[0]}-${range[1]} из ${total} пользователей`,
        }}
        locale={{
          emptyText: "Нет данных о пользователях",
        }}
      />
    </Space>
  );
};
export default Tasks;

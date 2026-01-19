import React, { useState, useEffect } from "react";
import { Space, Typography, Table, Button, message } from "antd";
import { UserOutlined, ReloadOutlined } from "@ant-design/icons";
import { columns } from "./const";
import type { User } from "../../models/users";

const { Title } = Typography;

const Users = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchUsers = async () => {
    try {
      setLoading(true);

      const response = await fetch("http://localhost:3001/api/users", {
        headers: {
          "Content-Type": "application/json",
        },
      });
      const result = await response.json();

      console.log("result", result);

      if (result.success) {
        setUsers(result.data.users || result.data || []);
        message.success(
          `Загружено ${
            result.data.users?.length || result.data?.length || 0
          } пользователей`
        );
      } else {
        message.error("Ошибка при загрузке пользователей");
      }
    } catch (error) {
      console.error("Error fetching users:", error);
      message.error("Не удалось загрузить пользователей");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  return (
    <Space direction="vertical" size="large" style={{ width: "100%" }}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <Title level={2}>
          <UserOutlined /> Пользователи
        </Title>
        <Button
          type="primary"
          icon={<ReloadOutlined />}
          loading={loading}
          onClick={fetchUsers}
        >
          Обновить
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={users}
        rowKey="id"
        loading={loading}
        scroll={{ x: 1200 }}
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

export default Users;

import { Button, Space, Table, Typography, message, Form } from "antd";
import { useState, useEffect } from "react";
import type { Task } from "../../models/tasks";
import { PlusCircleOutlined, ReloadOutlined } from "@ant-design/icons";
import { columns } from "./const";
import usePortalModal from "../../hooks/usePortalModal";
import PortalModal from "../../components/Modal/Modal";
import CreateTaskForm from "../../forms/CreateTaskForm";

const { Title } = Typography;

const Tasks = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const { showModal, hideModal, modalState, updateModal } = usePortalModal();
  const [createTaskForm, setTaskForm] = useState<Task | null>(null);
  const [form] = Form.useForm();

  const handleAddClick = () => {
    showModal({
      title: "Добавить новое задание",
      content: <CreateTaskForm form={form} />,
      type: "success",
      onConfirm: () => handleCreateTask(),
      onCancel: () => {
        setTaskForm(null);
        hideModal();
      },
      okText: "Сохранить",
      cancelText: "Отмена",
    });
  };

  const handleCreateTask = async () => {
    try {
      const values = await form.validateFields();
      const taskData = {
        ...values,
        variants: values.variants
          ? values.variants.split("\n").filter((v: string) => v.trim() !== "")
          : [],
      };

      console.log("Данные для отправки:", taskData);

      updateModal({ confirmLoading: true });
      message.success("Задание успешно добавлено");
      form.resetFields();
      hideModal();
      // fetchTasks();
    } catch (error) {
      console.error("Ошибка валидации:", error);
      message.warning("Заполните все обязательные поля корректно");
    } finally {
      updateModal({ confirmLoading: false });
    }
  };

  const handleRefreshClick = () => {
    fetchTasks();
  };

  // todo вынести в отдельный сервис
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
    <>
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
            onClick={handleAddClick}
          >
            Добавить
          </Button>
          <Button
            type="primary"
            icon={<ReloadOutlined />}
            loading={loading}
            onClick={handleRefreshClick}
          >
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

      <PortalModal modalState={modalState} hideModal={hideModal} />
    </>
  );
};
export default Tasks;

import { Typography, Tag, Space } from "antd";
import type { Task } from "../../models/tasks";

const { Text } = Typography;

export const columns = [
  {
    title: "ID",
    dataIndex: "id",
    key: "id",
    width: 60,
    sorter: (a: Task, b: Task) => a.id - b.id,
  },
  {
    title: "Вопрос",
    dataIndex: "question",
    key: "question",
    width: 300,
    render: (question: string) => <Text>{question}</Text>,
  },
  {
    title: "Ответ",
    dataIndex: "answer",
    key: "answer",
    width: 200,
    render: (answer: string) => (
      <Text>{answer || <Text type="secondary">—</Text>}</Text>
    ),
  },
  {
    title: "Решение",
    dataIndex: "solution",
    key: "solution",
    width: 250,
    render: (solution: string) => (
      <Text>{solution || <Text type="secondary">—</Text>}</Text>
    ),
  },
  {
    title: "Тема",
    dataIndex: "theme",
    key: "theme",
    width: 50,
    render: (theme: string) => (
      <Tag color="blue">{theme || <Text type="secondary">—</Text>}</Tag>
    ),
  },
  {
    title: "Тип",
    dataIndex: "type",
    key: "type",
    width: 50,
    render: (type: string) => (
      <Tag color="purple">{type || <Text type="secondary">—</Text>}</Tag>
    ),
  },
  {
    title: "Уровень",
    dataIndex: "level",
    key: "level",
    width: 10,
    render: (level: string) => {
      return <Tag>{level || <Text type="secondary">—</Text>}</Tag>;
    },
  },
  {
    title: "Варианты",
    dataIndex: "variants",
    key: "variants",
    width: 200,
    render: (variants: string[]) => {
      if (!variants || variants.length === 0) {
        return <Text type="secondary">Нет вариантов</Text>;
      }
      return (
        <Space direction="vertical" size="small">
          {variants.map((variant, index) => (
            <Text key={index}>{`${index + 1}. ${variant}`}</Text>
          ))}
        </Space>
      );
    },
  },
  {
    title: "Стоимость",
    dataIndex: "cost",
    key: "cost",
    width: 100,
    render: (cost: number) => <Tag color="gold">{cost || 0}</Tag>,
    sorter: (a: Task, b: Task) => a.cost - b.cost,
  },
  {
    title: "Создано",
    dataIndex: "created_at",
    key: "created_at",
    width: 180,
    render: (date: string) =>
      date ? (
        new Date(date).toLocaleDateString("ru-RU", {
          year: "numeric",
          month: "short",
          day: "numeric",
          hour: "2-digit",
          minute: "2-digit",
        })
      ) : (
        <Text type="secondary">—</Text>
      ),
    sorter: (a: Task, b: Task) =>
      new Date(a.created_at).getTime() - new Date(b.created_at).getTime(),
  },
];

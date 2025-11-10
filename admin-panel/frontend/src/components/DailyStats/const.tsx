import { Tag } from "antd";

export const columns = [
  {
    title: "Дата",
    dataIndex: "date",
    key: "date",
    render: (date: string) => new Date(date).toLocaleDateString("ru-RU"),
  },
  {
    title: "Регистрации",
    dataIndex: "registrations",
    key: "registrations",
    render: (count: number) => (
      <Tag color={count > 0 ? "green" : "default"}>{count}</Tag>
    ),
  },
];

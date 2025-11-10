import { Typography, Tag } from "antd";
import type { User } from "../../models/users";

const { Text } = Typography;

export const columns = [
  {
    title: "ID",
    dataIndex: "id",
    key: "id",
    width: 80,
    sorter: (a: User, b: User) => a.id - b.id,
  },
  {
    title: "Telegram ID",
    dataIndex: "telegram_id",
    key: "telegram_id",
    width: 160,
    render: (telegramId: number) => <Text code>{telegramId}</Text>,
  },
  {
    title: "Имя пользователя",
    dataIndex: "username",
    key: "username",
    width: 180,
    render: (username: string) =>
      username ? `@${username}` : <Text type="secondary">Не указан</Text>,
  },
  {
    title: "Имя",
    dataIndex: "first_name",
    key: "first_name",
    width: 180,
    render: (firstName: string) =>
      firstName || <Text type="secondary">Не указано</Text>,
  },
  {
    title: "Фамилия",
    dataIndex: "last_name",
    width: 180,
    key: "last_name",
    render: (lastName: string) =>
      lastName || <Text type="secondary">Не указана</Text>,
  },
  {
    title: "Язык",
    width: 50,
    dataIndex: "language_code",
    key: "language_code",
    render: (language: string) =>
      language ? (
        <Tag color="blue">{language.toUpperCase()}</Tag>
      ) : (
        <Text type="secondary">—</Text>
      ),
  },
  {
    title: "Статус",
    dataIndex: "is_active",
    key: "is_active",
    width: 100,
    render: (isActive: boolean) => (
      <Tag color={isActive ? "green" : "red"}>
        {isActive ? "Активен" : "Неактивен"}
      </Tag>
    ),
  },
  {
    title: "Chat ID",
    dataIndex: "chat_id",
    key: "chat_id",
    width: 160,
    render: (chatId: number | null) =>
      chatId ? <Text code>{chatId}</Text> : <Text type="secondary">—</Text>,
  },
  {
    title: "Создан",
    dataIndex: "created_at",
    key: "created_at",
    width: 180,
    render: (date: string) =>
      new Date(date).toLocaleDateString("ru-RU", {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      }),
    sorter: (a: User, b: User) =>
      new Date(a.created_at).getTime() - new Date(b.created_at).getTime(),
  },
  {
    title: "Обновлен",
    dataIndex: "updated_at",
    key: "updated_at",
    width: 180,
    render: (date: string) =>
      new Date(date).toLocaleDateString("ru-RU", {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      }),
    sorter: (a: User, b: User) =>
      new Date(a.updated_at).getTime() - new Date(b.updated_at).getTime(),
  },
];

import { type MenuProps } from "antd";
import {
  UserOutlined,
  LaptopOutlined,
  DashboardOutlined,
  SettingOutlined,
  LogoutOutlined,
} from "@ant-design/icons";

export const menuItems = [
  {
    key: "/",
    icon: <DashboardOutlined />,
    label: "Дашборд",
  },
  {
    key: "/users",
    icon: <UserOutlined />,
    label: "Пользователи",
  },
  {
    key: "/tasks",
    icon: <LaptopOutlined />,
    label: "Задания",
  },
  {
    key: "/settings",
    icon: <SettingOutlined />,
    label: "Настройки",
  },
];

export const userMenuItems: MenuProps["items"] = [
  {
    key: "profile",
    icon: <UserOutlined />,
    label: "Profile",
  },
  {
    key: "logout",
    icon: <LogoutOutlined />,
    label: "Logout",
    danger: true,
  },
];

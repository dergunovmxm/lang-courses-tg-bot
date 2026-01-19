import { useNavigate } from "react-router-dom";
import { Button, Layout, Menu } from "antd";
import { menuItems } from "./const";
import { useState } from "react";

const { Sider } = Layout;

const Sidebar = () => {
  const navigate = useNavigate();

  const [collapsed, setCollapsed] = useState(false);

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key);
  };

  return (
    <Sider
      width={250}
      collapsible
      collapsed={collapsed}
      onCollapse={(value) => setCollapsed(value)}
      style={{
        overflow: "auto",
        height: "100vh",
        position: "sticky",
        top: 0,
        left: 0,
      }}
    >
      <Menu
        mode="inline"
        defaultSelectedKeys={["1"]}
        defaultOpenKeys={["sub1"]}
        style={{ height: "100%", borderRight: 0 }}
        items={menuItems}
        onClick={handleMenuClick}
      ></Menu>
    </Sider>
  );
};

export default Sidebar;

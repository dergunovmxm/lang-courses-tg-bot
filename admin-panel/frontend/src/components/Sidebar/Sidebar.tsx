import { useNavigate } from "react-router-dom";
import { Layout, Menu } from "antd";
import { menuItems } from "./const";

const Sidebar = () => {
  const navigate = useNavigate();
  const { Sider } = Layout;

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key);
  };

  return (
    <Sider width={250}>
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

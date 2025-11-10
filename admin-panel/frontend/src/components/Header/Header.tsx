import { Layout, Typography } from "antd";

const Header = () => {
  const { Header } = Layout;
  const { Title } = Typography;

  return (
    <Header style={{ background: "#fff", padding: "0 20px" }}>
      <div style={{ display: "flex", alignItems: "center", height: "100%" }}>
        <Title level={3} style={{ margin: 0, color: "#1890ff" }}>
          GradeUp Admin 🚀
        </Title>
      </div>
    </Header>
  );
};

export default Header;

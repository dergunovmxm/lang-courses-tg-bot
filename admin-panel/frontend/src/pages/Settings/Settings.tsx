import { Space, Typography } from "antd";

const Settings = () => {
  const { Title } = Typography;
  return (
    <Space direction="vertical" size="large" style={{ width: "100%" }}>
      <Title level={2}>Настройки</Title>
    </Space>
  );
};
export default Settings;

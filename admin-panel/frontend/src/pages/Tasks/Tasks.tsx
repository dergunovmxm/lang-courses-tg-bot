import { Space, Typography } from "antd";

const Tasks = () => {
  const { Title } = Typography;
  return (
    <Space direction="vertical" size="large" style={{ width: "100%" }}>
      <Title level={2}>Задания</Title>
    </Space>
  );
};
export default Tasks;

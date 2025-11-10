import { FallOutlined, MinusOutlined, RiseOutlined } from "@ant-design/icons";

export const getGrowthConfig = (growthRate: number) => {
  if (growthRate > 0) {
    return {
      color: "#cf1322",
      icon: <RiseOutlined />,
      status: "рост",
    };
  } else if (growthRate < 0) {
    return {
      color: "#3f8600",
      icon: <FallOutlined />,
      status: "снижение",
    };
  } else {
    return {
      color: "#d4b106",
      icon: <MinusOutlined />,
      status: "без изменений",
    };
  }
};

export const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString("ru-RU", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });
};

export const formatDateTime = (dateString: string) => {
  return new Date(dateString).toLocaleString("ru-RU", {
    day: "numeric",
    month: "long",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};

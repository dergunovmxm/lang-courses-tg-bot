import {
  ArrowDownOutlined,
  ArrowUpOutlined,
  FallOutlined,
  MinusOutlined,
  RiseOutlined,
} from "@ant-design/icons";

export const getGrowthConfig = (growthRate: number) => {
  if (growthRate > 0) {
    return {
      color: "#52c41a",
      icon: <RiseOutlined />,
      status: "рост",
      arrow: <ArrowUpOutlined />,
      progressStatus: "success" as const,
    };
  } else if (growthRate < 0) {
    return {
      color: "#cf1322",
      icon: <FallOutlined />,
      status: "снижение",
      arrow: <ArrowDownOutlined />,
      progressStatus: "exception" as const,
    };
  } else {
    return {
      color: "#faad14",
      icon: <MinusOutlined />,
      status: "без изменений",
      arrow: <MinusOutlined />,
      progressStatus: "normal" as const,
    };
  }
};

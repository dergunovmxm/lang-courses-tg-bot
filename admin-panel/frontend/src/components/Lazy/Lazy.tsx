import React, { Suspense } from "react";
import { Spin } from "antd";

export const LoadingFallback: React.FC = () => (
  <div
    style={{
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
      height: "200px",
    }}
  >
    <Spin size="large" />
  </div>
);

export const Lazy: React.FC<{ component: React.ComponentType }> = ({
  component: Component,
}) => (
  <Suspense fallback={<LoadingFallback />}>
    <Component />
  </Suspense>
);

export default Lazy;

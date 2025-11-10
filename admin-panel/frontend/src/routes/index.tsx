import React from "react";
import Lazy from "../components/Lazy";

// Lazy imports для страниц
const Dashboard = React.lazy(() => import("../pages/Dashboard"));
const Users = React.lazy(() => import("../pages/Users"));
const Tasks = React.lazy(() => import("../pages/Tasks"));
const Settings = React.lazy(() => import("../pages/Settings"));

export interface Route {
  path: string;
  component: React.ComponentType;
}

export const publicRoutes: Route[] = [
  {
    path: "/",
    component: () => <Lazy component={Dashboard} />,
  },
  {
    path: "/users",
    component: () => <Lazy component={Users} />,
  },
  {
    path: "/tasks",
    component: () => <Lazy component={Tasks} />,
  },
  {
    path: "/settings",
    component: () => <Lazy component={Settings} />,
  },
];

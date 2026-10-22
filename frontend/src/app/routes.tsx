import React from "react";
import { createBrowserRouter } from "react-router-dom";
import App from "./App";
import HomeownerView from "../pages/HomeownerView";
import DeveloperView from "../pages/DeveloperView";

export const router = createBrowserRouter([
    {
        path: "/",
        element: <App />,
        children: [
            { index: true, element: <HomeownerView /> },
            { path: "developer", element: <DeveloperView /> }
        ]
    }
]);
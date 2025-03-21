// import { useState } from 'react'
// import './App.css'
import "./index.css"

import Dashboard from "@/app/dashboard/dashboard.tsx";
import Search from "@/app/search/image_search.tsx";

import {StrictMode, useEffect, useState} from "react";


function App() {
    const [activeComponent, setActiveComponent] = useState("dashboard");

    useEffect(() => {
        console.log(activeComponent)
    }, [activeComponent]);

    const renderComponent = () => {
        switch (activeComponent) {
            case "dashboard":
                return <Dashboard setPage={setActiveComponent}/>;
            case "search":
                return <Search setPage={setActiveComponent}/>;
            default:
                return <Dashboard/>;
        }
    };

    return (
        <>
            {/*<div>{renderComponent()}</div>*/}
            <Dashboard />
            {/*<Search />*/}
        </>
    );
}

export default App

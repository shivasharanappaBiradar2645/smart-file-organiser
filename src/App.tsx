// import { useState } from 'react'
// import './App.css'
import "./index.css"

import Dashboard from "@/app/dashboard/dashboard.tsx";
import Search from "@/app/search/image_search.tsx";

import {StrictMode} from "react";

function App() {

    return (
        <StrictMode>
            <Dashboard/>
            {/*<Search/>*/}
        </StrictMode>
    )
}

export default App

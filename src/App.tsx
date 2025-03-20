// import { useState } from 'react'
// import './App.css'
import "./index.css"

import Dashboard from "@/app/dashboard/dashboard.tsx";
import {StrictMode} from "react";

function App() {
  // const [count, setCount] = useState(0)

  return (
    <StrictMode>
    <Dashboard/>
    </StrictMode>
  )
}

export default App

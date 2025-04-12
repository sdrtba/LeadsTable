import { createRoot } from 'react-dom/client'
import { App } from './App.jsx'
import 'bulma/css/bulma.min.css'
import {UserProvider} from "./context/UserContext.jsx";

createRoot(document.getElementById('root')).render(
    <UserProvider>
        <App />
    </UserProvider>
)

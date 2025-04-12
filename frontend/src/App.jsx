import React, {useContext, useEffect, useState} from "react"
import {Register} from "./components/Register.jsx";
import {Header} from "./components/Header.jsx";
import {UserContext} from "./context/UserContext.jsx";
import {Login} from "./components/Login.jsx";
import {Table} from "./components/Table.jsx";

export const App = () => {
    const [message, setMessage] = useState("")
    const [token, ] = useContext(UserContext)

    useEffect(() => {
        const getAPI = async () => {
            const requestOptions = {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                },
            }

            const response = await fetch("/api", requestOptions)
            const data = await response.json()

            if (response.ok) {
                setMessage(data.message)
            }
        }

        getAPI()
    }, []);

    return (
        <>
            <Header title={message}/>
            <div className="columns">
                <div className="column"></div>
                <div className="column m-5 is-two-thirds">
                    {
                        !token ? (
                            <div className="columns">
                                <Register/> <Login/>
                            </div>
                        ) : (
                            <Table/>
                        )
                    }
                </div>
                <div className="column"></div>
            </div>
        </>
    )
}
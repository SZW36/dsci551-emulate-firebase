import React, { useEffect, useState, useContext } from "react";
import io from "socket.io-client";
import SignIn from "./components/SignInPage/SignIn";
import ChatRoom from "./components/ChatRoom/ChatRoom";
import { Routes, Route } from "react-router-dom";
import { UserContext } from "./context/user.context";

function App() {
	// var ws = new WebSocket("ws://127.0.0.1:5000/");
	// ws.onmessage = function (event) {
	// 	console.log(event.data);
	// };
	const [sid, setSid] = useState(null);

	const { currentUser, setCurrentUser } = useContext(UserContext);

	useEffect(() => {
		const socket = io("http://localhost:5000");

		socket.on("json", (msg) => {
			if ("your_sid" in msg) {
				setCurrentUser({ sid: msg["your_sid"] });
			}
			console.log(msg);
		});

		return () => {
			socket.disconnect();
		};
	}, []);

	return (
		// <div className="App">
		// 	<button
		// 		onClick={async () => {
		// 			console.log(sid);
		// 			axios.put("http://127.0.0.1:5000", { sid }).then((response) => {
		// 				console.log(response);
		// 			});
		// 		}}
		// 	>
		// 		my botton
		// 	</button>
		// 	<SignIn />
		// </div>
		<Routes>
			<Route path="/" element={<SignIn />} />
			<Route path="/chat_room" element={<ChatRoom />} />
		</Routes>
	);
}

export default App;

import axios from "axios";
import React, { useEffect } from "react";
import io from "socket.io-client";

function App() {
	// var ws = new WebSocket("ws://127.0.0.1:5000/");
	// ws.onmessage = function (event) {
	// 	console.log(event.data);
	// };
	useEffect(() => {
		const socket = io("http://localhost:5000");

		socket.on("json", (msg) => {
			console.log(msg);
		});

		return () => {
			socket.disconnect();
		};
	}, []);

	return (
		<div className="App">
			<button
				onClick={() => {
					axios.get("http://127.0.0.1:5000");
				}}
			>
				my botton
			</button>
		</div>
	);
}

export default App;

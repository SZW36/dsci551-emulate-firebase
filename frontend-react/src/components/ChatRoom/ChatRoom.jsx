import { useContext, useState, useEffect, useRef } from "react";
import { UserContext } from "../../context/user.context";
import "./ChatRoom.css";
import axios from "axios";

const ChatRoom = () => {
	const { currentUser } = useContext(UserContext);
	// const [messages, setMessages] = useState([]);
	const [newMessage, setNewMessage] = useState("");
	const boxRef = useRef(null);

	const handleNewMessage = (event) => {
		setNewMessage(event.target.value);
	};

	const handleSendMessage = () => {
		if (newMessage.trim() === "") {
			return;
		}

		const message = {
			sid: currentUser["sid"],
			name: currentUser["name"],
			message: newMessage.trim(),
			// isCurrentUser: true,
		};

		axios.post("http://127.0.0.1:5000", message).then((response) => {
			console.log(response);
		});
		// setMessages((prevMessages) => [...prevMessages, message]);
		setNewMessage("");
	};

	useEffect(() => {
		if (boxRef.current) {
			boxRef.current.scrollTop = boxRef.current.scrollHeight;
		}
	}, [currentUser["messages"]]);

	return (
		<div className="chat-room">
			<div className="chat-room__box" ref={boxRef}>
				{currentUser?.messages?.map((message, index) => (
					<div
						key={index}
						className={
							message["sid"] == currentUser["sid"]
								? "chat-room__message chat-room__message--current-user"
								: "chat-room__message chat-room__message--other-user"
						}
					>
						{message["sid"] == currentUser["sid"]
							? `${message.message}: ${message.name}`
							: `${message.name}: ${message.message}`}
					</div>
				))}
			</div>
			<div className="chat-room__input-box">
				<input
					type="text"
					placeholder="Type a message..."
					value={newMessage}
					onChange={handleNewMessage}
					className="chat-room__input"
				/>
				<button className="chat-room__send-button" onClick={handleSendMessage}>
					Send
				</button>
			</div>
			<div className="chat-room__center-box"></div>
		</div>
	);
};

export default ChatRoom;

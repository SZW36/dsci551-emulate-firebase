import React, { useState, useContext } from "react";
import "./SignIn.css";
import { UserContext } from "../../context/user.context";
import axios from "axios";
import { useNavigate } from "react-router-dom";

function SignIn() {
	const [inputText, setInputText] = useState("");

	const { currentUser, setCurrentUser } = useContext(UserContext);

	// console.log(currentUser);

	const handleInputChange = (event) => {
		setInputText(event.target.value);
	};

	const navigate = useNavigate();

	const handleSubmit = (event) => {
		event.preventDefault();
		// console.log(inputText); // replace with your desired logic for handling the user input
		// console.log("SignIn 1");
		// console.log(currentUser);
		// currentUser["name"] = inputText;
		// console.log("SignIn 2");
		// console.log(currentUser);
		// setCurrentUser(currentUser);
		// console.log("SignIn 3");
		// console.log(currentUser);

		setCurrentUser((prevUser) => ({
			...prevUser,
			name: inputText,
		}));

		navigate("/chat_room");

		// axios.put("http://127.0.0.1:5000", { "sid" : currentUser["sid"] }).then((response) => {
		// 	console.log(response);
		// });
	};

	return (
		<div className="SignIn">
			<form onSubmit={handleSubmit} className="form">
				<label htmlFor="inputField" className="label">
					Enter Your Name:
				</label>
				<br />
				<input
					id="inputField"
					type="text"
					value={inputText}
					onChange={handleInputChange}
					className="input"
					placeholder="e.g. Alex"
				/>
				<br />
				<button type="submit" className="button">
					Submit
				</button>
			</form>
		</div>
	);
}

export default SignIn;

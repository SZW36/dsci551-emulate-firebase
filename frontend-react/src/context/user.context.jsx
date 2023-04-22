import { createContext, useState } from "react";

export const UserContext = createContext({
	messages: [],
	sid: null,
	name: null,
});

export const UserProvider = ({ children }) => {
	const [currentUser, setCurrentUser] = useState({
		messages: [],
		sid: null,
		name: null,
	});
	const value = { currentUser, setCurrentUser };

	return (
		<UserContext.Provider value={value}> {children} </UserContext.Provider>
	);
};

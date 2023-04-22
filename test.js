a = { abc: { abc: 1 } };

b = { def: 2 };

a["abc"] = { ...a["abc"], ...b };

console.log(a);

import React, { useState } from "react";

const NewDashboard = () => {
  // 1️⃣ React state to remember which fruit is selected
  const [selectedFruit, setSelectedFruit] = useState("");

  // 2️⃣ This runs whenever the user changes the dropdown value
  const handleFruitChange = (event) => {
    const fruit = event.target.value; // get selected value from the <select>
    setSelectedFruit(fruit);          // update React state
  };

  // 3️⃣ JSX: what we want to show on the screen
  return (
    <div style={containerStyle}>
      <h1 style={titleStyle}>New Dashboard</h1>

      <div style={cardStyle}>
        <label htmlFor="fruit-select" style={labelStyle}>
          Choose a fruit:
        </label>

        <select
          id="fruit-select"
          value={selectedFruit}
          onChange={handleFruitChange}
          style={selectStyle}
        >
          <option value="">-- Select one --</option>
          <option value="apple">Apple</option>
          <option value="banana">Banana</option>
          <option value="mango">Mango</option>
        </select>

        {/* 4️⃣ Show this box ONLY if some fruit is selected */}
        {selectedFruit && (
          <div style={resultBoxStyle}>
            <p>
              You selected: <strong>{selectedFruit}</strong>
            </p>

            <ul style={listStyle}>
              {selectedFruit === "apple" && (
                <>
                  <li>Apples are usually red or green.</li>
                  <li>They’re crispy and juicy.</li>
                </>
              )}

              {selectedFruit === "banana" && (
                <>
                  <li>Bananas are soft and sweet.</li>
                  <li>They’re great in smoothies.</li>
                </>
              )}

              {selectedFruit === "mango" && (
                <>
                  <li>Mangoes are tropical and sweet.</li>
                  <li>They’re amazing in desserts.</li>
                </>
              )}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

// 5️⃣ Basic inline CSS objects for styling
const containerStyle = {
  minHeight: "100vh",          // full screen height
  display: "flex",
  flexDirection: "column",
  justifyContent: "center",    // center horizontally
  alignItems: "center",        // center vertically
  backgroundColor: "#f5f5f5",
  fontFamily: "system-ui, sans-serif",
};

const titleStyle = {
  textAlign: "center",
  marginBottom: "16px",
};

const cardStyle = {
  backgroundColor: "white",
  padding: "24px",
  borderRadius: "8px",
  boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
  minWidth: "300px",
};

const labelStyle = {
  display: "block",
  marginBottom: "8px",
  fontWeight: "500",
};

const selectStyle = {
  width: "100%",
  padding: "8px",
  borderRadius: "4px",
  border: "1px solid #ccc",
  marginBottom: "16px",
};

const resultBoxStyle = {
  marginTop: "12px",
  padding: "12px",
  borderRadius: "4px",
  backgroundColor: "#f0f8ff",
  border: "1px solid #cce",
};

const listStyle = {
  marginTop: "8px",
  paddingLeft: "20px",
};

export default NewDashboard;

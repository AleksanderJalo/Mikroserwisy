import React, { useState } from "react";

const GATEWAY_URL = "http://127.0.0.1:8080";

function App() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [token, setToken] = useState("");
  const [orderId, setOrderId] = useState("");
  const [orderTitle, setOrderTitle] = useState("");
  const [orderAmount, setOrderAmount] = useState("");
  const [ordersOutput, setOrdersOutput] = useState("");
  const [logsOutput, setLogsOutput] = useState("");
  const [feedback, setFeedback] = useState("");


  const register = async () => {
    try {
      const resp = await fetch(`${GATEWAY_URL}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      const data = await resp.json();
      if (resp.ok) setFeedback("Użytkownik zarejestrowany poprawnie");
      else setFeedback(data.detail || "Błąd rejestracji");
    } catch (err) {
      setFeedback("Błąd połączenia z serwerem");
    }
  };

  const login = async () => {
    try {
      const resp = await fetch(`${GATEWAY_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      const data = await resp.json();
      if (data.access_token) {
        setToken(data.access_token);
        console.log("Token:", data.access_token);
        setFeedback("Logowanie poprawne");
      } else {
        setFeedback("Błąd logowania");
      }
    } catch (err) {
      setFeedback("Błąd połączenia z serwerem");
    }
  };


  const createOrder = async () => {
    try {
      const order = { id: Number(orderId), title: orderTitle, amount: Number(orderAmount) };
      const resp = await fetch(`${GATEWAY_URL}/app/orders`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
          "username": username,
        },
        body: JSON.stringify(order),
      });
      const data = await resp.json();
      if (resp.ok) setFeedback(`Dodano zamówienie: ${orderTitle}, ilość: ${orderAmount}`);
      else setFeedback(data.detail || "Błąd dodawania zamówienia");
    } catch (err) {
      setFeedback("Błąd połączenia z serwerem");
    }
  };

  const updateOrder = async () => {
    try {
      const order = { id: Number(orderId), title: orderTitle, amount: Number(orderAmount) };
      const resp = await fetch(`${GATEWAY_URL}/app/orders/${order.id}`, {
        method: "PUT",
        headers: { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
          "username": username,
        },
        body: JSON.stringify(order),
      });
      const data = await resp.json();
      if (resp.ok) setFeedback(`Zaktualizowano zamówienie: ${orderTitle}, ilość: ${orderAmount}`);
      else setFeedback(data.detail || "Błąd aktualizacji zamówienia");
    } catch (err) {
      setFeedback("Błąd połączenia z serwerem");
    }
  };

  const deleteOrder = async () => {
    try {
      const resp = await fetch(`${GATEWAY_URL}/app/orders/${Number(orderId)}`, {
        method: "DELETE",
        headers: { "Authorization": `Bearer ${token}`, "username": username },
      });
      const data = await resp.json();
      if (resp.ok) setFeedback(`Usunięto zamówienie o ID: ${orderId}`);
      else setFeedback(data.detail || "Błąd usuwania zamówienia");
    } catch (err) {
      setFeedback("Błąd połączenia z serwerem");
    }
  };

  const getOrder = async () => {
    try {
      const resp = await fetch(`${GATEWAY_URL}/app/orders/${Number(orderId)}`, {
        headers: { "Authorization": `Bearer ${token}`, "username": username },
      });
      const data = await resp.json();
      setOrdersOutput(JSON.stringify(data, null, 2));
      setFeedback("Pobrano zamówienie");
    } catch (err) {
      setFeedback("Błąd połączenia z serwerem");
    }
  };

  const getOrders = async () => {
    try {
      const resp = await fetch(`${GATEWAY_URL}/app/orders`, {
        headers: { "Authorization": `Bearer ${token}`, "username": username },
      });
      const data = await resp.json();
      setOrdersOutput(JSON.stringify(data, null, 2));
      setFeedback("Pobrano wszystkie zamówienia");
    } catch (err) {
      setFeedback("Błąd połączenia z serwerem");
    }
  };

  const getLogs = async () => {
    try {
      const resp = await fetch(`${GATEWAY_URL}/logs/logs`);
      const data = await resp.json();
      setLogsOutput(JSON.stringify(data, null, 2));
      setFeedback("Pobrano logi");
    } catch (err) {
      setFeedback("Błąd połączenia z serwerem");
    }
  };

  return (
    <div style={{ padding: "20px", fontFamily: "Arial, sans-serif" }}>
      <h1>Projekt Przetwarzanie Rozproszone</h1>

      <section>
        <h2>Autoryzacja</h2>
        <input placeholder="Nazwa użytkownika" value={username} onChange={e => setUsername(e.target.value)} />
        <input type="password" placeholder="Hasło" value={password} onChange={e => setPassword(e.target.value)} />
        <button onClick={register}>Zarejestruj</button>
        <button onClick={login}>Zaloguj</button>
        <p><strong>Feedback:</strong> {feedback}</p>
      </section>

      <section>
        <h2> Zamówienia</h2>
        <input type="number" placeholder="ID Zamówienia" value={orderId} onChange={e => setOrderId(e.target.value)} />
        <input placeholder="Tytuł" value={orderTitle} onChange={e => setOrderTitle(e.target.value)} />
        <input type="number" placeholder="Ilość" value={orderAmount} onChange={e => setOrderAmount(e.target.value)} />
        <div style={{ marginTop: "5px" }}>
          <button onClick={createOrder}>Dodaj</button>
          <button onClick={updateOrder}>Aktualizuj</button>
          <button onClick={deleteOrder}>Usuń</button>
          <button onClick={getOrder}>Pokaż wybrane</button>
          <button onClick={getOrders}>Pokaż wszystkie</button>
        </div>
        <pre>{ordersOutput}</pre>
      </section>

      <section>
        <h2>Logi</h2>
        <button onClick={getLogs}>Pobierz logi</button>
        <pre>{logsOutput}</pre>
      </section>
    </div>
  );
}

export default App;

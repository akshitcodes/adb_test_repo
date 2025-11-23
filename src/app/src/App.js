import './App.css';
import React, { useState, useEffect } from 'react';
import { getTodos, postTodo } from './api';

export function App() {
  const [todos, setTodos] = useState([]);
  const [text, setText] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(10);
  const [totalPages, setTotalPages] = useState(1);

  const fetchTodos = async () => {
    try {
      const data = await getTodos(page, pageSize);
      setTodos(Array.isArray(data.results) ? data.results : []);
      setTotalPages(data.total_pages || 1);
    } catch (err) {
      console.error(err);
      setError('Unable to load todos');
    }
  };

  useEffect(() => {
    fetchTodos();
  }, [page]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    const trimmed = text ? text.trim() : '';
    const MAX_TODO_LENGTH = 200;
    if (!trimmed) return setError('Please enter a todo');
    if (trimmed.length > MAX_TODO_LENGTH) return setError(`Todo must be at most ${MAX_TODO_LENGTH} characters`);
    setSaving(true);
    try {
      await postTodo(trimmed);
      setText('');
      await fetchTodos();
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.error || err.message || 'Unable to save todo');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="App">
      <div>
        <h1>List of TODOs</h1>
        {error && <div style={{color:'red'}}>{error}</div>}
        <div className="todo-list-wrap">
          <ul className="todo-list">
            {todos.length === 0 && <li>No todos yet</li>}
            {todos.map(t => (
              <li key={t.id}>{t.text}</li>
            ))}
          </ul>
        </div>
        <div style={{marginTop:8}}>
          <button onClick={() => setPage(p => Math.max(1, p-1))} disabled={page <= 1}>Prev</button>
          <span style={{margin: '0 8px'}}>Page {page} / {totalPages}</span>
          <button onClick={() => setPage(p => Math.min(totalPages, p+1))} disabled={page >= totalPages}>Next</button>
        </div>
      </div>
      <div>
        <h1>Create a ToDo</h1>
        <form onSubmit={handleSubmit}>
          <div>
            <label htmlFor="todo">ToDo: </label>
            <input id="todo" type="text" value={text} onChange={(e)=>setText(e.target.value)} maxLength={200} />
          </div>
          <div style={{"marginTop": "5px"}}>
            <button type="submit" disabled={saving}>{saving ? 'Saving...' : 'Add ToDo!'}</button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default App;

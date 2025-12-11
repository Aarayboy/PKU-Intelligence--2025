import axios from "axios";

const api = axios.create({
<<<<<<< HEAD
  baseURL: "http://127.0.0.1:8000",
  timeout: 8000
=======
  baseURL: "http://127.0.0.1:8000"
>>>>>>> 73951398caa1c7d19c3b38d852910cf4d3d33660
});

export default api;
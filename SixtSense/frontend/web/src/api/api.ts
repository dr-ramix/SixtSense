import axios from "axios";

const api = axios.create({
  baseURL: "https://hackatum25.sixt.io/api/",
});

export default api;

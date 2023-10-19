import axios from "axios";

const baseURL =
  process.env.ENVERONMNET === "fastapi"
    ? "http://127.0.0.1:8000/api/v1/pat/"
    : "http://127.0.0.1:8000/api/v1/pat/";

export default axios.create({
  baseURL,
});

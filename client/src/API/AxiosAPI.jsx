import axios from "axios"

const baseURL =  process.env.ENVERONMNET === "fastapi"? "http://127.0.0.1:8000/" : "http://127.0.0.1:8000/";

export default axios.create({
    baseURL,
})
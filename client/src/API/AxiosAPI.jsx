import axios from "axios";
import { useContext } from "react";
import { Context } from "../Context/AppContextProvider";

const baseURL =
  process.env.ENVERONMNET === "fastapi"
    ? "http://127.0.0.1:8000/api/v1/pat/"
    : "http://127.0.0.1:8000/api/v1/pat/";

const AxiosAPI = axios.create({
  baseURL,
});

// Add a request interceptor
AxiosAPI.interceptors.request.use(
  (config) => {
    // Modify the request config to include the authorization header
    const token = localStorage.getItem("token");
    if (token) {
      console.log(token, typeof token);
      config.headers["Authorization"] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    // Do something with the request error
    return Promise.reject(error);
  }
);

// Add a response interceptor
AxiosAPI.interceptors.response.use(
  (response) => {
    if (response.data.conn_status == "f") {
      // alert(response.data.message);
      console.log("response.data.conn_status: ", response.data.conn_status);
      window.location.href = "/login";
    }
    // Do something with the response data
    console.log("Response Data:", response.data);
    return response;
  },
  (error) => {
    // Do something with the response error
    console.error("Response Error:", error);
    return Promise.reject(error);
  }
);

export default AxiosAPI;

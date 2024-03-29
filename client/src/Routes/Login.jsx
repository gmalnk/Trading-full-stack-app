import React, { useContext, useState } from "react";
import ButtonDark from "../Components/ButtonDark";
import { useLocation, useNavigate } from "react-router-dom";
import AxiosAPI from "../API/AxiosAPI";
import { Context } from "../Context/AppContextProvider";

export default function Login(props) {
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const { setLogedIn } = useContext(Context);

  const handleOnCLickLogInButton = async () => {
    if (name === "") {
      alert("Please enter your name!");
    } else if (email === "") {
      alert("Please enter your email address!");
    } else if (password === "") {
      alert("Please enter a password!");
    } else {
      await AxiosAPI.post(
        "signin",
        {},
        {
          headers: {
            name,
            email,
            password,
          },
        }
      ).then((response) => {
        if (response.data.conn_status === "s") {
          localStorage.setItem("token", response.data.access_token);
          // const previousPath = location.state && location.state.from;
          // console.log(previousPath);
          setLogedIn(true);
          navigate("/");
        } else {
          alert(response.data.message);
        }
      });
    }
  };

  return (
    <>
      <div class="login">
        <div class="loginSection">
          <div class="loginContainer">
            <div class="loginImgContainer">
              <img loading="lazy" src="./Images/8.jpg" class="loginImg" />
            </div>
            <div class="loginFormContainer">
              <div class="loginForm">
                <div class="loginFormHeading">LOG IN</div>
                <div class="loginFormSubHeadding">
                  Sign in to access your account
                </div>
                <div class="loginFormText">Name</div>
                <input
                  class="loginFormInput"
                  placeholder="Name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                ></input>
                <div class="loginFormText">Email</div>
                <input
                  class="loginFormInput"
                  placeholder="yourmail@gmail.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                ></input>
                <div class="loginFormText">Password</div>
                <input
                  class="loginFormInput"
                  placeholder="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                ></input>
                <div style={{ marginTop: "20px" }}>
                  <div onClick={handleOnCLickLogInButton}>
                    <ButtonDark text="log in" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

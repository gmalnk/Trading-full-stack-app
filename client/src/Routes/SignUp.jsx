import React, { useContext, useState } from "react";
import ButtonDark from "../Components/ButtonDark";
import AxiosAPI from "../API/AxiosAPI";
import { useNavigate } from "react-router-dom";
import { Context } from "../Context/AppContextProvider";

const SignUp = () => {
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const { setLogedIn } = useContext(Context);

  const handleOnCLickSignUpButton = async () => {
    if (name === "") {
      alert("Please enter your name!");
    } else if (email === "") {
      alert("Please enter your email address!");
    } else if (password === "") {
      alert("Please enter a password!");
    } else if (confirmPassword === "") {
      alert("Please confirn password!");
    } else if (confirmPassword !== password) {
      alert("passwords do not match!");
    } else {
      await AxiosAPI.post(
        "signup",
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
              <img loading="lazy" src="./Images/9.jpg" class="loginImg" />
            </div>
            <div class="loginFormContainer">
              <div class="loginForm">
                <div class="div-6">Join Us</div>
                <div class="loginFormHeading">SIGN UP</div>
                <div class="loginFormSubHeadding">
                  Sign up to access your account
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
                <div class="loginFormText">Confirm Password</div>
                <input
                  class="loginFormInput"
                  placeholder="confirm password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                ></input>
                <div style={{ marginTop: "20px" }}>
                  <div onClick={handleOnCLickSignUpButton}>
                    <ButtonDark text="Sign up" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default SignUp;

import React from "react";

export default function Navbar() {
  const link = window.location.pathname;
  return (
    <nav className="navbar navbar-expand-lg navbar-light bg-white m-0 p-0">
      <div className="container-fluid">
        <div className="collapse navbar-collapse" id="navbarCollapse">
          <div className="navbar-nav">
            <a
              href="/"
              className={
                link === "/" ? "nav-item nav-link active" : "nav-item nav-link"
              }>
              Home
            </a>
            <a
              href="/stocks"
              className={
                link === "/stocks"
                  ? "nav-item nav-link active"
                  : "nav-item nav-link"
              }>
              Stocks
            </a>
            <a
              href="/trades"
              className={
                link === "/trades"
                  ? "nav-item nav-link active"
                  : "nav-item nav-link"
              }>
              Trades
            </a>
            <a
              href="/p&l"
              className={
                link === "/p&l"
                  ? "nav-item nav-link active"
                  : "nav-item nav-link"
              }>
              P/L
            </a>
            <a
              href="/about"
              className={
                link === "/about"
                  ? "nav-item nav-link active"
                  : "nav-item nav-link"
              }>
              About
            </a>
          </div>
          <div className="navbar-nav ms-auto">
            <a
              href="/login"
              className={
                link === "/login"
                  ? "nav-item nav-link active"
                  : "nav-item nav-link"
              }>
              Login / SignUp
            </a>
          </div>
        </div>
      </div>
    </nav>
  );
}

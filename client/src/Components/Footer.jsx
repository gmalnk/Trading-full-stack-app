import React from "react";
import ButtonDark from "./ButtonDark";
import TextLogo from "./TextLogo";

const Footer = () => {
  return (
    <div className="footerContainer">
      <div className="footerContainer-row1">
        <div className="footerDetailsContainer">
          <div className="footerContainer-mailSubscriptionColumn">
            <div className="mailSubscriptionContainer">
              <TextLogo />
              <div className="mailSubscriptionDescription">
                Join our mailing list for updates.
              </div>
              <div className="mailSubscriptionForm">
                <input
                  className="mailSubscriptionInput"
                  placeholder="yourmail@gmail.com"
                ></input>
                <ButtonDark text="Subscribe" />
              </div>
              <div className="mailSubscriptionConsent">
                By subscribing, you agree to our Privacy Policy and consent to
                receive updates.
              </div>
            </div>
          </div>
          <div className="footerContainer-InfoColumn">
            <div className="infoColumnContainer">
              <div className="infoDetailsContainer">
                <div className="aboutUsColumn">
                  <div className="aboutUsDetails">
                    <div className="detailsHeader">About Us</div>
                    <div className="option1">Product</div>
                    <div className="option">Services</div>
                    <div className="option">Contact Us</div>
                    <div className="option">FAQs</div>
                    <div className="option">Support</div>
                  </div>
                </div>
                <div className="developedUsingColumn">
                  <div className="developedUsingDetails">
                    <div className="detailsHeader">Developed Using</div>
                    <div className="option1">React JS</div>
                    <div className="option">Python - Backend</div>
                    <div className="option">Postgresql</div>
                    <div className="option">FastAPI</div>
                    <div className="option">SmartAPI</div>
                  </div>
                </div>
                <div className="followUsColumn">
                  <div className="followUsDetails">
                    <div className="detailsHeader">Follow us</div>
                    <div className="option1">
                      <img
                        loading="lazy"
                        src="https://cdn.builder.io/api/v1/image/assets/TEMP/f3a1957b-40aa-40a1-8b44-71ad0a382d95?apiKey=05a03f3237de41d99e4f93550adfb278&"
                        className="followUsImg"
                      />
                      <div style={{ marginLeft: "5pX" }}>
                        <a
                          href="https://www.facebook.com/anil.nayak.56211497/"
                          target="_blank"
                        >
                          Facebook
                        </a>
                      </div>
                    </div>
                    <div className="option">
                      <img
                        loading="lazy"
                        src="https://cdn.builder.io/api/v1/image/assets/TEMP/8c3f429c-a24f-488a-8538-f2042885ca5e?apiKey=05a03f3237de41d99e4f93550adfb278&"
                        className="followUsImg"
                      />
                      <div style={{ marginLeft: "5pX" }}>
                        <a
                          href="https://www.instagram.com/m.r_anilnayak/"
                          target="_blank"
                        >
                          Instagram
                        </a>
                      </div>
                    </div>
                    <div className="option">
                      <img
                        loading="lazy"
                        src="https://cdn.builder.io/api/v1/image/assets/TEMP/6ee1f83e-4656-4d49-b694-bb6f1243f0e7?apiKey=05a03f3237de41d99e4f93550adfb278&"
                        className="followUsImg"
                      />
                      <div style={{ marginLeft: "5pX" }}>
                        <a href="" target="_blank">
                          Twitter
                        </a>
                      </div>
                    </div>
                    <div className="option">
                      <img
                        loading="lazy"
                        src="https://cdn.builder.io/api/v1/image/assets/TEMP/7e83e41b-01db-4173-857d-b9db12d13428?apiKey=05a03f3237de41d99e4f93550adfb278&"
                        className="followUsImg"
                      />
                      <div style={{ marginLeft: "5pX" }}>
                        <a
                          href="https://www.linkedin.com/in/goram-nayak-28a721182/"
                          target="_blank"
                        >
                          LinkedIn
                        </a>
                      </div>
                    </div>
                    <div className="option">
                      <img
                        loading="lazy"
                        src="https://cdn.builder.io/api/v1/image/assets/TEMP/af3a1396-8934-4cd7-ae13-e2eb7bfb183e?apiKey=05a03f3237de41d99e4f93550adfb278&"
                        className="followUsImg"
                      />
                      <div style={{ marginLeft: "5pX" }}>
                        <a href="" target="_blank">
                          YouTube
                        </a>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className="footerContainer-row2"></div>
      <div className="footerContainer-copyRights">
        <div className="footerContainer-copyRightsText">
          © 2023 Algo Traders. All rights reserved.
        </div>
        <div className="legalInformationSection">
          <div className="legalInformation">Privacy Policy</div>
          <div className="legalInformation">Terms of Service</div>
          <div className="legalInformation">Cookie Settings</div>
        </div>
      </div>
    </div>
  );
};

export default Footer;

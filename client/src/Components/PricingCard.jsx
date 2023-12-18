import React from "react";
import ButtonDark from "./ButtonDark";

const PricingCard = (props) => {
  console.log(props.plan.Items);
  return (
    <div class="pricingPlanCard">
      <div class="pricingPlanContainer">
        <div class="pricingPlanHeading">{props.plan.Heading}</div>
        <div class="pricingPlanCost">{props.plan.Cost}</div>
        <div class="pricingPlanLine"></div>
        <div class="pricingPlanSubHeadding">Includes:</div>
        {props.plan.Items.map((element) => {
          return (
            <div class="pricingPlanItem">
              <img
                loading="lazy"
                src="https://cdn.builder.io/api/v1/image/assets/TEMP/3312b4e0-1bcc-4a7f-adb7-560bc5c2383b?apiKey=05a03f3237de41d99e4f93550adfb278&"
                class="pricingPlanItemImg"
              />
              <div class="priicngPlanItemText">{element}</div>
            </div>
          );
        })}
        <div
          style={{
            alignSelf: "stretch",
            textAlign: "center",
            marginTop: "24px",
          }}
        >
          <ButtonDark text="Subcribe" />
        </div>
      </div>
    </div>
  );
};

export default PricingCard;

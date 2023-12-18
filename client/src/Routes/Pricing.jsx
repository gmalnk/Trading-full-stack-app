import React from "react";
import ButtonDark from "../Components/ButtonDark";
import ButtonLight from "../Components/ButtonLight";
import PricingCard from "../Components/PricingCard";
import { basicPlan, bussinessPlan } from "../Constants/constants";

const Pricing = () => {
  return (
    <div class="pricingContainer">
      <div class="pricingSection">
        <div class="pricingAffordable">Affordable</div>
        <div class="pricingPlans">Pricing Plans</div>
        <div class="pricingText">
          Choose the perfect plan that suits your needs
        </div>
        <div class="pricingButtons">
          <ButtonDark text="Monthly" />
          <ButtonLight text="Yearly" />
        </div>
        <div class="pricingCards">
          <div class="pricingCardsContainer">
            <PricingCard plan={basicPlan} />
            <PricingCard plan={bussinessPlan} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Pricing;

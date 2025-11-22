export type Car = {
  vehicle: {
    id: string;
    brand: string;
    model: string;
    acrissCode: string;
    images: string[];
    bagsCount: number;
    passengersCount: number;
    groupType: string;
    tyreType: string;
    transmissionType: string;
    fuelType: string;
    isNewCar: boolean;
    isRecommended: boolean;
    isMoreLuxury: boolean;
    isExcitingDiscount: boolean;
    attributes: {
      key: string;
      title: string;
      value: string;
      attributeType: string;
      iconUrl: string;
    }[];
    vehicleStatus: string;
    vehicleCost: { currency: string; value: number };
    upsellReasons: string[];
  };
  pricing: {
    discountPercentage: number;
    displayPrice: {
      currency: string;
      amount: number;
      prefix: string;
      suffix: string;
    };
    totalPrice: {
      currency: string;
      amount: number;
      prefix: string;
      suffix: string;
    };
  };
  dealInfo: string;
  tags: string[];
};

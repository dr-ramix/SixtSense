export type AddOnResponse = {
  addons: AddOn[];
};

export type AddOn = {
  id: number;
  name: string;
  options: AddOnOption[];
};

export type AddOnOption = {
  chargeDetail: AddOnChargeDetail;
  additionalInfo: AddOnAdditionalInfo;
};

export type AddOnChargeDetail = {
  id: string;
  title: string;
  description: string;
  iconUrl: string;
  tags: string[];
};

export type AddOnAdditionalInfo = {
  price: AddOnPriceInfo;
  isPreviouslySelected: boolean;
  isSelected: boolean;
  isEnabled: boolean;
  selectionStrategy: AddOnSelectionStrategy;
  isNudge: boolean;
};

export type AddOnPriceInfo = {
  discountPercentage: number;
  displayPrice: {
    currency: string;
    amount: number;
    suffix: string;
  };
};

export type AddOnSelectionStrategy = {
  isMultiSelectionAllowed: boolean;
  maxSelectionLimit: number;
  currentSelection: number;
};

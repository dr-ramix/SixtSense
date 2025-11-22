export interface Protection {
  id: string;
  name: string;
  deductibleAmount: {
    currency: string;
    value: number;
  };
  ratingStars: number;
  isPreviouslySelected: boolean;
  isSelected: boolean;
  isDeductibleAvailable: boolean;
  includes: CoverageItem[];
  excludes: CoverageItem[];
  price: {
    discountPercentage: number;
    displayPrice: PriceDetail;
    listPrice?: PriceDetail;
    totalPrice: PriceDetail;
  };
  isNudge: boolean;
}

export interface CoverageItem {
  id: string;
  title: string;
  description: string;
  tags: string[];
}

export interface PriceDetail {
  currency: string;
  amount: number;
  suffix: string;
}

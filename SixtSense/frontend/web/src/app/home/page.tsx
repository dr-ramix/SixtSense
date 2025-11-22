import CarSelection from "@/components/carConfiguration/CarSelection";
import AddOnSelection from "@/components/carConfiguration/AddOnSelection";
import InsuranceSelection from "@/components/carConfiguration/InsuranceSelection";
import Chatbot from "@/components/chat/Chatbot";
import { Button } from "@/components/ui/button";
import { Car } from "@/domain/Car";
import { useState } from "react";

const sampleCar: Car = {
  vehicle: {
    id: "1a1257a0-e495-43ff-b213-9786338e159b",
    brand: "VOLKSWAGEN",
    model: "GOLF",
    acrissCode: "CDAR",
    images: [
      "https://vehicle-pictures-prod.orange.sixt.com/143707/9d9d9c/18_1.png",
    ],
    bagsCount: 0,
    passengersCount: 5,
    groupType: "SEDAN",
    tyreType: "All-year tyres",
    transmissionType: "Automatic",
    fuelType: "Petrol",
    isNewCar: true,
    isRecommended: false,
    isMoreLuxury: false,
    isExcitingDiscount: false,
    attributes: [
      {
        key: "P100_VEHICLE_ATTRIBUTE_AUTOMATIC",
        title: "Transmission",
        value: "Automatic",
        attributeType: "CARD_ATTRIBUTE",
        iconUrl:
          "https://www.sixt.com/shared/icons/trex/p100/gearbox_automatic.png",
      },
      {
        key: "P100_VEHICLE_ATTRIBUTE_SEATS",
        title: "Seats",
        value: "5",
        attributeType: "CARD_ATTRIBUTE",
        iconUrl: "https://www.sixt.com/shared/icons/trex/p100/seat.png",
      },
    ],
    vehicleStatus: "AVAILABLE",
    vehicleCost: { currency: "EUR", value: 36400 },
    upsellReasons: [],
  },
  pricing: {
    discountPercentage: 0,
    displayPrice: { currency: "EUR", amount: 0, prefix: "+", suffix: "/day" },
    totalPrice: { currency: "EUR", amount: 0, prefix: "", suffix: "in total" },
  },
  dealInfo: "BOOKED_CATEGORY",
  tags: [],
};

const sampleProtections = [
  {
    id: "1002182",
    name: "Peace of Mind",
    deductibleAmount: {
      currency: "USD",
      value: 0,
    },
    ratingStars: 3,
    isPreviouslySelected: false,
    isSelected: false,
    isDeductibleAvailable: true,
    includes: [
      {
        id: "LD",
        title:
          "LDW - Loss Damage Waiver for collision damages, scratches, bumps and theft.",
        description:
          "Enjoy the peace of mind of knowing you're protected from high costs in case your vehicle is stolen or damaged.",
        tags: [],
      },
      {
        id: "S3",
        title: "Supplemental Liability Insurance",
        description:
          "With liability insurance, you are protected against claims from third parties up to a limit of USD 300,000 per accident.",
        tags: [],
      },
      {
        id: "IP",
        title: "Personal Property Coverage",
        description:
          "Safeguard your personal items and those of your accompanying family members from damage or loss.",
        tags: [],
      },
      {
        id: "I",
        title: "Personal Accident Coverage",
        description:
          "Both the driver and passengers of the rental vehicle are entitled to financial compensation for accident-related medical costs.",
        tags: [],
      },
      {
        id: "BC",
        title: "Extended Roadside Protection",
        description:
          "In the case of self-caused errors that prevent further travel, SIXT will assist you getting on the road again (flat tire, empty tank or battery, lost or locked-in key).",
        tags: [],
      },
    ],
    excludes: [],
    price: {
      discountPercentage: 2,
      displayPrice: {
        currency: "USD",
        amount: 69.32,
        suffix: "/day",
      },
      listPrice: {
        currency: "USD",
        amount: 71.14,
        suffix: "/day",
      },
      totalPrice: {
        currency: "USD",
        amount: 69.32,
        suffix: "/day",
      },
    },
    isNudge: false,
  },
  {
    id: "1001013",
    name: "Cover The Car & Liability",
    deductibleAmount: {
      currency: "USD",
      value: 0,
    },
    ratingStars: 2,
    isPreviouslySelected: false,
    isSelected: false,
    isDeductibleAvailable: true,
    includes: [
      {
        id: "LD",
        title:
          "LDW - Loss Damage Waiver for collision damages, scratches, bumps and theft.",
        description:
          "Enjoy the peace of mind of knowing you're protected from high costs in case your vehicle is stolen or damaged.",
        tags: [],
      },
      {
        id: "S3",
        title: "Supplemental Liability Insurance",
        description:
          "With liability insurance, you are protected against claims from third parties up to a limit of USD 300,000 per accident.",
        tags: [],
      },
    ],
    excludes: [
      {
        id: "IP",
        title: "Personal Property Coverage",
        description:
          "Safeguard your personal items and those of your accompanying family members from damage or loss.",
        tags: [],
      },
      {
        id: "I",
        title: "Personal Accident Coverage",
        description:
          "Both the driver and passengers of the rental vehicle are entitled to financial compensation for accident-related medical costs.",
        tags: [],
      },
      {
        id: "BC",
        title: "Extended Roadside Protection",
        description:
          "In the case of self-caused errors that prevent further travel, SIXT will assist you getting on the road again (flat tire, empty tank or battery, lost or locked-in key).",
        tags: [],
      },
    ],
    price: {
      discountPercentage: 3,
      displayPrice: {
        currency: "USD",
        amount: 48.03,
        suffix: "/day",
      },
      listPrice: {
        currency: "USD",
        amount: 49.85,
        suffix: "/day",
      },
      totalPrice: {
        currency: "USD",
        amount: 48.03,
        suffix: "/day",
      },
    },
    isNudge: false,
  },
  {
    id: "1000629",
    name: "Cover The Car",
    deductibleAmount: {
      currency: "USD",
      value: 0,
    },
    ratingStars: 1,
    isPreviouslySelected: false,
    isSelected: false,
    isDeductibleAvailable: true,
    includes: [
      {
        id: "LD",
        title:
          "LDW - Loss Damage Waiver for collision damages, scratches, bumps and theft.",
        description:
          "Enjoy the peace of mind of knowing you're protected from high costs in case your vehicle is stolen or damaged.",
        tags: [],
      },
    ],
    excludes: [
      {
        id: "S3",
        title: "Supplemental Liability Insurance",
        description:
          "With liability insurance, you are protected against claims from third parties up to a limit of USD 300,000 per accident.",
        tags: [],
      },
      {
        id: "IP",
        title: "Personal Property Coverage",
        description:
          "Safeguard your personal items and those of your accompanying family members from damage or loss.",
        tags: [],
      },
      {
        id: "I",
        title: "Personal Accident Coverage",
        description:
          "Both the driver and passengers of the rental vehicle are entitled to financial compensation for accident-related medical costs.",
        tags: [],
      },
      {
        id: "BC",
        title: "Extended Roadside Protection",
        description:
          "In the case of self-caused errors that prevent further travel, SIXT will assist you getting on the road again (flat tire, empty tank or battery, lost or locked-in key).",
        tags: [],
      },
    ],
    price: {
      discountPercentage: 5,
      displayPrice: {
        currency: "USD",
        amount: 31.85,
        suffix: "/day",
      },
      listPrice: {
        currency: "USD",
        amount: 33.67,
        suffix: "/day",
      },
      totalPrice: {
        currency: "USD",
        amount: 31.85,
        suffix: "/day",
      },
    },
    isNudge: false,
  },
  {
    id: "1",
    name: "I don’t need protection",
    description:
      "I have coverage through personal insurance, my credit card, external protection purchased while booking, or do not need any protection . I understand I'm still responsible to SIXT for any damage, theft, or third-party claims.",
    deductibleAmount: {
      currency: "USD",
      value: 0,
    },
    ratingStars: 0,
    isPreviouslySelected: true,
    isSelected: true,
    isDeductibleAvailable: false,
    includes: [],
    excludes: [],
    price: {
      discountPercentage: 0,
      displayPrice: {
        currency: "USD",
        amount: 0,
        suffix: "/day",
      },
      totalPrice: {
        currency: "USD",
        amount: 0,
        suffix: "/day",
      },
    },
    isNudge: false,
  },
];

const sampleAddOns = [
  {
    id: 0,
    name: "",
    options: [
      {
        chargeDetail: {
          id: "T4",
          title: "General Toll Service",
          description: "Pay only incurred tolls plus a discounted service fee",
          iconUrl: "https://www.sixt.com/shared/icons/rent/circle_plus.png",
          tags: [],
        },
        additionalInfo: {
          price: {
            discountPercentage: 0,
            displayPrice: {
              currency: "USD",
              amount: 5.99,
              suffix: "/day",
            },
          },
          isPreviouslySelected: false,
          isSelected: false,
          isEnabled: true,
          selectionStrategy: {
            isMultiSelectionAllowed: false,
            maxSelectionLimit: 1,
            currentSelection: 0,
          },
          isNudge: false,
        },
      },
      {
        chargeDetail: {
          id: "AD",
          title: "Additional driver",
          description:
            "Share the driving for a safer and more relaxed trip. Each extra driver is charged per day and must show a valid license when picking up the vehicle.",
          iconUrl: "https://www.sixt.com/shared/icons/rent/foreign-use.png",
          tags: ["AD_FORM_ENABLED"],
        },
        additionalInfo: {
          price: {
            discountPercentage: 0,
            displayPrice: {
              currency: "USD",
              amount: 14.99,
              suffix: "/day & driver",
            },
          },
          isPreviouslySelected: false,
          isSelected: false,
          isEnabled: true,
          selectionStrategy: {
            isMultiSelectionAllowed: true,
            maxSelectionLimit: 8,
            currentSelection: 0,
          },
          isNudge: false,
        },
      },
    ],
  },
  {
    id: 1,
    name: "Child seats",
    options: [
      {
        chargeDetail: {
          id: "BS",
          title: "Infant seat",
          description:
            "For babies up to 15 months old with a height up to 32 inches (81 cm). The seat can only be used rear-facing.",
          iconUrl:
            "https://www.sixt.com/shared/icons/rent/extras/2x/ico_childseat.png",
          tags: [],
        },
        additionalInfo: {
          price: {
            discountPercentage: 0,
            displayPrice: {
              currency: "USD",
              amount: 13.99,
              suffix: "/day",
            },
          },
          isPreviouslySelected: false,
          isSelected: false,
          isEnabled: true,
          selectionStrategy: {
            isMultiSelectionAllowed: true,
            maxSelectionLimit: 3,
            currentSelection: 0,
          },
          isNudge: false,
        },
      },
      {
        chargeDetail: {
          id: "CS",
          title: "Toddler seat",
          description:
            "For children aged between 6 months and 4 years with a height up to 49 inches (124 cm).",
          iconUrl:
            "https://www.sixt.com/shared/icons/rent/extras/2x/ico_childseat.png",
          tags: [],
        },
        additionalInfo: {
          price: {
            discountPercentage: 0,
            displayPrice: {
              currency: "USD",
              amount: 13.99,
              suffix: "/day",
            },
          },
          isPreviouslySelected: false,
          isSelected: false,
          isEnabled: true,
          selectionStrategy: {
            isMultiSelectionAllowed: true,
            maxSelectionLimit: 3,
            currentSelection: 0,
          },
          isNudge: false,
        },
      },
      {
        chargeDetail: {
          id: "BO",
          title: "Booster seat",
          description:
            "For children aged between 4 and 12 years with a height of 43 and 57 inches (110 cm to 145 cm).",
          iconUrl:
            "https://www.sixt.com/shared/icons/rent/extras/2x/ico_childseat.png",
          tags: [],
        },
        additionalInfo: {
          price: {
            discountPercentage: 0,
            displayPrice: {
              currency: "USD",
              amount: 13.99,
              suffix: "/day",
            },
          },
          isPreviouslySelected: false,
          isSelected: false,
          isEnabled: true,
          selectionStrategy: {
            isMultiSelectionAllowed: true,
            maxSelectionLimit: 3,
            currentSelection: 0,
          },
          isNudge: false,
        },
      },
    ],
  },
];

export default function HomePage() {
  const steps = [
    {
      id: "car-selection",
      content: <CarSelection cars={[sampleCar, sampleCar, sampleCar]} />,
    },
    {
      id: "insurance-selection",
      content: (
        <div className="w-full flex flex-col gap-3 overflow-y-auto pr-1">
          <InsuranceSelection protections={sampleProtections} />
        </div>
      ),
    },
    {
      id: "addon-selection",
      content: <AddOnSelection addOns={sampleAddOns} />,
    },
  ];

  const [stepIndex, setStepIndex] = useState(0);

  const goPrev = () => setStepIndex((i) => Math.max(0, i - 1));
  const goNext = () => setStepIndex((i) => Math.min(steps.length - 1, i + 1));

  return (
    <div className="flex min-h-screen w-full">
      {/* Left side - Chatbot */}
      <div className="w-1/2 border-r p-6 flex items-center justify-center bg-gray-50">
        <Chatbot />
      </div>

      {/* Right side - Configuration */}
      <div className="w-1/2 p-6 flex flex-col gap-4 bg-white">
        <div className="flex-1 flex items-center justify-center">
          {steps[stepIndex].content}
        </div>
        <div className="flex justify-between">
          <Button variant="outline" onClick={goPrev} disabled={stepIndex === 0}>
            Previous
          </Button>
          <Button onClick={goNext} disabled={stepIndex === steps.length - 1}>
            Next
          </Button>
        </div>
      </div>
    </div>
  );
}

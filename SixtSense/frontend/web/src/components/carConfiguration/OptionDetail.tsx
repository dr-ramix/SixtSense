import { AddOnOption } from "@/domain/AddOn";
import { Card } from "../ui/card";
import BackgroundGradient from "../ui/background-gradient";

type OptionDetailProps = {
  option: AddOnOption;
  selected?: boolean;
  onToggle?: (option: AddOnOption) => void;
};

export default function OptionDetail({
  option,
  selected,
  onToggle,
}: OptionDetailProps) {
  return (
    <Card
      className={`relative overflow-hidden p-3 w-full flex-shrink-0 border cursor-pointer transition ${
        selected
          ? "border-transparent bg-primary/5"
          : "border-transparent hover:border-primary/40 hover:ring-1 hover:ring-primary/20"
      }`}
      onClick={() => onToggle?.(option)}
      role="button"
      tabIndex={0}
    >
      {selected && <BackgroundGradient />}
      <div className="relative z-10 flex justify-between items-start w-full">
        <div className="font-medium">{option.chargeDetail.title}</div>

        <div className="text-sm opacity-80 whitespace-nowrap">
          {option.additionalInfo.price.displayPrice.currency}{" "}
          {option.additionalInfo.price.displayPrice.amount}
          {option.additionalInfo.price.displayPrice.suffix}
        </div>
      </div>

      <div className="relative z-10 mt-2 text-left">
        {option.chargeDetail.description}
      </div>
    </Card>
  );
}

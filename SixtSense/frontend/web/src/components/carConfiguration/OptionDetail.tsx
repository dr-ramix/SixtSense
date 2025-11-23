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
      className={`relative overflow-hidden p-4 w-full flex-shrink-0 border cursor-pointer transition ${
        selected
          ? "border-border/70 bg-primary/5"
          : "border-border/70 hover:border-primary/60 hover:ring-1 hover:ring-primary/20"
      }`}
      onClick={() => onToggle?.(option)}
      role="button"
      tabIndex={0}
    >
      {selected && <BackgroundGradient />}
      <div className="relative z-10 flex justify-between items-start w-full">
        <div className="font-medium">{option.chargeDetail.title}</div>

        <div className="text-sm font-bold justify-self-end pr-8">
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

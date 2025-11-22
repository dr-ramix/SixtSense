import { AddOn } from "@/domain/AddOn";
import OptionDetail from "./OptionDetail";

type AddOnSelectionProps = {
  addOns: AddOn[];
};

export default function AddOnSelection({ addOns }: AddOnSelectionProps) {
  return (
    <div className="w-full flex flex-col gap-3">
      {addOns.map((addOn) => (
        <div className="text-sm align-top justify-start w-full">
          {/* Row 1 */}
          <div className="font-semibold justify-self-start">{addOn.name}</div>

          {/* Row 2 */}
          <div className="flex flex-col gap-4 text-sm align-top justify-start w-full pt-3">
            {addOn.options.map((option) => (
              <OptionDetail option={option} />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

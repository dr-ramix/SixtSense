import { AddOn, AddOnOption } from "@/domain/AddOn";
import OptionDetail from "./OptionDetail";

type AddOnSelectionProps = {
  addOns: AddOn[];
  selectedOptions: AddOnOption[];
  onToggle: (option: AddOnOption) => void;
};

export default function AddOnSelection({
  addOns,
  selectedOptions,
  onToggle,
}: AddOnSelectionProps) {
  return (
    <div className="w-full flex flex-col gap-3">
      {addOns.map((addOn) => (
        <div key={addOn.id} className="text-sm align-top justify-start w-full">
          {/* Row 1 */}
          <div className="font-semibold justify-self-start">{addOn.name}</div>

          {/* Row 2 */}
          <div className="flex flex-col gap-4 text-sm align-top justify-start w-full pt-3">
            {addOn.options.map((option) => (
              <OptionDetail
                key={option.chargeDetail.id}
                option={option}
                selected={selectedOptions.some(
                  (o) => o.chargeDetail.id === option.chargeDetail.id
                )}
                onToggle={onToggle}
              />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

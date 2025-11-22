import { Protection } from "@/domain/Protection";
import { Star } from "lucide-react";
import CoverageItemDetails from "./CoverageItemComponent";
import { Card } from "../ui/card";

type IncuranceSelectionProps = {
  protections: Protection[];
  selectedProtection?: Protection | null;
  onSelect: (protection: Protection) => void;
};

export default function InsuranceSelection({
  protections,
  selectedProtection,
  onSelect,
}: IncuranceSelectionProps) {
  return (
    <div className="w-full flex flex-col gap-3">
      {protections.map((protection) => {
        const isSelected = selectedProtection?.id === protection.id;
        return (
          <Card
            key={protection.id}
            className={`w-full m-0 p-3 h-40 flex flex-1 flex-row items-center justify-start rounded-2xl shadow-md overflow-hidden border transition cursor-pointer ${
              isSelected
                ? "border-primary ring-2 ring-primary/60 bg-primary/5"
                : "border-transparent hover:border-primary/40 hover:ring-1 hover:ring-primary/20"
            }`}
            onClick={() => onSelect(protection)}
            role="button"
            tabIndex={0}
          >
            <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-sm align-top justify-start w-full">
              {/* Row 1 */}
              <div className="font-semibold justify-self-start">
                {protection.name}
              </div>
              <div className="font-large font-bold justify-self-end pr-4 flex items-center gap-1">
                {[...Array(protection.ratingStars)].map((_, i) => (
                  <Star key={i} className="inline-block w-4 h-4 opacity-70" />
                ))}
              </div>

              {/* Row 2 */}
              <div className="justify-self-start">
                {protection.includes.length !== 0 && <div>Includes:</div>}
                {protection.includes.map((include) => (
                  <CoverageItemDetails key={include.id} item={include} />
                ))}
              </div>

              <div className="justify-self-start">
                {protection.excludes.length !== 0 && <div>Excludes:</div>}
                {protection.excludes.map((exclude) => (
                  <CoverageItemDetails key={exclude.id} item={exclude} />
                ))}
              </div>

              {/* Row 3 */}
              <div className="font-large font-bold justify-self-end col-span-2 pr-4">
                {protection.price.totalPrice.currency}{" "}
                {protection.price.totalPrice.amount}
                {protection.price.totalPrice.suffix}
              </div>
            </div>
          </Card>
        );
      })}
    </div>
  );
}
